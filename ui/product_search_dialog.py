"""Hộp thoại danh sách mặt hàng khớp từ khóa.

Người phụ trách: THÀNH VIÊN A.
HỢP ĐỒNG với module B: ProductSearchDialog(master, products, keyword="") rồi
    self.wait_window(dialog); dialog.result  # Product đã chọn, hoặc None nếu đóng
"""
from tkinter import ttk

from ui.helpers import BaseDialog


class ProductSearchDialog(BaseDialog):
    def __init__(self, master, products, keyword=""):
        super().__init__(master, "Kết quả tìm kiếm")
        self.result = None  # Product được chọn
        self._products = products

        card = ttk.Frame(self, style="Card.TFrame", padding=24)
        card.pack(fill="both", expand=True, padx=14, pady=14)
        ttk.Label(card, text="TODO (A): hộp thoại kết quả tìm kiếm", style="H2.TLabel").pack(anchor="w")
        # TODO (A): - dòng "Tìm thấy N mặt hàng cho '<keyword>'"
        #           - bảng ui.widgets.DataTable: Mã, Tên mặt hàng, Danh mục
        #           - double-click / Enter / nút "Chọn" -> gán self.result rồi self.destroy()
        #           - Escape hoặc nút "Đóng" -> self.destroy() (result vẫn None)
        ttk.Label(card, text=f"Nhận được {len(products)} mặt hàng cho '{keyword}'.",
                  style="CardMuted.TLabel").pack(anchor="w", pady=(6, 14))
        ttk.Button(card, text="Đóng", command=self.destroy).pack(anchor="e")
        self.present()
