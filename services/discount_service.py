from utils.exceptions import DiscountError
from utils.formatter import format_money


class DiscountService:
    def __init__(self, discount_repo):
        self._repo = discount_repo

    def list_active(self):
        return self._repo.list_active()

    def get_applicable(self, code, order_total):
        code = (code or "").strip().upper()
        if not code:
            raise DiscountError("Vui lòng nhập mã ưu đãi")
        discount = self._repo.find_by_code(code)
        if discount is None:
            raise DiscountError(f"Mã '{code}' không tồn tại")
        if not discount.active:
            raise DiscountError(f"Mã '{code}' đã hết hiệu lực")
        if order_total < discount.min_order_value:
            raise DiscountError(
                f"Đơn hàng cần tối thiểu {format_money(discount.min_order_value)} "
                f"để dùng mã '{code}'"
            )
        return discount
