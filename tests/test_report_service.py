"""Test cho ReportService + ReportRepository (doanh số theo ngày, tháng, từng nhân viên).

Người phụ trách: THÀNH VIÊN C.
Chèn sẵn vài đơn với ngày giờ cố định (db.insert vào orders) rồi kiểm tra số liệu; nhớ thử cả đơn lúc 00:00:00 và 23:59:59.
"""
from datetime import date, timedelta
import unittest

from tests.helpers import Env
from utils.exceptions import PermissionDenied, ValidationError


class ReportServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    def _insert_order(self, created_at, user_id=None, total=100000, discount=10000, final=90000):
        if user_id is None:
            user_id = self.env.auth.current_user.id
        return self.env.db.insert("orders", {
            "created_at": created_at,
            "user_id": user_id,
            "total_amount": total,
            "discount_amount": discount,
            "final_amount": final,
        })

    def test_summary_whole_shop(self):
        """Tổng hợp toàn cửa hàng: số đơn, tiền hàng, giảm giá, thực thu đúng."""
        self._insert_order("2026-10-10 10:00:00", total=100000, discount=10000, final=90000)
        self._insert_order("2026-10-10 12:00:00", total=50000, discount=0, final=50000)
        s = self.env.reports.summary(date(2026, 10, 10), date(2026, 10, 10))
        self.assertEqual(s.order_count, 2)
        self.assertEqual(s.gross, 150000)
        self.assertEqual(s.discount, 10000)
        self.assertEqual(s.net, 140000)

    def test_range_is_inclusive_and_midnight_boundaries_are_exact(self):
        """Khoảng ngày gồm cả ngày cuối; đơn lúc 00:00:00 và 23:59:59 xếp đúng ngày."""
        self._insert_order("2026-10-10 00:00:00", total=10000, discount=0, final=10000)
        self._insert_order("2026-10-10 23:59:59", total=20000, discount=0, final=20000)
        self._insert_order("2026-10-11 00:00:00", total=30000, discount=0, final=30000)

        s = self.env.reports.summary(date(2026, 10, 10), date(2026, 10, 10))
        self.assertEqual(s.order_count, 2)
        self.assertEqual(s.net, 30000)

        s2 = self.env.reports.summary(date(2026, 10, 10), date(2026, 10, 11))
        self.assertEqual(s2.order_count, 3)
        self.assertEqual(s2.net, 60000)

    def test_summary_per_staff(self):
        """Lọc theo user_id chỉ tính đơn của người đó."""
        staff = self.env.user_repo.find_by_username("nhanvien")
        admin = self.env.user_repo.find_by_username("admin")
        self._insert_order("2026-10-10 10:00:00", user_id=admin.id, total=100000, discount=0, final=100000)
        self._insert_order("2026-10-10 11:00:00", user_id=staff.id, total=50000, discount=0, final=50000)

        s_staff = self.env.reports.summary(date(2026, 10, 10), date(2026, 10, 10), user_id=staff.id)
        self.assertEqual(s_staff.order_count, 1)
        self.assertEqual(s_staff.net, 50000)

        s_admin = self.env.reports.summary(date(2026, 10, 10), date(2026, 10, 10), user_id=admin.id)
        self.assertEqual(s_admin.order_count, 1)
        self.assertEqual(s_admin.net, 100000)

    def test_empty_range_returns_zeros(self):
        """Khoảng không có đơn trả về 0 (không phải None)."""
        s = self.env.reports.summary(date(2026, 1, 1), date(2026, 1, 2))
        self.assertEqual((s.order_count, s.gross, s.discount, s.net), (0, 0, 0, 0))

    def test_series_by_day_fills_missing_days(self):
        """Theo ngày: ngày không có đơn vẫn xuất hiện với 0."""
        self._insert_order("2026-10-01 10:00:00", total=50000, discount=0, final=50000)
        self._insert_order("2026-10-03 10:00:00", total=70000, discount=0, final=70000)

        series = self.env.reports.series(date(2026, 10, 1), date(2026, 10, 3), "day")
        self.assertEqual(len(series), 3)
        self.assertEqual(series[0].period, "2026-10-01")
        self.assertEqual(series[0].net, 50000)
        self.assertEqual(series[1].period, "2026-10-02")
        self.assertEqual(series[1].net, 0)
        self.assertEqual(series[2].period, "2026-10-03")
        self.assertEqual(series[2].net, 70000)

    def test_series_by_day_for_one_staff(self):
        """Theo ngày cho một nhân viên."""
        staff = self.env.user_repo.find_by_username("nhanvien")
        admin = self.env.user_repo.find_by_username("admin")
        self._insert_order("2026-10-01 10:00:00", user_id=admin.id, total=100000, discount=0, final=100000)
        self._insert_order("2026-10-01 11:00:00", user_id=staff.id, total=50000, discount=0, final=50000)

        series = self.env.reports.series(date(2026, 10, 1), date(2026, 10, 1), "day", user_id=staff.id)
        self.assertEqual(len(series), 1)
        self.assertEqual(series[0].net, 50000)

    def test_series_by_month(self):
        """Theo tháng: gom đúng các đơn trong cùng tháng."""
        self._insert_order("2026-10-05 10:00:00", total=50000, discount=0, final=50000)
        self._insert_order("2026-10-20 10:00:00", total=30000, discount=0, final=30000)
        self._insert_order("2026-11-01 10:00:00", total=60000, discount=0, final=60000)

        series = self.env.reports.series(date(2026, 10, 1), date(2026, 11, 30), "month")
        self.assertEqual(len(series), 2)
        self.assertEqual(series[0].period, "2026-10")
        self.assertEqual(series[0].net, 80000)
        self.assertEqual(series[1].period, "2026-11")
        self.assertEqual(series[1].net, 60000)

    def test_series_by_month_crosses_year_boundary(self):
        """Khoảng 12/2026 đến 01/2027 cho 2 tháng đúng thứ tự."""
        series = self.env.reports.series(date(2026, 12, 1), date(2027, 1, 31), "month")
        self.assertEqual(len(series), 2)
        self.assertEqual(series[0].period, "2026-12")
        self.assertEqual(series[1].period, "2027-01")

    def test_by_staff_ranking_includes_staff_without_sales(self):
        """Xếp hạng nhân viên theo thực thu giảm dần, người chưa bán vẫn hiện với 0."""
        staff = self.env.user_repo.find_by_username("nhanvien")
        self._insert_order("2026-10-10 10:00:00", user_id=staff.id, total=80000, discount=0, final=80000)

        ranking = self.env.reports.by_staff(date(2026, 10, 1), date(2026, 10, 31))
        self.assertEqual(len(ranking), 2)
        self.assertEqual(ranking[0].user_id, staff.id)
        self.assertEqual(ranking[0].net, 80000)
        self.assertEqual(ranking[1].username, "admin")
        self.assertEqual(ranking[1].net, 0)
        self.assertEqual(ranking[1].order_count, 0)

    def test_validation(self):
        """start > end và xem theo ngày quá 366 ngày bị ValidationError."""
        with self.assertRaises(ValidationError):
            self.env.reports.summary(date(2026, 10, 15), date(2026, 10, 10))
        with self.assertRaises(ValidationError):
            self.env.reports.series(date(2026, 1, 1), date(2026, 1, 1) + timedelta(days=367), "day")

    def test_staff_can_only_see_own_numbers(self):
        """Nhân viên xem số của người khác hoặc gọi by_staff bị PermissionDenied; my_summary luôn đúng của chính mình."""
        staff = self.env.user_repo.find_by_username("nhanvien")
        admin = self.env.user_repo.find_by_username("admin")
        self._insert_order("2026-10-10 10:00:00", user_id=staff.id, total=50000, discount=0, final=50000)

        self.env.login("nhanvien")
        with self.assertRaises(PermissionDenied):
            self.env.reports.summary(date(2026, 10, 1), date(2026, 10, 31), user_id=None)
        with self.assertRaises(PermissionDenied):
            self.env.reports.summary(date(2026, 10, 1), date(2026, 10, 31), user_id=admin.id)
        with self.assertRaises(PermissionDenied):
            self.env.reports.by_staff(date(2026, 10, 1), date(2026, 10, 31))

        my_s = self.env.reports.my_summary(date(2026, 10, 1), date(2026, 10, 31))
        self.assertEqual(my_s.order_count, 1)
        self.assertEqual(my_s.net, 50000)


if __name__ == "__main__":
    unittest.main()
