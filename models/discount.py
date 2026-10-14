"""Mã ưu đãi: lớp cha trừu tượng + 2 lớp con (kế thừa, đa hình).

Người phụ trách: THÀNH VIÊN B.
"""
from abc import ABC, abstractmethod


class Discount(ABC):
    """Lớp cha. Bảng discounts: id, code, type ('PERCENT' | 'FIXED'), value, min_order_value, active."""

    def __init__(self, id, code, min_order_value=0, active=True):
        self.id = id
        self.code = code
        self.min_order_value = min_order_value
        self.active = active

    def is_applicable(self, total):
        """TODO (B): True khi mã còn hiệu lực VÀ total >= min_order_value."""
        raise NotImplementedError("TODO (B): Discount.is_applicable")

    @abstractmethod
    def calculate(self, total):
        """Số tiền được giảm cho đơn có tổng `total` (lớp con cài đặt)."""

    @abstractmethod
    def describe(self):
        """Mô tả ngắn hiện trên giao diện, ví dụ 'Giảm 10%' (lớp con cài đặt)."""

    @staticmethod
    def from_row(row):
        """TODO (B): factory - từ một dòng DB (dict các cột của bảng discounts) tạo đúng lớp con."""
        raise NotImplementedError("TODO (B): Discount.from_row")


class PercentDiscount(Discount):
    def __init__(self, id, code, percent, min_order_value=0, active=True):
        super().__init__(id, code, min_order_value, active)
        self.percent = percent

    def calculate(self, total):
        """TODO (B): total * percent / 100 (làm tròn xuống số nguyên đồng)."""
        raise NotImplementedError("TODO (B): PercentDiscount.calculate")

    def describe(self):
        """TODO (B)"""
        raise NotImplementedError("TODO (B): PercentDiscount.describe")


class FixedDiscount(Discount):
    def __init__(self, id, code, amount, min_order_value=0, active=True):
        super().__init__(id, code, min_order_value, active)
        self.amount = amount

    def calculate(self, total):
        """TODO (B): giảm amount nhưng không vượt quá total."""
        raise NotImplementedError("TODO (B): FixedDiscount.calculate")

    def describe(self):
        """TODO (B): dùng utils.formatter.format_money."""
        raise NotImplementedError("TODO (B): FixedDiscount.describe")
