"""Tiện ích ngày giờ."""
from datetime import date, datetime, timedelta

DT_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE = "%d/%m/%Y"
DISPLAY_DATETIME = "%d/%m/%Y %H:%M:%S"


def to_datetime(value):
    """Chuẩn hóa giá trị đọc từ DB (SQL Server trả datetime, SQLite trả chuỗi)."""
    if value is None or isinstance(value, datetime):
        return value
    return datetime.strptime(str(value)[:19], DT_FORMAT)


def db_datetime(value):
    """datetime -> chuỗi ISO để truyền làm tham số SQL (chạy được trên cả SQL Server lẫn SQLite)."""
    return value.strftime(DT_FORMAT)


def parse_date(text):
    """'09/10/2026' -> date. Ném ValueError với thông báo tiếng Việt."""
    try:
        return datetime.strptime((text or "").strip(), DISPLAY_DATE).date()
    except ValueError:
        raise ValueError(f"Ngày '{text}' không hợp lệ, hãy nhập theo dạng dd/mm/yyyy (ví dụ 09/10/2026)") from None


def format_date(d):
    return d.strftime(DISPLAY_DATE)


def day_bounds(start, end):
    """[start 00:00, end+1 00:00) dưới dạng 2 chuỗi tham số SQL."""
    lo = datetime.combine(start, datetime.min.time())
    hi = datetime.combine(end + timedelta(days=1), datetime.min.time())
    return db_datetime(lo), db_datetime(hi)


def first_of_month(d):
    return d.replace(day=1)


def add_months(d, months):
    """Cộng/trừ tháng, trả về ngày đầu tháng."""
    index = d.year * 12 + (d.month - 1) + months
    return date(index // 12, index % 12 + 1, 1)


def month_start_end(d):
    first = first_of_month(d)
    return first, add_months(first, 1) - timedelta(days=1)
