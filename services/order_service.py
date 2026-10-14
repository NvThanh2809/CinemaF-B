"""Thanh toán và tra cứu đơn đã bán.

Người phụ trách: THÀNH VIÊN B.
Phụ thuộc: ProductRepository.decrease_stock (A), AuthService.require_login (C, người bán = người đang đăng nhập).
"""
from datetime import datetime  # noqa: F401  (B dùng khi code)

from models.order import Order  # noqa: F401
from models.order_detail import OrderDetail  # noqa: F401
from utils.exceptions import DiscountError, EmptyCartError  # noqa: F401


class OrderService:
    def __init__(self, db, order_repo, product_repo, auth):
        self._db = db
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._auth = auth

    def checkout(self, cart):
        """TODO (B): thanh toán một CartService, trả về Order đã lưu (có id).

        Các bước: require_login -> giỏ rỗng thì EmptyCartError -> mã không còn hợp lệ thì DiscountError
        -> dựng Order (user_id = người bán) -> BỌC TRONG `with self._db.transaction():`
        trừ kho từng dòng (nên sắp xếp theo variant_id để tránh deadlock) rồi order_repo.insert
        -> cart.clear(). Thiếu hàng thì InsufficientStockError và rollback toàn bộ.
        """
        raise NotImplementedError("TODO (B): OrderService.checkout")

    def list_orders(self, start, end, user_id=None):
        """TODO (B): chủ cửa hàng xem tất cả (hoặc lọc user_id); nhân viên CHỈ thấy đơn của chính mình."""
        raise NotImplementedError("TODO (B): OrderService.list_orders")

    def get_order(self, order_id):
        """TODO (B): trả về Order; nhân viên không được xem đơn của người khác (PermissionDenied)."""
        raise NotImplementedError("TODO (B): OrderService.get_order")
