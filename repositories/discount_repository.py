"""Truy vấn SQL cho mã ưu đãi.

Người phụ trách: THÀNH VIÊN B.
"""
from models.discount import Discount  # noqa: F401  (B dùng khi code)


class DiscountRepository:
    def __init__(self, db):
        self._db = db

    def find_by_code(self, code):
        """TODO (B): trả về Discount (qua Discount.from_row) hoặc None nếu không có mã."""
        raise NotImplementedError("TODO (B): DiscountRepository.find_by_code")

    def list_active(self):
        """TODO (B): list[Discount] của các mã còn hiệu lực (active = 1), sắp xếp theo code."""
        raise NotImplementedError("TODO (B): DiscountRepository.list_active")
