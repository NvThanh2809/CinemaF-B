"""Hộp thoại xem hóa đơn sau khi thanh toán (và xem/in lại từ Lịch sử đơn hàng).

Người phụ trách: THÀNH VIÊN B.
HỢP ĐỒNG: InvoiceView(master, order) với order là models.order.Order đầy đủ.
"""
from tkinter import ttk

from ui.helpers import BaseDialog


class InvoiceView(BaseDialog):
    def __init__(self, master, order):
        super().__init__(master, f"Hóa đơn #{order.id}")
        card = ttk.Frame(self, style="Card.TFrame", padding=24)
        card.pack(fill="both", expand=True, padx=14, pady=14)
        ttk.Label(card, text="TODO (B): hiển thị hóa đơn", style="H2.TLabel").pack(anchor="w")
        # TODO (B): - tk.Text chỉ đọc hiển thị utils.invoice_printer.render_invoice_text(order), phông Consolas
        #           - gọi save_invoice(order) và hiện đường dẫn file đã lưu
        #           - nút "Mở file", "In hóa đơn" (open_invoice; bắt lỗi nếu không mở được), "Đóng"
        ttk.Button(card, text="Đóng", command=self.destroy).pack(anchor="e", pady=(14, 0))
        self.present()
