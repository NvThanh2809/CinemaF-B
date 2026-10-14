"""Truy vấn SQL cho đơn hàng và chi tiết đơn.

Người phụ trách: THÀNH VIÊN B.
Bảng orders(id, created_at, user_id, discount_id, total_amount, discount_amount, final_amount)
Bảng order_details(id, order_id, variant_id, quantity, unit_price)
Lưu ý: module C (ReportRepository) đọc các cột created_at, user_id, total_amount, discount_amount, final_amount
của bảng orders. Đổi tên/kiểu các cột này phải báo C.
"""
from models.order import Order  # noqa: F401  (B dùng khi code)
from models.order_detail import OrderDetail  # noqa: F401
from utils.dates import db_datetime, day_bounds, to_datetime  # noqa: F401


class OrderRepository:
    def __init__(self, db):
        self._db = db

    def insert(self, order):
        """TODO (B): ghi đơn + toàn bộ chi tiết, gán order.id, trả về id.

        Dùng self._db.insert("orders", {...}) (trả id vừa tạo). Không tự commit: OrderService bọc db.transaction().
        created_at truyền qua utils.dates.db_datetime(order.created_at).
        """
        raise NotImplementedError("TODO (B): OrderRepository.insert")

    def find_by_id(self, order_id):
        """TODO (B): trả về Order đầy đủ (kèm details, seller_name, discount_code) hoặc None."""
        raise NotImplementedError("TODO (B): OrderRepository.find_by_id")

    def list_orders(self, start, end, user_id=None, limit=500):
        """TODO (B): đơn trong khoảng ngày [start, end] (kiểu date, gồm cả ngày end), mới nhất trước.

        user_id=None là tất cả nhân viên. Dùng utils.dates.day_bounds và self._db.top(limit)/limit(limit).
        """
        raise NotImplementedError("TODO (B): OrderRepository.list_orders")
