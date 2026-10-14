"""Test cho OrderService + OrderRepository + DiscountService (thanh toán, phạm vi xem đơn).

Người phụ trách: THÀNH VIÊN B.
Env() đăng nhập sẵn chủ cửa hàng; env.login('nhanvien') để đổi sang nhân viên. Tạo đơn qua env.orders.checkout(cart).

Cách làm: mỗi test bên dưới là MỘT hành vi cần kiểm tra. Viết xong test nào thì xóa dòng @TODO của test đó
và thay phần mô tả bằng code kiểm tra thật. Chạy: python -m unittest discover -s tests -t .
"""
import unittest

from tests.helpers import Env

TODO = unittest.skip("TODO (B): chưa viết test này")


class OrderServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    @TODO
    def test_checkout_saves_order_with_seller_and_reduces_stock(self):
        """Thanh toán xong: đơn được lưu kèm người bán, tổng/giảm/thực thu đúng, tồn kho giảm, giỏ hàng được xóa."""

    @TODO
    def test_checkout_requires_login(self):
        """Chưa đăng nhập thì checkout ném AuthError."""

    @TODO
    def test_checkout_empty_cart_rejected(self):
        """Giỏ rỗng ném EmptyCartError."""

    @TODO
    def test_insufficient_stock_rolls_back_everything(self):
        """Dòng thứ hai thiếu hàng: dòng đầu không bị trừ kho, không có đơn nào được lưu, giỏ vẫn giữ nguyên."""

    @TODO
    def test_discount_validation_messages(self):
        """Mã không tồn tại / hết hạn / chưa đủ tối thiểu / để trống: mỗi trường hợp một DiscountError rõ lý do; mã gõ chữ thường vẫn nhận."""

    @TODO
    def test_checkout_blocks_discount_that_is_no_longer_valid(self):
        """Áp mã rồi bớt hàng làm đơn dưới mức tối thiểu: checkout ném DiscountError."""

    @TODO
    def test_unit_price_is_saved_at_sale_time(self):
        """Đổi giá sản phẩm sau khi bán thì đơn cũ vẫn giữ giá lúc bán."""

    @TODO
    def test_staff_only_sees_own_orders_owner_sees_all(self):
        """Nhân viên chỉ thấy đơn của mình và không xem được đơn người khác (PermissionDenied); chủ cửa hàng thấy tất cả và lọc được theo nhân viên."""


if __name__ == "__main__":
    unittest.main()
