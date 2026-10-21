class OrderDetail:
    def __init__(self, variant_id, product_name, size, unit_price, quantity):
        self.variant_id = variant_id
        self.product_name = product_name
        self.size = size
        self.unit_price = unit_price
        self._quantity = 0
        self.quantity = quantity

    @property
    def code(self):
        return f"V{self.variant_id:03d}"

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if value < 0:
            raise ValueError("Số lượng không được âm")
        self._quantity = value

    @property
    def subtotal(self):
        return self.unit_price * self._quantity

    def __repr__(self):
        return f"OrderDetail({self.product_name} {self.size} x{self._quantity})"
