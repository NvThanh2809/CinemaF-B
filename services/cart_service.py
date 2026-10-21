from utils.exceptions import DiscountError


class CartService:
    def __init__(self):
        self._items = []
        self._discount = None

    @property
    def items(self):
        return list(self._items)

    @property
    def is_empty(self):
        return not self._items

    def add_item(self, detail):
        if detail.quantity <= 0:
            raise ValueError("Số lượng phải lớn hơn 0")
        for item in self._items:
            if item.variant_id == detail.variant_id:
                item.quantity += detail.quantity
                return
        self._items.append(detail)

    def update_quantity(self, index, quantity):
        if quantity <= 0:
            self.remove_item(index)
        else:
            self._items[index].quantity = quantity

    def remove_item(self, index):
        del self._items[index]

    def clear(self):
        self._items.clear()
        self._discount = None

    @property
    def total(self):
        return sum(item.subtotal for item in self._items)

    @property
    def discount(self):
        return self._discount

    @property
    def discount_still_valid(self):
        return self._discount is None or self._discount.is_applicable(self.total)

    def apply_discount(self, discount):
        if not discount.is_applicable(self.total):
            raise DiscountError("Đơn hàng chưa đủ điều kiện dùng mã này")
        self._discount = discount

    def remove_discount(self):
        self._discount = None

    @property
    def discount_amount(self):
        if self._discount is None or not self.discount_still_valid:
            return 0
        return self._discount.calculate(self.total)

    @property
    def final_amount(self):
        return self.total - self.discount_amount
