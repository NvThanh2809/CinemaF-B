"""Xuất hóa đơn dạng văn bản (.txt) và mở/in file.

Người phụ trách: THÀNH VIÊN B.
Dùng config.CINEMA_NAME, CINEMA_ADDRESS, INVOICE_DIR và utils.formatter.format_money.
"""
from config import CINEMA_ADDRESS, CINEMA_NAME, INVOICE_DIR  # noqa: F401  (B dùng khi code)
from utils.formatter import format_money  # noqa: F401


def render_invoice_text(order):
    """TODO (B): trả về chuỗi hóa đơn (rộng ~52 ký tự): tên rạp, địa chỉ, số HĐ, ngày giờ, người bán,
    từng dòng (mã, tên, size, SL x đơn giá, thành tiền), tổng tiền, giảm giá (kèm mã), THANH TOÁN, lời cảm ơn."""
    raise NotImplementedError("TODO (B): render_invoice_text")


def save_invoice(order):
    """TODO (B): lưu hóa đơn ra INVOICE_DIR/hoadon_<id 6 chữ số>.txt (UTF-8), trả về đường dẫn Path."""
    raise NotImplementedError("TODO (B): save_invoice")


def open_invoice(path, print_it=False):
    """TODO (B): mở file bằng ứng dụng mặc định; print_it=True thì gửi ra máy in (Windows: os.startfile(path, 'print'))."""
    raise NotImplementedError("TODO (B): open_invoice")
