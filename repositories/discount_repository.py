from models.discount import Discount


class DiscountRepository:
    def __init__(self, db):
        self._db = db

    def find_by_code(self, code):
        row = self._db.query_one(
            "SELECT id, code, type, value, min_order_value, active FROM discounts WHERE code = ?",
            (code,),
        )
        return Discount.from_row(row) if row else None

    def list_active(self):
        rows = self._db.query(
            "SELECT id, code, type, value, min_order_value, active FROM discounts "
            "WHERE active = 1 ORDER BY code"
        )
        return [Discount.from_row(r) for r in rows]
