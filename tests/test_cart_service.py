"""Test cho CartService (hóa đơn tạm). Lớp này không đụng DB nên chỉ cần CartService() và OrderDetail(...).

Người phụ trách: THÀNH VIÊN B.
Dùng OrderDetail(variant_id, tên, size, đơn giá, số lượng) và PercentDiscount / FixedDiscount.

Cách làm: mỗi test bên dưới là MỘT hành vi cần kiểm tra. Viết xong test nào thì xóa dòng @TODO của test đó
và thay phần mô tả bằng code kiểm tra thật. Chạy: python -m unittest discover -s tests -t .
"""
import unittest

from tests.helpers import Env

TODO = unittest.skip("TODO (B): chưa viết test này")


class CartServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    @TODO
    def test_total_and_subtotal(self):
        """2 dòng hàng: thành tiền từng dòng và tổng tiền đúng."""

    @TODO
    def test_same_variant_merges_quantity(self):
        """Thêm cùng variant_id hai lần thì chỉ còn 1 dòng, số lượng cộng dồn."""

    @TODO
    def test_update_quantity_and_remove(self):
        """update_quantity đổi số lượng; số lượng 0 thì xóa dòng."""

    @TODO
    def test_invalid_quantity_rejected(self):
        """add_item với số lượng 0 ném ValueError."""

    @TODO
    def test_percent_discount(self):
        """Giảm 10% đơn 150.000đ: giảm 15.000đ, phải trả 135.000đ."""

    @TODO
    def test_fixed_discount_never_exceeds_total(self):
        """Mã giảm cố định lớn hơn tổng tiền: phải trả 0đ, không âm."""

    @TODO
    def test_discount_below_minimum_rejected(self):
        """Đơn chưa đạt giá trị tối thiểu: apply_discount ném DiscountError."""

    @TODO
    def test_only_one_discount_per_order(self):
        """Áp mã thứ hai thì thay mã thứ nhất (mỗi đơn tối đa 1 mã)."""

    @TODO
    def test_discount_becomes_invalid_after_removing_items(self):
        """Bớt hàng làm đơn dưới mức tối thiểu: discount_still_valid False và discount_amount về 0."""

    @TODO
    def test_clear_removes_items_and_discount(self):
        """clear() xóa cả hàng lẫn mã ưu đãi."""

    @TODO
    def test_items_returns_a_copy(self):
        """Sửa danh sách trả về từ .items không làm thay đổi giỏ hàng (đóng gói)."""


if __name__ == "__main__":
    unittest.main()
