"""Hộp thoại chọn kích cỡ + số lượng.

Người phụ trách: THÀNH VIÊN A.
HỢP ĐỒNG với module B: VariantDialog(master, product, variants) rồi
    self.wait_window(dialog); dialog.result  # OrderDetail, hoặc None nếu hủy
Kết quả PHẢI là: OrderDetail(variant.id, product.name, variant.size, variant.price, qty)
"""
from tkinter import ttk

from models.order_detail import OrderDetail  # noqa: F401  (A dùng khi code)
from ui.helpers import BaseDialog


class VariantDialog(BaseDialog):
    def __init__(self, master, product, variants):
        super().__init__(master, "Chọn kích cỡ và số lượng")
        self.result = None  # OrderDetail
        self._product = product
        self._variants = variants  # list[ProductVariant] đã lọc bỏ size hết hàng

        card = ttk.Frame(self, style="Card.TFrame", padding=24)
        card.pack(fill="both", expand=True, padx=14, pady=14)
        ttk.Label(card, text=f"TODO (A): chọn size cho {product.name}", style="H2.TLabel").pack(anchor="w")
        # TODO (A): - Radiobutton cho từng size: "Size L - 50.000đ (còn 100)"
        #           - Spinbox số lượng (tối thiểu 1, tối đa = tồn kho của size đang chọn)
        #           - nhãn thành tiền cập nhật ngay khi đổi size / số lượng
        #           - OK: kiểm tra số nguyên dương và không vượt tồn kho, lỗi thì messagebox, đúng thì gán self.result
        ttk.Label(card, text=f"Có {len(variants)} kích cỡ để chọn.", style="CardMuted.TLabel").pack(anchor="w", pady=(6, 14))
        ttk.Button(card, text="Hủy", command=self.destroy).pack(anchor="e")
        self.present()
