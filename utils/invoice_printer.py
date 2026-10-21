import os
import subprocess
import sys

from config import CINEMA_ADDRESS, CINEMA_NAME, INVOICE_DIR
from utils.dates import DISPLAY_DATETIME
from utils.formatter import format_money

WIDTH = 52


def _money_row(label, value):
    text = format_money(value)
    return label + text.rjust(WIDTH - len(label))


def render_invoice_text(order):
    line = "-" * WIDTH
    out = [
        CINEMA_NAME.center(WIDTH),
        CINEMA_ADDRESS.center(WIDTH),
        "",
        "HÓA ĐƠN BÁN HÀNG".center(WIDTH),
        f"Số HĐ : {order.id:06d}" if order.id else "Số HĐ : -",
        f"Ngày  : {order.created_at.strftime(DISPLAY_DATETIME)}",
    ]
    if order.seller_name:
        out.append(f"Thu ngân: {order.seller_name}")
    out.append(line)
    for d in order.details:
        out.append(f"{d.code} {d.product_name} ({d.size})")
        left = f"   {d.quantity} x {format_money(d.unit_price)}"
        out.append(left + format_money(d.subtotal).rjust(WIDTH - len(left)))
    out.append(line)
    out.append(_money_row("Tổng tiền:", order.total_amount))
    if order.discount_amount:
        out.append(_money_row(f"Giảm giá ({order.discount_code}):", -order.discount_amount))
    out.append(_money_row("THANH TOÁN:", order.final_amount))
    out.append(line)
    out.append("Cảm ơn quý khách - Hẹn gặp lại!".center(WIDTH))
    return "\n".join(out)


def save_invoice(order):
    INVOICE_DIR.mkdir(parents=True, exist_ok=True)
    path = INVOICE_DIR / f"hoadon_{order.id:06d}.txt"
    path.write_text(render_invoice_text(order), encoding="utf-8")
    return path


def open_invoice(path, print_it=False):
    path = str(path)
    if sys.platform.startswith("win"):
        os.startfile(path, "print" if print_it else "open")
    elif sys.platform == "darwin":
        subprocess.Popen(["lpr", path] if print_it else ["open", path])
    else:
        subprocess.Popen(["lpr", path] if print_it else ["xdg-open", path])
