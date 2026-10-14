"""Hóa đơn tạm (giỏ hàng) đang lập, chưa lưu DB. Mỗi đơn tối đa 1 mã ưu đãi.

Người phụ trách: THÀNH VIÊN B.
Lớp này KHÔNG đụng DB, nên viết và test độc lập được ngay (xem tests/test_cart_service.py).
"""


class CartService:
    def __init__(self):
        self._items = []      # list[OrderDetail]
        self._discount = None  # Discount hoặc None

    # ---- mặt hàng ----
    @property
    def items(self):
        """TODO (B): trả về BẢN SAO danh sách (đóng gói), không trả self._items."""
        raise NotImplementedError("TODO (B): CartService.items")

    @property
    def is_empty(self):
        raise NotImplementedError("TODO (B): CartService.is_empty")

    def add_item(self, detail):
        """TODO (B): thêm dòng; cùng variant_id thì cộng dồn số lượng; số lượng <= 0 thì ném ValueError."""
        raise NotImplementedError("TODO (B): CartService.add_item")

    def update_quantity(self, index, quantity):
        """TODO (B): đặt lại số lượng của dòng; quantity <= 0 thì xóa dòng."""
        raise NotImplementedError("TODO (B): CartService.update_quantity")

    def remove_item(self, index):
        raise NotImplementedError("TODO (B): CartService.remove_item")

    def clear(self):
        """TODO (B): xóa hết dòng và bỏ luôn mã ưu đãi."""
        raise NotImplementedError("TODO (B): CartService.clear")

    # ---- tiền ----
    @property
    def total(self):
        """TODO (B): tổng thành tiền các dòng (trước giảm giá)."""
        raise NotImplementedError("TODO (B): CartService.total")

    # ---- mã ưu đãi ----
    @property
    def discount(self):
        raise NotImplementedError("TODO (B): CartService.discount")

    @property
    def discount_still_valid(self):
        """TODO (B): True khi chưa có mã, hoặc mã vẫn đủ điều kiện với tổng tiền hiện tại."""
        raise NotImplementedError("TODO (B): CartService.discount_still_valid")

    def apply_discount(self, discount):
        """TODO (B): áp mã (thay mã cũ nếu có - chỉ 1 mã/đơn); chưa đủ điều kiện thì ném DiscountError."""
        raise NotImplementedError("TODO (B): CartService.apply_discount")

    def remove_discount(self):
        raise NotImplementedError("TODO (B): CartService.remove_discount")

    @property
    def discount_amount(self):
        """TODO (B): số tiền giảm; 0 nếu không có mã hoặc mã không còn hợp lệ."""
        raise NotImplementedError("TODO (B): CartService.discount_amount")

    @property
    def final_amount(self):
        """TODO (B): total - discount_amount."""
        raise NotImplementedError("TODO (B): CartService.final_amount")
