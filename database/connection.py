"""Lớp truy cập CSDL.

- SQL Server (qua pyodbc) là CSDL chính.
- SQLite chỉ dùng để dev nhanh / chạy test khi không có SQL Server.

Mọi repository chỉ làm việc với `Database`, mọi khác biệt giữa hai hệ CSDL (trả id sau INSERT,
gom nhóm theo ngày, tìm kiếm không dấu, giới hạn dòng...) được gom ở đây.
"""
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import config
from utils.exceptions import DatabaseConnectionError
from utils.text import like_escape, normalize

SCHEMA_DIR = Path(__file__).resolve().parent
_DRIVER_PREFERENCE = (
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
    "ODBC Driver 13 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server",
)


class Database:
    def __init__(self, conn, dialect):
        self._conn = conn
        self.dialect = dialect  # "sqlserver" | "sqlite"
        self._depth = 0         # độ sâu của transaction() đang mở

    @property
    def is_sqlserver(self):
        return self.dialect == "sqlserver"

    # ------------------------------------------------------------ truy vấn
    def _run(self, cur, sql, params):
        if params:
            cur.execute(sql, tuple(params))
        else:
            cur.execute(sql)

    def query(self, sql, params=()):
        """SELECT -> list[dict]."""
        cur = self._conn.cursor()
        try:
            self._run(cur, sql, params)
            columns = [c[0] for c in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        finally:
            cur.close()

    def query_one(self, sql, params=()):
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def scalar(self, sql, params=(), default=None):
        row = self.query_one(sql, params)
        if not row:
            return default
        value = next(iter(row.values()))
        return default if value is None else value

    def execute(self, sql, params=()):
        """INSERT/UPDATE/DELETE -> số dòng bị ảnh hưởng. Tự commit nếu không nằm trong transaction()."""
        cur = self._conn.cursor()
        try:
            self._run(cur, sql, params)
            count = cur.rowcount
        except Exception:
            if self._depth == 0:
                self._conn.rollback()
            raise
        finally:
            cur.close()
        if self._depth == 0:
            self._conn.commit()
        return count

    def insert(self, table, values):
        """INSERT một dòng, trả về id (khóa chính tên `id`) vừa tạo."""
        columns = list(values)
        col_sql = ", ".join(columns)
        marks = ", ".join("?" for _ in columns)
        if self.is_sqlserver:
            sql = f"INSERT INTO {table} ({col_sql}) OUTPUT INSERTED.id VALUES ({marks})"
        else:
            sql = f"INSERT INTO {table} ({col_sql}) VALUES ({marks}) RETURNING id"
        cur = self._conn.cursor()
        try:
            cur.execute(sql, tuple(values[c] for c in columns))
            new_id = int(cur.fetchone()[0])
        except Exception:
            if self._depth == 0:
                self._conn.rollback()
            raise
        finally:
            cur.close()
        if self._depth == 0:
            self._conn.commit()
        return new_id

    @contextmanager
    def transaction(self):
        """Gom nhiều thao tác vào một transaction: lỗi bất kỳ -> rollback tất cả."""
        self._depth += 1
        try:
            yield self
        except BaseException:
            self._depth -= 1
            if self._depth == 0:
                self._conn.rollback()
            raise
        else:
            self._depth -= 1
            if self._depth == 0:
                self._conn.commit()

    def close(self):
        self._conn.close()

    # --------------------------------------------- khác biệt giữa các hệ CSDL
    def day_expr(self, column):
        """Biểu thức SQL trả 'YYYY-MM-DD' của một cột ngày giờ."""
        if self.is_sqlserver:
            return f"CONVERT(VARCHAR(10), {column}, 23)"
        return f"strftime('%Y-%m-%d', {column})"

    def month_expr(self, column):
        """Biểu thức SQL trả 'YYYY-MM'."""
        if self.is_sqlserver:
            return f"CONVERT(VARCHAR(7), {column}, 23)"
        return f"strftime('%Y-%m', {column})"

    def like_no_accent(self, column):
        """Điều kiện LIKE không phân biệt dấu/hoa thường (kèm 1 tham số, tạo bằng like_param)."""
        if self.is_sqlserver:
            # Collation *_AI bỏ dấu tiếng Việt, riêng đ/Đ là chữ cái riêng nên phải REPLACE.
            return (f"REPLACE(REPLACE({column}, N'đ', N'd'), N'Đ', N'D') "
                    f"COLLATE Latin1_General_100_CI_AI LIKE ? ESCAPE '\\'")
        return f"norm({column}) LIKE ? ESCAPE '\\'"

    @staticmethod
    def like_param(keyword):
        return f"%{like_escape(normalize(keyword))}%"

    def top(self, n):
        """Chèn ngay sau SELECT."""
        return f"TOP {int(n)} " if self.is_sqlserver else ""

    def limit(self, n):
        """Chèn cuối câu SELECT."""
        return "" if self.is_sqlserver else f" LIMIT {int(n)}"

    # ----------------------------------------------------------- schema
    def table_exists(self, name):
        if self.is_sqlserver:
            return self.scalar("SELECT OBJECT_ID(?, N'U')", (f"dbo.{name}",)) is not None
        return self.scalar("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (name,)) is not None

    def run_script(self, script):
        """Chạy file schema (SQL Server: tách theo dòng GO)."""
        if self.is_sqlserver:
            batches = re.split(r"^\s*GO\s*$", script, flags=re.IGNORECASE | re.MULTILINE)
            with self.transaction():
                for batch in batches:
                    if batch.strip():
                        self.execute(batch)
        else:
            self._conn.executescript(script)


# ================================================================ kết nối
def connect(engine=None):
    engine = (engine or config.DB_ENGINE).lower()
    if engine == "sqlite":
        return connect_sqlite(config.SQLITE_PATH)
    if engine == "sqlserver":
        return connect_sqlserver()
    raise DatabaseConnectionError(f"CINEMA_DB_ENGINE không hợp lệ: '{engine}' (dùng 'sqlserver' hoặc 'sqlite')")


def connect_sqlite(path):
    """path = ':memory:' để dùng DB tạm khi test."""
    path = str(path)
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.create_function("norm", 1, normalize, deterministic=True)
    return Database(conn, "sqlite")


def _pick_driver(pyodbc):
    if config.DB_DRIVER:
        return config.DB_DRIVER
    installed = pyodbc.drivers()
    for name in _DRIVER_PREFERENCE:
        if name in installed:
            return name
    raise DatabaseConnectionError(
        "Máy chưa cài ODBC Driver cho SQL Server.\n"
        "Tải 'ODBC Driver 18 for SQL Server' của Microsoft rồi chạy lại ứng dụng.")


def connect_sqlserver():
    try:
        import pyodbc
    except ImportError:
        raise DatabaseConnectionError(
            "Chưa cài thư viện pyodbc.\nChạy lệnh:  pip install pyodbc") from None

    if not re.fullmatch(r"[A-Za-z0-9_]+", config.DB_NAME):
        raise DatabaseConnectionError("CINEMA_DB_NAME chỉ được gồm chữ, số và dấu gạch dưới.")

    driver = _pick_driver(pyodbc)
    def braced(value):  # giá trị có ; hoặc } phải đặt trong {...} (} viết đôi) theo quy tắc chuỗi ODBC
        return "{" + value.replace("}", "}}") + "}"

    auth = (f"UID={braced(config.DB_USER)};PWD={braced(config.DB_PASSWORD)};"
            if config.DB_USER else "Trusted_Connection=yes;")
    base = f"DRIVER={{{driver}}};SERVER={config.DB_SERVER};{auth}"
    if driver.startswith("ODBC Driver"):
        base += "TrustServerCertificate=yes;"  # chứng chỉ tự ký của SQL Server cài trên máy local

    try:
        # Tạo database nếu chưa có (CREATE DATABASE không chạy được trong transaction -> autocommit)
        master = pyodbc.connect(base + "DATABASE=master;", autocommit=True, timeout=8)
        try:
            exists = master.cursor().execute("SELECT DB_ID(?)", config.DB_NAME).fetchone()[0]
            if exists is None:
                master.execute(f"CREATE DATABASE [{config.DB_NAME}]")
        finally:
            master.close()
        conn = pyodbc.connect(base + f"DATABASE={config.DB_NAME};", timeout=8)
    except pyodbc.Error as exc:
        raise DatabaseConnectionError(
            f"Không kết nối được SQL Server '{config.DB_SERVER}'.\n\n"
            "Hãy kiểm tra:\n"
            "  1. Dịch vụ SQL Server (SQL Server Express) đang chạy.\n"
            f"  2. Tên server đúng (đang dùng: {config.DB_SERVER}) - sửa DB_SERVER trong config.py "
            "hoặc đặt biến môi trường CINEMA_DB_SERVER.\n"
            "  3. Nếu dùng tài khoản SQL (sa...), đặt CINEMA_DB_USER và CINEMA_DB_PASSWORD; "
            "để trống sẽ dùng Windows Authentication.\n"
            "  4. Tài khoản có quyền tạo database / tạo bảng.\n\n"
            f"Chi tiết: {exc}") from exc
    return Database(conn, "sqlserver")


# ============================================================== khởi tạo DB
def init_db(db):
    """Tạo bảng + dữ liệu mẫu ở lần chạy đầu; bổ sung tài khoản mặc định nếu chưa có user nào."""
    from database import seed

    if not db.table_exists("users"):
        filename = "schema_sqlserver.sql" if db.is_sqlserver else "schema_sqlite.sql"
        db.run_script((SCHEMA_DIR / filename).read_text(encoding="utf-8"))
        seed.seed_catalog(db)
    if db.scalar("SELECT COUNT(*) FROM users", default=0) == 0:
        seed.seed_users(db)
