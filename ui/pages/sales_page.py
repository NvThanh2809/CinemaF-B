import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from services.cart_service import CartService
from ui.invoice_view import InvoiceView
from ui.pages.base import Page
from ui.product_search_dialog import ProductSearchDialog
from ui.theme import C, F_BASE, F_BIG, F_BOLD
from ui.variant_dialog import VariantDialog
from ui.widgets import Card, DataTable, PageHeader
from utils.exceptions import AppError
from utils.formatter import format_money

TOTAL_IID = "total"
MSG_NO_DISCOUNT = "Chưa áp dụng mã (mỗi đơn chỉ dùng 1 mã)"


class SalesPage(Page):
    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        self._cart = CartService()

        PageHeader(self, "Bán hàng", f"Thu ngân: {ctx.auth.require_login().full_name}").pack(fill="x")
        self._build_search()

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=(14, 0))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        self._build_invoice(body).grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        side = ttk.Frame(body)
        side.grid(row=0, column=1, sticky="ns")
        ttk.Frame(side, width=330, height=1).pack()
        self._build_discount(side).pack(fill="x")
        self._build_payment(side).pack(fill="x", pady=(14, 0))
        self.refresh_cart()

    def _build_search(self):
        card = Card(self, padding=(16, 12))
        card.pack(fill="x", pady=(14, 0))
        row = ttk.Frame(card.inner, style="Card.TFrame")
        row.pack(fill="x")
        ttk.Label(row, text="Tìm mặt hàng", style="Card.TLabel", font=F_BOLD).pack(side="left")
        self._keyword = tk.StringVar()
        self._search_entry = ttk.Entry(row, textvariable=self._keyword, width=44)
        self._search_entry.pack(side="left", padx=12)
        self._search_entry.bind("<Return>", lambda e: self._on_search())
        ttk.Button(row, text="Tìm kiếm", style="Primary.TButton", command=self._on_search).pack(side="left")
        ttk.Label(row, text="Gõ tên hoặc danh mục (không cần dấu). Để trống để xem tất cả.",
                  style="CardMuted.TLabel").pack(side="left", padx=14)

    def _build_invoice(self, parent):
        card = Card(parent)
        head = ttk.Frame(card.inner, style="Card.TFrame")
        head.pack(fill="x")
        ttk.Label(head, text="Hóa đơn tạm", style="H2.TLabel").pack(side="left")
        ttk.Button(head, text="Hủy đơn", command=self._on_cancel).pack(side="right")
        ttk.Button(head, text="Xóa dòng", command=self._on_remove).pack(side="right", padx=6)
        ttk.Button(head, text="Sửa số lượng", command=self._on_edit_quantity).pack(side="right")

        self._table = DataTable(card.inner, [
            ("code", "Mã", 70, "center"),
            ("name", "Tên mặt hàng", 250, "w"),
            ("size", "Kích cỡ", 70, "center"),
            ("price", "Đơn giá", 100, "e"),
            ("qty", "Số lượng", 80, "center"),
            ("subtotal", "Thành tiền", 120, "e"),
        ], height=9)
        self._table.pack(fill="both", expand=True, pady=(10, 0))
        self._table.tree.bind("<Double-1>", lambda e: self._on_edit_quantity())
        self._table.tree.bind("<Delete>", lambda e: self._on_remove())
        ttk.Label(card.inner, text="Nhấp đúp một dòng để sửa số lượng · phím Delete để xóa dòng",
                  style="CardMuted.TLabel").pack(anchor="w", pady=(8, 0))
        return card

    def _build_discount(self, parent):
        card = Card(parent)
        ttk.Label(card.inner, text="Mã ưu đãi", style="H2.TLabel").pack(anchor="w")
        row = ttk.Frame(card.inner, style="Card.TFrame")
        row.pack(fill="x", pady=(10, 0))
        self._code = tk.StringVar()
        self._code_box = ttk.Combobox(row, textvariable=self._code, width=14, values=self._active_codes())
        self._code_box.pack(side="left", fill="x", expand=True)
        self._code_box.bind("<Return>", lambda e: self._on_apply_discount())
        ttk.Button(row, text="Áp dụng", command=self._on_apply_discount).pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Bỏ mã", command=self._on_remove_discount).pack(side="left", padx=(6, 0))
        self._discount_info = ttk.Label(card.inner, text=MSG_NO_DISCOUNT, style="CardMuted.TLabel",
                                        wraplength=290, justify="left")
        self._discount_info.pack(anchor="w", pady=(8, 0))
        return card

    def _build_payment(self, parent):
        card = Card(parent)
        ttk.Label(card.inner, text="Thanh toán", style="H2.TLabel").pack(anchor="w")
        grid = ttk.Frame(card.inner, style="Card.TFrame")
        grid.pack(fill="x", pady=(10, 0))
        grid.columnconfigure(1, weight=1)
        self._lbl_total = self._money_row(grid, 0, "Tổng tiền hàng")
        self._lbl_discount = self._money_row(grid, 1, "Giảm giá")
        ttk.Separator(grid).grid(row=2, column=0, columnspan=2, sticky="ew", pady=8)
        self._lbl_final = self._money_row(grid, 3, "Khách cần trả", big=True)
        ttk.Button(card.inner, text="THANH TOÁN", style="Big.Primary.TButton",
                   command=self._on_checkout).pack(fill="x", pady=(14, 0))
        return card

    @staticmethod
    def _money_row(parent, row, label, big=False):
        ttk.Label(parent, text=label, style="Card.TLabel", font=F_BOLD if big else F_BASE).grid(
            row=row, column=0, sticky="w", pady=2)
        value = ttk.Label(parent, text="0đ", style="Card.TLabel", font=F_BIG if big else F_BASE, anchor="e")
        if big:
            value.config(foreground=C["primary"])
        value.grid(row=row, column=1, sticky="e", pady=2)
        return value

    def _active_codes(self):
        try:
            return [d.code for d in self.ctx.discounts.list_active()]
        except AppError as exc:
            self.warn("Không tải được mã ưu đãi", exc)
            return []

    def on_show(self):
        self._code_box.config(values=self._active_codes())
        self._search_entry.focus_set()

    def has_unsaved_work(self):
        return not self._cart.is_empty

    def refresh_cart(self):
        self._table.clear()
        for index, d in enumerate(self._cart.items):
            self._table.add((d.code, d.product_name, d.size, format_money(d.unit_price),
                             d.quantity, format_money(d.subtotal)), iid=str(index))
        self._table.add(("", "TỔNG TIỀN", "", "", "", format_money(self._cart.total)),
                        iid=TOTAL_IID, tags=("total",))

        self._lbl_total.config(text=format_money(self._cart.total))
        discount_amount = self._cart.discount_amount
        self._lbl_discount.config(text=f"-{format_money(discount_amount)}" if discount_amount else "0đ")
        self._lbl_final.config(text=format_money(self._cart.final_amount))
        self._refresh_discount_info()

    def _refresh_discount_info(self):
        discount = self._cart.discount
        if discount is None:
            self._discount_info.config(text=MSG_NO_DISCOUNT, foreground=C["muted"])
        elif not self._cart.discount_still_valid:
            self._discount_info.config(
                text=f"Mã {discount.code} không còn đủ điều kiện (đơn tối thiểu "
                     f"{format_money(discount.min_order_value)}). Hãy bỏ mã hoặc thêm hàng.",
                foreground=C["danger"])
        else:
            self._discount_info.config(
                text=f"Đang dùng {discount.code}: {discount.describe()}", foreground=C["success"])

    def _selected_index(self):
        selected = self._table.selected()
        if selected is None or selected == TOTAL_IID:
            return None
        return int(selected)

    def _on_search(self):
        keyword = self._keyword.get().strip()
        try:
            products = self.ctx.products.search(keyword)
        except AppError as exc:
            self.warn("Không thể tìm kiếm", exc)
            return
        if not products:
            messagebox.showinfo("Không có kết quả", f"Không tìm thấy mặt hàng nào cho '{keyword}'.", parent=self)
            return
        dialog = ProductSearchDialog(self, products, keyword)
        self.wait_window(dialog)
        if dialog.result:
            self._choose_variant(dialog.result)

    def _choose_variant(self, product):
        variants = [v for v in self.ctx.products.get_variants(product.id) if v.stock > 0]
        if not variants:
            messagebox.showwarning("Hết hàng", f"{product.name} hiện đã hết hàng.", parent=self)
            return
        dialog = VariantDialog(self, product, variants)
        self.wait_window(dialog)
        if dialog.result:
            self._cart.add_item(dialog.result)
            self.refresh_cart()
            self._keyword.set("")
            self._search_entry.focus_set()

    def _on_edit_quantity(self):
        index = self._selected_index()
        if index is None:
            return
        item = self._cart.items[index]
        quantity = simpledialog.askinteger(
            "Sửa số lượng", f"{item.product_name} ({item.size})\nSố lượng mới (0 để xóa dòng):",
            parent=self, initialvalue=item.quantity, minvalue=0, maxvalue=999)
        if quantity is not None:
            self._cart.update_quantity(index, quantity)
            self.refresh_cart()

    def _on_remove(self):
        index = self._selected_index()
        if index is not None:
            self._cart.remove_item(index)
            self.refresh_cart()

    def _on_cancel(self):
        if self._cart.is_empty or messagebox.askyesno(
                "Hủy đơn", "Xóa toàn bộ đơn hàng hiện tại?", parent=self):
            self._reset_order()

    def _on_apply_discount(self):
        try:
            discount = self.ctx.discounts.get_applicable(self._code.get(), self._cart.total)
            self._cart.apply_discount(discount)
        except AppError as exc:
            messagebox.showwarning("Mã ưu đãi", str(exc), parent=self)
            return
        self.refresh_cart()

    def _on_remove_discount(self):
        self._cart.remove_discount()
        self._code.set("")
        self.refresh_cart()

    def _on_checkout(self):
        if self._cart.is_empty:
            messagebox.showinfo("Thanh toán", "Đơn hàng chưa có mặt hàng nào.", parent=self)
            return
        confirmed = messagebox.askyesno(
            "Xác nhận thanh toán",
            f"Khách cần thanh toán {format_money(self._cart.final_amount)}.\nXác nhận?",
            parent=self)
        if not confirmed:
            return
        try:
            order = self.ctx.orders.checkout(self._cart)
        except AppError as exc:
            messagebox.showerror("Không thể thanh toán", str(exc), parent=self)
            self.refresh_cart()
            return
        self._reset_order(already_cleared=True)
        InvoiceView(self, order)

    def _reset_order(self, already_cleared=False):
        if not already_cleared:
            self._cart.clear()
        self._code.set("")
        self._keyword.set("")
        self.refresh_cart()
        self._search_entry.focus_set()
