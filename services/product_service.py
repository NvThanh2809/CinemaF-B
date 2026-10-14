"""Nghiệp vụ tìm kiếm mặt hàng.

Người phụ trách: THÀNH VIÊN A.
HỢP ĐỒNG với module B (SalesPage gọi hai hàm này, ĐỪNG đổi chữ ký khi chưa báo B):
    search(keyword)      -> list[Product]         (từ khóa rỗng = trả về tất cả)
    get_variants(id)     -> list[ProductVariant]
"""


class ProductService:
    def __init__(self, product_repo):
        self._repo = product_repo

    def search(self, keyword):
        """TODO (A): cắt khoảng trắng đầu/cuối, rỗng thì lấy tất cả."""
        raise NotImplementedError("TODO (A): ProductService.search")

    def get_variants(self, product_id):
        """TODO (A)"""
        raise NotImplementedError("TODO (A): ProductService.get_variants")
