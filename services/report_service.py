"""Thống kê doanh số. Chủ cửa hàng xem được tất cả; nhân viên chỉ xem doanh số của chính mình.
Kiểu trả về nằm sẵn ở models/report.py: SalesSummary, PeriodSales, StaffSales.
"""
from datetime import date

from models.report import PeriodSales, SalesSummary, StaffSales
from utils.dates import add_months, first_of_month
from utils.exceptions import PermissionDenied, ValidationError

MAX_DAYS = 366
GRANULARITIES = ("day", "month")


class ReportService:
    def __init__(self, repo, auth):
        self._repo = repo
        self._auth = auth

    # ---------------------------------------------------------------- công khai
    def summary(self, start, end, user_id=None):
        """SalesSummary của khoảng [start, end] (gồm cả ngày end). user_id=None là toàn cửa hàng (chỉ chủ)."""
        self._check_access(user_id)
        self._check_range(start, end)
        return SalesSummary(**self._repo.summary(start, end, user_id))

    def my_summary(self, start, end):
        """summary của người đang đăng nhập."""
        return self.summary(start, end, self._auth.require_login().id)

    def series(self, start, end, granularity, user_id=None):
        """list[PeriodSales] theo từng ngày ('day') hoặc tháng ('month') trong khoảng, kỳ không có đơn điền 0.

        Theo tháng: mỗi tháng chỉ tính các đơn nằm TRONG khoảng đã chọn, nên tổng các kỳ luôn bằng summary().
        """
        self._check_access(user_id)
        self._check_range(start, end)
        if granularity not in GRANULARITIES:
            raise ValidationError("Chỉ xem được theo ngày hoặc theo tháng")
        if granularity == "day" and (end - start).days + 1 > MAX_DAYS:
            raise ValidationError(f"Xem theo ngày tối đa {MAX_DAYS} ngày, hãy chọn khoảng ngắn hơn hoặc xem theo tháng")
        found = {r["bucket"]: r for r in self._repo.by_period(start, end, granularity, user_id)}
        result = []
        for period, label in self._periods(start, end, granularity):
            row = found.get(period, {})
            result.append(PeriodSales(period, label, row.get("order_count", 0), row.get("gross", 0),
                                      row.get("discount", 0), row.get("net", 0)))
        return result

    def by_staff(self, start, end):
        """Chỉ chủ cửa hàng. list[StaffSales] xếp theo doanh thu giảm dần, gồm cả người chưa bán gì."""
        self._auth.require_owner()
        self._check_range(start, end)
        return [StaffSales(**row) for row in self._repo.by_staff(start, end)]

    @staticmethod
    def today():
        """Gợi ý ngày cho UI (đã làm sẵn)."""
        return date.today()

    # ---------------------------------------------------------------- nội bộ
    def _check_access(self, user_id):
        """Chủ xem được mọi thứ; nhân viên chỉ được xem số của chính mình (user_id phải là id của họ)."""
        me = self._auth.require_login()
        if not me.is_owner and user_id != me.id:
            raise PermissionDenied("Bạn chỉ được xem doanh số của chính mình")

    @staticmethod
    def _check_range(start, end):
        if start > end:
            raise ValidationError("Ngày bắt đầu phải trước hoặc bằng ngày kết thúc")

    @staticmethod
    def _periods(start, end, granularity):
        """Liệt kê (mã kỳ, nhãn hiển thị) từ start đến end, theo đúng thứ tự thời gian."""
        if granularity == "day":
            from datetime import timedelta
            for i in range((end - start).days + 1):
                d = start + timedelta(days=i)
                yield d.isoformat(), d.strftime("%d/%m")
        else:
            month, last = first_of_month(start), first_of_month(end)
            while month <= last:
                yield month.strftime("%Y-%m"), month.strftime("%m/%Y")
                month = add_months(month, 1)