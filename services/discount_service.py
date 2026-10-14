"""Tra cứu và kiểm tra mã ưu đãi.

Người phụ trách: THÀNH VIÊN B.
"""
from utils.exceptions import DiscountError  # noqa: F401  (B dùng khi code)
from utils.formatter import format_money  # noqa: F401


class DiscountService:
    def __init__(self, discount_repo):
        self._repo = discount_repo

    def list_active(self):
        """TODO (B): list[Discount] đang hiệu lực (đổ vào ô chọn mã trên SalesPage)."""
        raise NotImplementedError("TODO (B): DiscountService.list_active")

    def get_applicable(self, code, order_total):
        """TODO (B): trả về Discount nếu dùng được cho đơn có tổng order_total.

        Ném DiscountError (thông báo tiếng Việt, nêu rõ lý do) khi: để trống mã, mã không tồn tại,
        mã hết hiệu lực, đơn chưa đạt giá trị tối thiểu. Mã không phân biệt hoa thường.
        """
        raise NotImplementedError("TODO (B): DiscountService.get_applicable")
