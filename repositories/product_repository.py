"""Truy vấn SQL cho danh mục / sản phẩm / biến thể.

Người phụ trách: THÀNH VIÊN A.
Repository chỉ chứa SQL và ánh xạ dòng -> model. KHÔNG viết nghiệp vụ ở đây.
Gợi ý: self._db.query(sql, params), self._db.execute(sql, params); luôn dùng tham số `?`.
"""
from models.product import Product  # noqa: F401  (A dùng khi code)
from models.product_variant import ProductVariant  # noqa: F401
from utils.exceptions import InsufficientStockError  # noqa: F401


class ProductRepository:
    def __init__(self, db):
        self._db = db

    def search_products(self, keyword):
        """TODO (A): tìm sản phẩm theo tên HOẶC tên danh mục, không phân biệt dấu/hoa thường.

        Trả về list[Product] (có category_name), sắp xếp theo danh mục rồi tên.
        Gợi ý: Database.like_no_accent("p.name") + Database.like_param(keyword) lo sẵn khác biệt SQL Server/SQLite.
        """
        raise NotImplementedError("TODO (A): ProductRepository.search_products")

    def get_variants(self, product_id):
        """TODO (A): trả về list[ProductVariant] của một sản phẩm, sắp xếp theo giá tăng dần."""
        raise NotImplementedError("TODO (A): ProductRepository.get_variants")

    def decrease_stock(self, variant_id, quantity):
        """TODO (A): trừ tồn kho (B gọi hàm này khi thanh toán, bên trong db.transaction()).

        UPDATE có điều kiện `stock >= ?` để kho không bao giờ âm; nếu không cập nhật được dòng nào
        thì ném InsufficientStockError với thông báo tiếng Việt nêu rõ tên hàng, size, tồn hiện có.
        """
        raise NotImplementedError("TODO (A): ProductRepository.decrease_stock")
