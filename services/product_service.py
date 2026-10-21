"""Nghiệp vụ tìm kiếm mặt hàng.

Người phụ trách: THÀNH VIÊN A.
"""
class ProductService:
    def __init__(self, product_repo):
        self._repo = product_repo

    def search(self, keyword):
        """Cắt khoảng trắng đầu/cuối, từ khóa rỗng thì lấy tất cả."""
        keyword = (keyword or "").strip()
        return self._repo.search_products(keyword)

    def get_variants(self, product_id):
        """Lấy danh sách các size và giá của sản phẩm."""
        return self._repo.get_variants(product_id)
