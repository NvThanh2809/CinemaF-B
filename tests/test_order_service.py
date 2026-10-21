import unittest

from models.order_detail import OrderDetail
from services.cart_service import CartService
from tests.helpers import Env
from utils.exceptions import AuthError, DiscountError, EmptyCartError, InsufficientStockError

TODO = unittest.skip("TODO (B): chưa viết test này")


class OrderServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env(login_as="nhanvien")
        self.cart = CartService()

    def tearDown(self):
        self.env.close()

    def _add(self, product_name, size, qty):
        row = self.env.db.query_one(
            "SELECT v.id, v.price, p.name FROM product_variants v "
            "JOIN products p ON p.id = v.product_id WHERE p.name = ? AND v.size = ?",
            (product_name, size),
        )
        self.cart.add_item(OrderDetail(row["id"], row["name"], size, row["price"], qty))
        return row["id"]

    def _stock(self, variant_id):
        return self.env.db.scalar("SELECT stock FROM product_variants WHERE id = ?", (variant_id,))

    def test_checkout_saves_order_with_seller_and_reduces_stock(self):
        variant_id = self._add("Bỏng ngô phô mai", "L", 2)
        before = self._stock(variant_id)
        self.cart.apply_discount(self.env.discounts.get_applicable("giam10", self.cart.total))

        order = self.env.orders.checkout(self.cart)

        self.assertEqual((order.total_amount, order.discount_amount, order.final_amount), (100000, 10000, 90000))
        self.assertEqual(self._stock(variant_id), before - 2)
        self.assertTrue(self.cart.is_empty)

        saved = self.env.db.query_one(
            "SELECT o.user_id, o.final_amount, d.code AS code, u.full_name AS seller "
            "FROM orders o JOIN users u ON u.id = o.user_id "
            "LEFT JOIN discounts d ON d.id = o.discount_id WHERE o.id = ?",
            (order.id,),
        )
        self.assertEqual(saved["final_amount"], 90000)
        self.assertEqual(saved["code"], "GIAM10")
        self.assertEqual(saved["seller"], "Nhân viên mẫu")
        self.assertEqual(saved["user_id"], self.env.auth.current_user.id)
        line = self.env.db.query_one(
            "SELECT quantity, unit_price FROM order_details WHERE order_id = ?", (order.id,)
        )
        self.assertEqual((line["quantity"], line["unit_price"]), (2, 50000))

    def test_checkout_without_discount(self):
        self._add("Coca-Cola", "M", 2)
        order = self.env.orders.checkout(self.cart)
        self.assertEqual((order.total_amount, order.discount_amount, order.final_amount), (50000, 0, 50000))
        self.assertIsNone(order.discount_id)

    def test_checkout_requires_login(self):
        self._add("Bỏng ngô phô mai", "L", 1)
        self.env.auth.logout()
        with self.assertRaises(AuthError):
            self.env.orders.checkout(self.cart)

    def test_checkout_empty_cart_rejected(self):
        with self.assertRaises(EmptyCartError):
            self.env.orders.checkout(self.cart)

    def test_insufficient_stock_rolls_back_everything(self):
        first = self._add("Bỏng ngô phô mai", "L", 1)
        second = self._add("Trà đào", "L", 5)
        self.env.db.execute("UPDATE product_variants SET stock = 2 WHERE id = ?", (second,))
        stock_first = self._stock(first)

        with self.assertRaises(InsufficientStockError):
            self.env.orders.checkout(self.cart)

        self.assertEqual(self._stock(first), stock_first)
        self.assertEqual(self.env.db.scalar("SELECT COUNT(*) FROM orders"), 0)
        self.assertFalse(self.cart.is_empty)

    def test_discount_validation_messages(self):
        for code, total in (("KHONGCO", 500000), ("HETHAN", 500000), ("GIAM10", 50000), ("", 500000)):
            with self.assertRaises(DiscountError):
                self.env.discounts.get_applicable(code, total)
        self.assertEqual(self.env.discounts.get_applicable("giam10", 200000).code, "GIAM10")

    def test_list_active_excludes_expired_codes(self):
        codes = [d.code for d in self.env.discounts.list_active()]
        self.assertIn("GIAM10", codes)
        self.assertNotIn("HETHAN", codes)

    def test_checkout_blocks_discount_that_is_no_longer_valid(self):
        self._add("Bỏng ngô phô mai", "L", 2)
        self.cart.apply_discount(self.env.discounts.get_applicable("GIAM10", self.cart.total))
        self.cart.update_quantity(0, 1)
        with self.assertRaises(DiscountError):
            self.env.orders.checkout(self.cart)

    def test_unit_price_is_saved_at_sale_time(self):
        variant_id = self._add("Bỏng ngô phô mai", "L", 1)
        order = self.env.orders.checkout(self.cart)
        self.env.db.execute("UPDATE product_variants SET price = 99000 WHERE id = ?", (variant_id,))
        saved_price = self.env.db.scalar(
            "SELECT unit_price FROM order_details WHERE order_id = ?", (order.id,)
        )
        self.assertEqual(saved_price, 50000)

    @TODO
    def test_staff_only_sees_own_orders_owner_sees_all(self):
        """Nhân viên chỉ thấy đơn của mình và không xem được đơn người khác (PermissionDenied); chủ cửa hàng thấy tất cả và lọc được theo nhân viên."""


if __name__ == "__main__":
    unittest.main()
