from abc import ABC, abstractmethod

from utils.formatter import format_money


class Discount(ABC):
    def __init__(self, id, code, min_order_value=0, active=True):
        self.id = id
        self.code = code
        self.min_order_value = min_order_value
        self.active = active

    def is_applicable(self, total):
        return self.active and total >= self.min_order_value

    @abstractmethod
    def calculate(self, total):
        pass

    @abstractmethod
    def describe(self):
        pass

    @staticmethod
    def from_row(row):
        common = dict(
            id=row["id"],
            code=row["code"],
            min_order_value=row["min_order_value"],
            active=bool(row["active"]),
        )
        if row["type"] == "PERCENT":
            return PercentDiscount(percent=row["value"], **common)
        if row["type"] == "FIXED":
            return FixedDiscount(amount=row["value"], **common)
        raise ValueError(f"Loại mã ưu đãi không hợp lệ: {row['type']}")


class PercentDiscount(Discount):
    def __init__(self, id, code, percent, min_order_value=0, active=True):
        super().__init__(id, code, min_order_value, active)
        self.percent = percent

    def calculate(self, total):
        return min(total, int(total * self.percent / 100))

    def describe(self):
        return f"Giảm {self.percent}%"


class FixedDiscount(Discount):
    def __init__(self, id, code, amount, min_order_value=0, active=True):
        super().__init__(id, code, min_order_value, active)
        self.amount = amount

    def calculate(self, total):
        return min(self.amount, total)

    def describe(self):
        return f"Giảm {format_money(self.amount)}"
