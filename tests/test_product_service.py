"""Test cho ProductService + ProductRepository (tìm kiếm, biến thể, trừ kho).

Người phụ trách: THÀNH VIÊN A.
"""
import unittest
from tests.helpers import Env
from utils.exceptions import InsufficientStockError


class ProductServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    def test_search_ignores_accents_and_case(self):
        """Tìm 'BONG NGO' vẫn ra 'Bỏng ngô phô mai'; từ khóa không tồn tại trả danh sách rỗng."""
        results = self.env.products.search("BONG NGO")
        names = [p.name for p in results]
        self.assertIn("Bỏng ngô phô mai", names)

        empty_results = self.env.products.search("tu_khoa_khong_ton_tai_123")
        self.assertEqual(len(empty_results), 0)

    def test_search_empty_keyword_returns_all(self):
        """Từ khóa rỗng hoặc toàn khoảng trắng trả về cả 11 sản phẩm."""
        self.assertEqual(len(self.env.products.search("")), 11)
        self.assertEqual(len(self.env.products.search("   ")), 11)

    def test_search_matches_category_name(self):
        """Tìm 'nước uống' trả về các sản phẩm thuộc danh mục Nước uống."""
        results = self.env.products.search("nuoc uong")
        self.assertTrue(len(results) > 0)
        for p in results:
            self.assertEqual(p.category_name, "Nước uống")

    def test_search_treats_percent_and_underscore_literally(self):
        """Tìm '%' hoặc '_' không khớp mọi sản phẩm (dùng utils.text.like_escape)."""
        self.assertEqual(len(self.env.products.search("%")), 0)
        self.assertEqual(len(self.env.products.search("_")), 0)

    def test_variants_sorted_by_price(self):
        """Bỏng ngô phô mai có đúng 2 size: M 30.000đ rồi L 50.000đ."""
        prods = [p for p in self.env.products.search("Bỏng ngô phô mai") if p.name == "Bỏng ngô phô mai"]
        self.assertTrue(len(prods) > 0)
        variants = self.env.products.get_variants(prods[0].id)
        self.assertEqual(len(variants), 2)
        self.assertEqual(variants[0].size, "M")
        self.assertEqual(variants[0].price, 30000)
        self.assertEqual(variants[1].size, "L")
        self.assertEqual(variants[1].price, 50000)

    def test_decrease_stock_reduces_stock(self):
        """decrease_stock giảm đúng số lượng tồn kho."""
        variants = self.env.product_repo.get_variants(1)
        old_stock = variants[0].stock
        self.env.product_repo.decrease_stock(variants[0].id, 2)
        updated_variants = self.env.product_repo.get_variants(1)
        self.assertEqual(updated_variants[0].stock, old_stock - 2)

    def test_decrease_stock_never_goes_negative(self):
        """Trừ quá tồn kho ném InsufficientStockError, tồn kho không đổi."""
        variants = self.env.product_repo.get_variants(1)
        old_stock = variants[0].stock
        with self.assertRaises(InsufficientStockError):
            self.env.product_repo.decrease_stock(variants[0].id, old_stock + 100)

        # Kiểm tra tồn kho vẫn nguyên vẹn
        current_variants = self.env.product_repo.get_variants(1)
        self.assertEqual(current_variants[0].stock, old_stock)


if __name__ == "__main__":
    unittest.main()
