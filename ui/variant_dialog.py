"""Hộp thoại chọn kích cỡ + số lượng.

Người phụ trách: THÀNH VIÊN A.
"""
import tkinter as tk
from tkinter import messagebox, ttk
from models.order_detail import OrderDetail
from ui.helpers import BaseDialog
from ui.theme import C, F_BOLD
from utils.formatter import format_money


class VariantDialog(BaseDialog):
    def __init__(self, master, product, variants):
        super().__init__(master, f"Chọn size: {product.name}")
        self.result = None  # OrderDetail
        self._product = product
        self._variants = [v for v in variants if v.stock > 0]  # Chỉ cho phép chọn size còn hàng

        card = ttk.Frame(self, style="Card.TFrame", padding=22)
        card.pack(fill="both", expand=True, padx=14, pady=14)

        if not self._variants:
            ttk.Label(card, text="Mặt hàng này hiện đã hết toàn bộ các kích cỡ!", style="Error.TLabel").pack(pady=10)
            ttk.Button(card, text="Đóng", command=self.destroy).pack(pady=5)
            self.present()
            return

        ttk.Label(card, text=product.name, style="H2.TLabel").pack(anchor="w")
        ttk.Label(card, text="Chọn kích cỡ:", style="CardMuted.TLabel").pack(anchor="w", pady=(8, 4))

        self.variant_var = tk.IntVar(value=self._variants[0].id)
        for v in self._variants:
            text = f"Size {v.size} — {format_money(v.price)}  (Còn {v.stock})"
            rb = ttk.Radiobutton(card, text=text, value=v.id, variable=self.variant_var,
                                 command=self._on_change, style="Card.TRadiobutton")
            rb.pack(anchor="w", pady=2)

        qty_frame = ttk.Frame(card, style="Card.TFrame")
        qty_frame.pack(fill="x", pady=(14, 6))
        ttk.Label(qty_frame, text="Số lượng:", style="Card.TLabel").pack(side="left")

        self.qty_var = tk.IntVar(value=1)
        self.spn_qty = ttk.Spinbox(qty_frame, from_=1, to=self._get_current_stock(),
                                   textvariable=self.qty_var, width=6, justify="center")
        self.spn_qty.pack(side="left", padx=10)
        self.qty_var.trace_add("write", lambda *args: self._on_change())

        # Thành tiền (dùng màu C["primary"] theo quy tắc 12)
        self.lbl_subtotal = ttk.Label(card, text="", foreground=C["primary"], font=F_BOLD, style="Card.TLabel")
        self.lbl_subtotal.pack(anchor="w", pady=(10, 16))

        btn_box = ttk.Frame(card, style="Card.TFrame")
        btn_box.pack(fill="x")
        ttk.Button(btn_box, text="Xác nhận", style="Primary.TButton", command=self._on_confirm).pack(side="right")
        ttk.Button(btn_box, text="Hủy", command=self.destroy).pack(side="right", padx=(0, 8))

        self.bind("<Return>", lambda e: self._on_confirm())
        self.bind("<Escape>", lambda e: self.destroy())

        self._on_change()
        self.present()

    def _get_current_variant(self):
        v_id = self.variant_var.get()
        return next((v for v in self._variants if v.id == v_id), self._variants[0])

    def _get_current_stock(self):
        return self._get_current_variant().stock

    def _on_change(self):
        variant = self._get_current_variant()
        self.spn_qty.configure(to=max(1, variant.stock))
        try:
            qty = self.qty_var.get()
        except tk.TclError:
            qty = 1
        subtotal = variant.price * max(1, qty)
        self.lbl_subtotal.config(text=f"Thành tiền: {format_money(subtotal)}")

    def _on_confirm(self):
        try:
            qty = self.qty_var.get()
            if qty <= 0:
                raise ValueError
        except (tk.TclError, ValueError):
            messagebox.showwarning("Lỗi", "Số lượng phải là số nguyên lớn hơn 0!", parent=self)
            return

        variant = self._get_current_variant()
        if qty > variant.stock:
            messagebox.showwarning("Lỗi", f"Chỉ còn {variant.stock} sản phẩm trong kho!", parent=self)
            return

        self.result = OrderDetail(
            variant_id=variant.id,
            product_name=self._product.name,
            size=variant.size,
            unit_price=variant.price,
            quantity=qty
        )
        self.destroy()