"""Thống kê doanh số. Chủ cửa hàng xem được tất cả; nhân viên chỉ xem doanh số của chính mình.

Người phụ trách: THÀNH VIÊN C.
Kiểu trả về nằm sẵn ở models/report.py: SalesSummary, PeriodSales, StaffSales.
"""
from datetime import date

from models.report import PeriodSales, SalesSummary, StaffSales  # noqa: F401  (C dùng khi code)
from utils.dates import add_months, first_of_month  # noqa: F401
from utils.exceptions import PermissionDenied, ValidationError  # noqa: F401

MAX_DAYS = 366


class ReportService:
    def __init__(self, repo, auth):
        self._repo = repo
        self._auth = auth

    def summary(self, start, end, user_id=None):
        """TODO (C): trả về SalesSummary. Phân quyền: nhân viên chỉ được user_id == chính mình (PermissionDenied).
        start > end thì ValidationError."""
        raise NotImplementedError("TODO (C): ReportService.summary")

    def my_summary(self, start, end):
        """TODO (C): summary của người đang đăng nhập."""
        raise NotImplementedError("TODO (C): ReportService.my_summary")

    def series(self, start, end, granularity, user_id=None):
        """TODO (C): list[PeriodSales] theo từng ngày ('day') hoặc tháng ('month') trong khoảng, kỳ không có đơn
        điền 0. Xem theo ngày tối đa MAX_DAYS ngày (ValidationError nếu vượt)."""
        raise NotImplementedError("TODO (C): ReportService.series")

    def by_staff(self, start, end):
        """TODO (C): chỉ chủ cửa hàng; trả về list[StaffSales] xếp theo doanh thu giảm dần."""
        raise NotImplementedError("TODO (C): ReportService.by_staff")

    @staticmethod
    def today():
        """Gợi ý ngày cho UI (đã làm sẵn)."""
        return date.today()
