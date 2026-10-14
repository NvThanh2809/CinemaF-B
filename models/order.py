class Order:
    def __init__(self, created_at, total_amount, discount_amount, final_amount,
                 details=None, discount_id=None, discount_code=None, id=None,
                 user_id=None, seller_name=""):
        self.id = id
        self.created_at = created_at          # datetime
        self.user_id = user_id                # nhân viên lập đơn
        self.seller_name = seller_name
        self.total_amount = total_amount
        self.discount_id = discount_id
        self.discount_code = discount_code
        self.discount_amount = discount_amount
        self.final_amount = final_amount
        self.details = list(details or [])

    def __repr__(self):
        return f"Order({self.id}, {self.final_amount})"
