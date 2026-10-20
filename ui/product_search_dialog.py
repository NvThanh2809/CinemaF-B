"""Hộp thoại danh sách mặt hàng khớp từ khóa.

Người phụ trách: THÀNH VIÊN A.
"""
from tkinter import ttk
from ui.helpers import BaseDialog
from ui.widgets import DataTable


class ProductSearchDialog(BaseDialog):
    def __init__(self, master, products, keyword=""):
        super().__init__(master, "Kết quả tìm kiếm")
        self.result = None  # Product được chọn
        self._products = products

        card = ttk.Frame(self, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True, padx=14, pady=14)

        kw_text = f" cho '{keyword}'" if keyword else ""
        ttk.Label(card, text=f"Tìm thấy {len(products)} mặt hàng{kw_text}:", style="H2.TLabel").pack(anchor="w", pady=(0, 10))

        # columns: (key, title, width, anchor)
        columns = [
            ("id", "Mã", 60, "center"),
            ("name", "Tên mặt hàng", 220, "w"),
            ("category_name", "Danh mục", 150, "w")
        ]
        self.table = DataTable(card, columns=columns, height=10)
        self.table.pack(fill="both", expand=True)

        for p in self._products:
            self.table.add((p.id, p.name, p.category_name), iid=str(p.id))

        self.table.tree.bind("<Double-1>", lambda e: self._on_select())
        self.bind("<Return>", lambda e: self._on_select())
        self.bind("<Escape>", lambda e: self.destroy())

        btn_box = ttk.Frame(card, style="Card.TFrame")
        btn_box.pack(fill="x", pady=(12, 0))
        ttk.Button(btn_box, text="Chọn", style="Primary.TButton", command=self._on_select).pack(side="right")
        ttk.Button(btn_box, text="Đóng", command=self.destroy).pack(side="right", padx=(0, 8))

        self.present()

    def _on_select(self):
        sel_id = self.table.selected()
        if not sel_id:
            return
        prod_id = int(sel_id)
        for p in self._products:
            if p.id == prod_id:
                self.result = p
                break
        self.destroy()
