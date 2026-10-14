"""Test cho ReportService + ReportRepository (doanh số theo ngày, tháng, từng nhân viên).

Người phụ trách: THÀNH VIÊN C.
Chèn sẵn vài đơn với ngày giờ cố định (db.insert vào orders) rồi kiểm tra số liệu; nhớ thử cả đơn lúc 00:00:00 và 23:59:59.

Cách làm: mỗi test bên dưới là MỘT hành vi cần kiểm tra. Viết xong test nào thì xóa dòng @TODO của test đó
và thay phần mô tả bằng code kiểm tra thật. Chạy: python -m unittest discover -s tests -t .
"""
import unittest

from tests.helpers import Env

TODO = unittest.skip("TODO (C): chưa viết test này")


class ReportServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    @TODO
    def test_summary_whole_shop(self):
        """Tổng hợp toàn cửa hàng: số đơn, tiền hàng, giảm giá, thực thu đúng."""

    @TODO
    def test_range_is_inclusive_and_midnight_boundaries_are_exact(self):
        """Khoảng ngày gồm cả ngày cuối; đơn lúc 00:00:00 và 23:59:59 xếp đúng ngày."""

    @TODO
    def test_summary_per_staff(self):
        """Lọc theo user_id chỉ tính đơn của người đó."""

    @TODO
    def test_empty_range_returns_zeros(self):
        """Khoảng không có đơn trả về 0 (không phải None)."""

    @TODO
    def test_series_by_day_fills_missing_days(self):
        """Theo ngày: ngày không có đơn vẫn xuất hiện với 0."""

    @TODO
    def test_series_by_day_for_one_staff(self):
        """Theo ngày cho một nhân viên."""

    @TODO
    def test_series_by_month(self):
        """Theo tháng: gom đúng các đơn trong cùng tháng."""

    @TODO
    def test_series_by_month_crosses_year_boundary(self):
        """Khoảng 12/2026 đến 01/2027 cho 2 tháng đúng thứ tự."""

    @TODO
    def test_by_staff_ranking_includes_staff_without_sales(self):
        """Xếp hạng nhân viên theo thực thu giảm dần, người chưa bán vẫn hiện với 0."""

    @TODO
    def test_validation(self):
        """start > end và xem theo ngày quá 366 ngày bị ValidationError."""

    @TODO
    def test_staff_can_only_see_own_numbers(self):
        """Nhân viên xem số của người khác hoặc gọi by_staff bị PermissionDenied; my_summary luôn đúng của chính mình."""


if __name__ == "__main__":
    unittest.main()
