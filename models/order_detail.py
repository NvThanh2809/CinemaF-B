"""Một dòng trong đơn hàng: một biến thể sản phẩm + số lượng.

Người phụ trách: THÀNH VIÊN B.
HỢP ĐỒNG với module A: VariantDialog tạo OrderDetail(variant_id, product_name, size, unit_price, quantity).
"""


class OrderDetail:
    def __init__(self, variant_id, product_name, size, unit_price, quantity):
        self.variant_id = variant_id
        self.product_name = product_name
        self.size = size
        self.unit_price = unit_price
        # TODO (B): đóng gói - đổi thành thuộc tính _quantity + @property quantity có setter,
        #           ném ValueError("Số lượng không được âm") khi value < 0.
        self.quantity = quantity

    @property
    def code(self):
        """TODO (B): mã hiển thị trên hóa đơn, ví dụ variant_id=2 -> 'V002'."""
        raise NotImplementedError("TODO (B): OrderDetail.code")

    @property
    def subtotal(self):
        """TODO (B): thành tiền = đơn giá * số lượng."""
        raise NotImplementedError("TODO (B): OrderDetail.subtotal")

    def __repr__(self):
        return f"OrderDetail({self.product_name} {self.size} x{self.quantity})"
