"""Trang Lịch sử đơn hàng.

Người phụ trách: THÀNH VIÊN B (Hỗ trợ hoàn thiện bởi THÀNH VIÊN A).
"""
import sys
from pathlib import Path

# Thêm thư mục gốc dự án vào sys.path để có thể chạy trực tiếp file này trên IDE mà không lỗi import
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tkinter as tk
from tkinter import ttk
from ui.invoice_view import InvoiceView
from ui.pages.base import Page
from ui.widgets import DataTable, DateRangeBar, PageHeader

try:
    from utils.dates import format_datetime
except ImportError:
    from utils.dates import to_datetime, DISPLAY_DATETIME
    def format_datetime(value):
        dt = to_datetime(value)
        return dt.strftime(DISPLAY_DATETIME) if dt else ""

from utils.formatter import format_money


class OrdersPage(Page):
    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        self._owner = ctx.auth.require_login().is_owner

        PageHeader(self, "Lịch sử đơn hàng",
                   "Tất cả đơn đã thanh toán" if self._owner else "Các đơn bạn đã bán").pack(fill="x")

        # 1. Bộ lọc
        filter_bar = ttk.Frame(self)
        filter_bar.pack(fill="x", pady=(14, 10))

        self.date_bar = DateRangeBar(filter_bar, on_apply=self.load_data)
        self.date_bar.pack(side="left")

        self.cbo_staff = None
        self.staff_map = {"Tất cả": None}

        if self._owner:
            ttk.Label(filter_bar, text="Nhân viên:").pack(side="left", padx=(18, 6))
            self.staff_var = tk.StringVar(value="Tất cả")
            self.cbo_staff = ttk.Combobox(filter_bar, textvariable=self.staff_var, state="readonly", width=18)
            self.cbo_staff.pack(side="left")
            self.cbo_staff.bind("<<ComboboxSelected>>", lambda e: self.load_data())

        btn_view = ttk.Button(filter_bar, text="Xem chi tiết hóa đơn", command=self.view_invoice)
        btn_view.pack(side="right")

        # 2. Bảng DataTable: columns = [(key, tiêu đề, độ rộng, căn lề)]
        columns = [
            ("id", "Số HĐ", 80, "center"),
            ("created_at", "Thời gian", 160, "center"),
            ("seller_name", "Nhân viên", 160, "w"),
            ("total_amount", "Tổng tiền", 120, "e"),
            ("discount_amount", "Giảm giá", 110, "e"),
            ("final_amount", "Thực thu", 120, "e")
        ]
        self.table = DataTable(self, columns=columns, height=14)
        self.table.pack(fill="both", expand=True)
        self.table.tree.bind("<Double-1>", lambda e: self.view_invoice())

        # 3. Dòng tổng kết
        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill="x", pady=(8, 0))
        self.lbl_summary = ttk.Label(summary_frame, text="", style="H2.TLabel")
        self.lbl_summary.pack(side="right")

    def on_show(self):
        """Được gọi mỗi khi mở lại tab này."""
        if self._owner and self.cbo_staff:
            try:
                users = self.ctx.users.list_users() or []
                self.staff_map = {"Tất cả": None}
                for u in users:
                    self.staff_map[u.full_name or u.username] = u.id
                self.cbo_staff["values"] = list(self.staff_map.keys())
            except Exception:
                pass
        self.load_data()

    def load_data(self):
        try:
            start_date, end_date = self.date_bar.get_range()
        except ValueError as err:
            self.warn("Lỗi", err)
            return

        user_id = None
        if self._owner and self.cbo_staff:
            selected_name = self.staff_var.get()
            user_id = self.staff_map.get(selected_name)

        try:
            orders = self.ctx.orders.list_orders(start_date, end_date, user_id=user_id) or []
        except Exception as e:
            self.warn("Lỗi tải dữ liệu", e)
            return

        self.table.clear()
        total_revenue = 0

        for o in orders:
            self.table.add((
                f"#{o.id}",
                format_datetime(o.created_at),
                o.seller_name or f"User #{o.user_id}",
                format_money(o.total_amount),
                format_money(o.discount_amount),
                format_money(o.final_amount)
            ), iid=str(o.id))
            total_revenue += o.final_amount

        limit_note = " (Đạt giới hạn 500 đơn)" if len(orders) >= 500 else ""
        self.lbl_summary.config(
            text=f"Tổng: {len(orders)} đơn{limit_note}  |  Tổng thực thu: {format_money(total_revenue)}"
        )

    def view_invoice(self):
        selected_id = self.table.selected()
        if not selected_id:
            return
        order_id = int(selected_id)
        try:
            order = self.ctx.orders.get_order(order_id)
            if order:
                # InvoiceView tự động hiển thị modal trong constructor
                InvoiceView(self, order)
        except Exception as e:
            self.warn("Lỗi", f"Không thể mở hóa đơn: {e}")


if __name__ == "__main__":
    from tests.helpers import Env
    from ui.theme import setup_styles

    root = tk.Tk()
    root.title("Xem trước - Lịch sử đơn hàng")
    root.geometry("900x600")
    setup_styles(root)

    env = Env()
    page = OrdersPage(root, env, None)
    page.pack(fill="both", expand=True)
    page.on_show()

    root.mainloop()
    env.close()
