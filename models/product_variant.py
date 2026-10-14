class ProductVariant:
    """Biến thể của sản phẩm (kích cỡ + giá + tồn kho)."""

    def __init__(self, id, product_id, size, price, stock=0):
        self.id = id
        self.product_id = product_id
        self.size = size
        self.price = price
        self.stock = stock

    def __repr__(self):
        return f"ProductVariant({self.id}, {self.size}, {self.price})"
