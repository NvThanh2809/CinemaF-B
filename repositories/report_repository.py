"""Truy vấn SQL thống kê doanh số.
Đọc bảng orders của module B: created_at, user_id, total_amount, discount_amount, final_amount.
start/end là kiểu datetime.date và TÍNH CẢ NGÀY end (dùng utils.dates.day_bounds).
Database.day_expr("created_at") / month_expr("created_at") lo sẵn khác biệt SQL Server/SQLite.
"""
from utils.dates import day_bounds

# Ba cột số liệu dùng chung cho mọi truy vấn (COALESCE để khoảng không có đơn ra 0 thay vì NULL)
_SUMS = ("COUNT(o.id) AS order_count, "
         "COALESCE(SUM(o.total_amount), 0) AS gross, "
         "COALESCE(SUM(o.discount_amount), 0) AS discount, "
         "COALESCE(SUM(o.final_amount), 0) AS net")


def _numbers(row):
    """Ép các cột số về int (SQL Server có thể trả Decimal/None tùy kiểu cột)."""
    return {k: int(row[k] or 0) for k in ("order_count", "gross", "discount", "net")}


class ReportRepository:
    def __init__(self, db):
        self._db = db

    def summary(self, start, end, user_id=None):
        """dict {order_count, gross, discount, net} trong khoảng; user_id=None là toàn cửa hàng."""
        lo, hi = day_bounds(start, end)
        sql = f"SELECT {_SUMS} FROM orders o WHERE o.created_at >= ? AND o.created_at < ?"
        params = [lo, hi]
        if user_id is not None:
            sql += " AND o.user_id = ?"
            params.append(user_id)
        return _numbers(self._db.query_one(sql, params))

    def by_period(self, start, end, granularity, user_id=None):
        """list[dict {bucket, order_count, gross, discount, net}] gom theo ngày ('day') hoặc tháng ('month').
        bucket là 'YYYY-MM-DD' hoặc 'YYYY-MM'. Chỉ trả các kỳ có đơn (ReportService điền 0 cho kỳ trống)."""
        if granularity == "day":
            bucket = self._db.day_expr("o.created_at")
        elif granularity == "month":
            bucket = self._db.month_expr("o.created_at")
        else:
            raise ValueError(f"granularity không hợp lệ: {granularity!r}")
        lo, hi = day_bounds(start, end)
        sql = (f"SELECT {bucket} AS bucket, {_SUMS} FROM orders o "
               "WHERE o.created_at >= ? AND o.created_at < ?")
        params = [lo, hi]
        if user_id is not None:
            sql += " AND o.user_id = ?"
            params.append(user_id)
        sql += f" GROUP BY {bucket} ORDER BY bucket"
        return [{"bucket": r["bucket"], **_numbers(r)} for r in self._db.query(sql, params)]

    def by_staff(self, start, end):
        """list[dict {user_id, full_name, username, role, active, order_count, gross, discount, net}]
        của MỌI tài khoản (LEFT JOIN để người chưa bán gì vẫn hiện số 0), xếp theo net giảm dần."""
        lo, hi = day_bounds(start, end)
        # Điều kiện thời gian đặt trong ON (không phải WHERE) để LEFT JOIN không làm mất người chưa bán gì.
        rows = self._db.query(
            f"SELECT u.id AS user_id, u.full_name, u.username, u.role, u.active, {_SUMS} "
            "FROM users u LEFT JOIN orders o "
            "ON o.user_id = u.id AND o.created_at >= ? AND o.created_at < ? "
            "GROUP BY u.id, u.full_name, u.username, u.role, u.active "
            "ORDER BY net DESC, u.full_name", [lo, hi])
        return [{"user_id": r["user_id"], "full_name": r["full_name"], "username": r["username"],
                 "role": r["role"], "active": bool(r["active"]), **_numbers(r)} for r in rows]