"""Truy vấn SQL cho danh mục / sản phẩm / biến thể.

Người phụ trách: THÀNH VIÊN A.
"""
from models.product import Product
from models.product_variant import ProductVariant
from utils.exceptions import InsufficientStockError


class ProductRepository:
    def __init__(self, db):
        self._db = db

    def search_products(self, keyword):
        """Tìm sản phẩm theo tên HOẶC tên danh mục, không phân biệt dấu/hoa thường.

        Trả về list[Product], sắp xếp theo tên danh mục rồi tên sản phẩm.
        """
        keyword = (keyword or "").strip()
        cond_p = self._db.like_no_accent("p.name")
        cond_c = self._db.like_no_accent("c.name")

        sql = f"""
            SELECT p.id, p.category_id, p.name, c.name AS category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE {cond_p} OR {cond_c}
            ORDER BY c.name, p.name
        """
        param = self._db.like_param(keyword)
        rows = self._db.query(sql, (param, param))
        return [Product(r["id"], r["category_id"], r["name"], r["category_name"]) for r in rows]

    def get_variants(self, product_id):
        """Trả về list[ProductVariant] của sản phẩm, sắp xếp theo giá tăng dần."""
        sql = """
            SELECT id, product_id, size, price, stock
            FROM product_variants
            WHERE product_id = ?
            ORDER BY price ASC
        """
        rows = self._db.query(sql, (product_id,))
        return [ProductVariant(r["id"], r["product_id"], r["size"], r["price"], r["stock"]) for r in rows]

    def decrease_stock(self, variant_id, qty):
        """Trừ tồn kho có điều kiện `stock >= ?`. Ném InsufficientStockError nếu thiếu hàng."""
        sql = "UPDATE product_variants SET stock = stock - ? WHERE id = ? AND stock >= ?"
        rowcount = self._db.execute(sql, (qty, variant_id, qty))

        if rowcount == 0:
            # Truy vấn thông tin chi tiết để báo lỗi tiếng Việt thân thiện
            info_sql = """
                SELECT p.name, v.size, v.stock
                FROM product_variants v
                JOIN products p ON v.product_id = p.id
                WHERE v.id = ?
            """
            row = self._db.query_one(info_sql, (variant_id,))
            if row:
                raise InsufficientStockError(
                    f"Mặt hàng '{row['name']}' (size {row['size']}) chỉ còn {row['stock']} sản phẩm trong kho (cần {qty})."
                )
            raise InsufficientStockError(f"Biến thể mã {variant_id} không tồn tại.")
        return True