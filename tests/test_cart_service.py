import unittest

from models.discount import FixedDiscount, PercentDiscount
from models.order_detail import OrderDetail
from services.cart_service import CartService
from utils.exceptions import DiscountError


def item(variant_id=1, price=50000, qty=1, name="Bỏng ngô phô mai", size="L"):
    return OrderDetail(variant_id, name, size, price, qty)


class CartServiceTest(unittest.TestCase):
    def setUp(self):
        self.cart = CartService()

    def test_total_and_subtotal(self):
        self.cart.add_item(item(1, 50000, 2))
        self.cart.add_item(item(2, 25000, 1, "Coca-Cola", "M"))
        self.assertEqual(self.cart.total, 125000)
        self.assertEqual(self.cart.items[0].subtotal, 100000)

    def test_same_variant_merges_quantity(self):
        self.cart.add_item(item(1, 50000, 1))
        self.cart.add_item(item(1, 50000, 2))
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.items[0].quantity, 3)

    def test_update_quantity_and_remove(self):
        self.cart.add_item(item(1, 50000, 1))
        self.cart.add_item(item(2, 25000, 1))
        self.cart.update_quantity(0, 4)
        self.assertEqual(self.cart.items[0].quantity, 4)
        self.cart.update_quantity(0, 0)
        self.assertEqual(len(self.cart.items), 1)

    def test_invalid_quantity_rejected(self):
        with self.assertRaises(ValueError):
            self.cart.add_item(item(1, 50000, 0))

    def test_percent_discount(self):
        self.cart.add_item(item(1, 50000, 3))
        self.cart.apply_discount(PercentDiscount(1, "GIAM10", 10, 100000))
        self.assertEqual(self.cart.discount_amount, 15000)
        self.assertEqual(self.cart.final_amount, 135000)

    def test_fixed_discount_never_exceeds_total(self):
        self.cart.add_item(item(1, 10000, 1))
        self.cart.apply_discount(FixedDiscount(1, "BIG", 50000, 0))
        self.assertEqual(self.cart.final_amount, 0)

    def test_discount_below_minimum_rejected(self):
        self.cart.add_item(item(1, 50000, 1))
        with self.assertRaises(DiscountError):
            self.cart.apply_discount(PercentDiscount(1, "GIAM10", 10, 100000))

    def test_only_one_discount_per_order(self):
        self.cart.add_item(item(1, 50000, 3))
        self.cart.apply_discount(PercentDiscount(1, "A", 10, 0))
        self.cart.apply_discount(FixedDiscount(2, "B", 20000, 0))
        self.assertEqual(self.cart.discount.code, "B")

    def test_discount_becomes_invalid_after_removing_items(self):
        self.cart.add_item(item(1, 50000, 2))
        self.cart.apply_discount(PercentDiscount(1, "GIAM10", 10, 100000))
        self.cart.update_quantity(0, 1)
        self.assertFalse(self.cart.discount_still_valid)
        self.assertEqual(self.cart.discount_amount, 0)

    def test_clear_removes_items_and_discount(self):
        self.cart.add_item(item(1, 50000, 3))
        self.cart.apply_discount(PercentDiscount(1, "A", 10, 0))
        self.cart.clear()
        self.assertTrue(self.cart.is_empty)
        self.assertIsNone(self.cart.discount)
        self.assertEqual(self.cart.final_amount, 0)

    def test_items_returns_a_copy(self):
        self.cart.add_item(item(1, 50000, 1))
        self.cart.items.clear()
        self.assertEqual(len(self.cart.items), 1)


if __name__ == "__main__":
    unittest.main()
