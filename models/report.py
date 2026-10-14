from dataclasses import dataclass


@dataclass
class SalesSummary:
    """Tổng hợp doanh số trong một khoảng."""
    order_count: int = 0
    gross: int = 0      # tổng tiền hàng (trước giảm giá)
    discount: int = 0   # tổng giảm giá
    net: int = 0        # doanh thu thực thu


@dataclass
class PeriodSales:
    """Doanh số của một ngày hoặc một tháng."""
    period: str         # 'YYYY-MM-DD' hoặc 'YYYY-MM'
    label: str          # 'dd/mm' hoặc 'mm/yyyy' để hiển thị
    order_count: int = 0
    gross: int = 0
    discount: int = 0
    net: int = 0


@dataclass
class StaffSales:
    user_id: int
    full_name: str
    username: str
    role: str
    active: bool
    order_count: int = 0
    gross: int = 0
    discount: int = 0
    net: int = 0
