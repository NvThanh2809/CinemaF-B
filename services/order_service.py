"""Thanh toán và tra cứu đơn đã bán.

Người phụ trách: THÀNH VIÊN B.
Phụ thuộc: ProductRepository.decrease_stock (A), AuthService.require_login (C, người bán = người đang đăng nhập).
"""
from datetime import datetime

from models.order import Order
from models.order_detail import OrderDetail
from utils.exceptions import DiscountError, EmptyCartError


class OrderService:
    def __init__(self, db, order_repo, product_repo, auth):
        self._db = db
        self._order_repo = order_repo
        self._product_repo = product_repo
        self._auth = auth

    def checkout(self, cart):
        seller = self._auth.require_login()
        if cart.is_empty:
            raise EmptyCartError("Đơn hàng chưa có mặt hàng nào")
        if not cart.discount_still_valid:
            raise DiscountError("Đơn hàng không còn đủ điều kiện dùng mã ưu đãi, hãy bỏ mã và thử lại")

        discount = cart.discount
        order = Order(
            created_at=datetime.now().replace(microsecond=0),
            user_id=seller.id,
            seller_name=seller.full_name,
            total_amount=cart.total,
            discount_amount=cart.discount_amount,
            final_amount=cart.final_amount,
            details=[
                OrderDetail(d.variant_id, d.product_name, d.size, d.unit_price, d.quantity)
                for d in cart.items
            ],
            discount_id=discount.id if discount else None,
            discount_code=discount.code if discount else None,
        )

        with self._db.transaction():
            for d in sorted(order.details, key=lambda x: x.variant_id):
                self._product_repo.decrease_stock(d.variant_id, d.quantity)
            self._order_repo.insert(order)

        cart.clear()
        return order

    def list_orders(self, start, end, user_id=None):
        """TODO (B): chủ cửa hàng xem tất cả (hoặc lọc user_id); nhân viên CHỈ thấy đơn của chính mình."""
        raise NotImplementedError("TODO (B): OrderService.list_orders")

    def get_order(self, order_id):
        """TODO (B): trả về Order; nhân viên không được xem đơn của người khác (PermissionDenied)."""
        raise NotImplementedError("TODO (B): OrderService.get_order")
