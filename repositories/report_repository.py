"""Truy vấn SQL thống kê doanh số.

Người phụ trách: THÀNH VIÊN C.
Đọc bảng orders của module B: created_at, user_id, total_amount, discount_amount, final_amount.
start/end là kiểu datetime.date và TÍNH CẢ NGÀY end (dùng utils.dates.day_bounds).
Gợi ý: Database.day_expr("created_at") / month_expr("created_at") lo sẵn khác biệt SQL Server/SQLite.
"""
from utils.dates import day_bounds  # noqa: F401  (C dùng khi code)


class ReportRepository:
    def __init__(self, db):
        self._db = db

    def summary(self, start, end, user_id=None):
        """TODO (C): dict {order_count, gross, discount, net} trong khoảng; user_id=None là toàn cửa hàng.
        Dùng COALESCE(SUM(...), 0) để khoảng không có đơn trả về 0 thay vì NULL."""
        raise NotImplementedError("TODO (C): ReportRepository.summary")

    def by_period(self, start, end, granularity, user_id=None):
        """TODO (C): list[dict {bucket, order_count, gross, discount, net}] gom theo ngày ('day') hoặc tháng ('month').
        bucket là 'YYYY-MM-DD' hoặc 'YYYY-MM'. Chỉ trả các kỳ có đơn (ReportService sẽ điền 0 cho kỳ trống)."""
        raise NotImplementedError("TODO (C): ReportRepository.by_period")

    def by_staff(self, start, end):
        """TODO (C): list[dict {user_id, full_name, username, role, active, order_count, gross, discount, net}]
        của MỌI tài khoản (LEFT JOIN để người chưa bán gì vẫn hiện số 0), xếp theo net giảm dần."""
        raise NotImplementedError("TODO (C): ReportRepository.by_staff")
