"""Định dạng hiển thị."""


def format_money(value):
    """50000 -> '50.000đ'"""
    return f"{int(round(value)):,}".replace(",", ".") + "đ"


def short_money(value):
    """Rút gọn cho nhãn biểu đồ: 1500000 -> '1,5tr', 50000 -> '50k'."""
    value = float(value)
    for limit, suffix in ((1e9, " tỷ"), (1e6, "tr"), (1e3, "k")):
        if abs(value) >= limit:
            number = f"{value / limit:.1f}".rstrip("0").rstrip(".").replace(".", ",")
            return number + suffix
    return str(int(value))
