"""Test cho ProductService + ProductRepository (tìm kiếm, biến thể, trừ kho).

Người phụ trách: THÀNH VIÊN A.
Env() có sẵn menu mẫu: 11 sản phẩm, 20 biến thể. Dùng env.products / env.product_repo.

Cách làm: mỗi test bên dưới là MỘT hành vi cần kiểm tra. Viết xong test nào thì xóa dòng @TODO của test đó
và thay phần mô tả bằng code kiểm tra thật. Chạy: python -m unittest discover -s tests -t .
"""
import unittest

from tests.helpers import Env

TODO = unittest.skip("TODO (A): chưa viết test này")


class ProductServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    @TODO
    def test_search_ignores_accents_and_case(self):
        """Tìm 'BONG NGO' vẫn ra 'Bỏng ngô phô mai'; từ khóa không tồn tại trả danh sách rỗng."""

    @TODO
    def test_search_empty_keyword_returns_all(self):
        """Từ khóa rỗng hoặc toàn khoảng trắng trả về cả 11 sản phẩm."""

    @TODO
    def test_search_matches_category_name(self):
        """Tìm 'nước uống' trả về các sản phẩm thuộc danh mục Nước uống."""

    @TODO
    def test_search_treats_percent_and_underscore_literally(self):
        """Tìm '%' hoặc '_' không khớp mọi sản phẩm (dùng utils.text.like_escape)."""

    @TODO
    def test_variants_sorted_by_price(self):
        """Bỏng ngô phô mai có đúng 2 size: M 30.000đ rồi L 50.000đ."""

    @TODO
    def test_decrease_stock_reduces_stock(self):
        """decrease_stock(variant, 2) giảm đúng 2 đơn vị tồn kho."""

    @TODO
    def test_decrease_stock_never_goes_negative(self):
        """Trừ quá tồn kho ném InsufficientStockError, thông báo nêu tên hàng + size + tồn hiện có, tồn kho không đổi."""


if __name__ == "__main__":
    unittest.main()
