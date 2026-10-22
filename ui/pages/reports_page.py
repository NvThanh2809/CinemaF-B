"""Trang Doanh số (chỉ chủ cửa hàng).

Hai tab: "Theo thời gian" (toàn cửa hàng hoặc một nhân viên, theo ngày/tháng) và "So sánh nhân viên".
Trang chỉ hiển thị; mọi phép tính và phân quyền nằm ở ctx.reports (ReportService).
"""
import tkinter as tk
from tkinter import ttk

from ui.pages.base import Page
from ui.theme import C
from ui.widgets import BarChart, Card, DataTable, DateRangeBar, PageHeader, StatCard
from utils.exceptions import AppError
from utils.formatter import format_money

ALL_STAFF = "Toàn cửa hàng"

PERIOD_COLUMNS = [
    ("period", "Kỳ", 80, "w"),
    ("orders", "Số đơn", 60, "e"),
    ("gross", "Tiền hàng", 100, "e"),
    ("discount", "Giảm giá", 90, "e"),
    ("net", "Thực thu", 110, "e"),
]
STAFF_COLUMNS = [
    ("rank", "Hạng", 50, "center"),
    ("full_name", "Họ tên", 180, "w"),
    ("username", "Tên đăng nhập", 130, "w"),
    ("role", "Vai trò", 110, "w"),
    ("orders", "Số đơn", 70, "e"),
    ("gross", "Tiền hàng", 110, "e"),
    ("discount", "Giảm giá", 100, "e"),
    ("net", "Thực thu", 120, "e"),
]


class ReportsPage(Page):
    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        self._me = ctx.auth.require_owner()
        self._targets = {ALL_STAFF: None}  # nhãn hiển thị -> user_id (None = cả cửa hàng)
        PageHeader(self, "Doanh số", "Thống kê doanh thu theo thời gian và theo từng nhân viên").pack(fill="x")

        self._tabs = ttk.Notebook(self)
        self._tabs.pack(fill="both", expand=True, pady=(14, 0))
        self._time_tab = ttk.Frame(self._tabs, padding=(0, 14, 0, 0))
        self._staff_tab = ttk.Frame(self._tabs, padding=(0, 14, 0, 0))
        self._tabs.add(self._time_tab, text="Theo thời gian")
        self._tabs.add(self._staff_tab, text="So sánh nhân viên")
        self._build_time_tab()
        self._build_staff_tab()

    def on_show(self):
        self._load_targets()
        self._refresh_time()
        self._refresh_staff()

    # ================================================================ tab 1: theo thời gian
    def _build_time_tab(self):
        tab = self._time_tab
        controls = Card(tab, padding=(16, 12))
        controls.pack(fill="x")
        row = ttk.Frame(controls.inner, style="Card.TFrame")
        row.pack(fill="x")
        ttk.Label(row, text="Đối tượng", style="Card.TLabel").pack(side="left")
        self._target = tk.StringVar(value=ALL_STAFF)
        self._target_box = ttk.Combobox(row, textvariable=self._target, state="readonly", width=30,
                                        values=[ALL_STAFF])
        self._target_box.pack(side="left", padx=(8, 24))
        self._target_box.bind("<<ComboboxSelected>>", lambda e: self._refresh_time())
        self._granularity = tk.StringVar(value="day")
        for text, value in (("Theo ngày", "day"), ("Theo tháng", "month")):
            ttk.Radiobutton(row, text=text, value=value, variable=self._granularity,
                            command=self._on_granularity).pack(side="left", padx=(0, 14))
        self._range = DateRangeBar(controls.inner, on_apply=self._refresh_time, default="month",
                                   style="Card.TFrame")
        self._range.pack(anchor="w", pady=(10, 0))

        stats = ttk.Frame(tab)
        stats.pack(fill="x", pady=(14, 0))
        self._cards = {}
        for i, (key, title, accent) in enumerate((
                ("orders", "Số đơn", C["primary"]), ("gross", "Tổng tiền hàng", C["muted"]),
                ("discount", "Giảm giá đã dùng", C["warning"]), ("net", "Doanh thu thực thu", C["success"]))):
            card = StatCard(stats, title, accent=accent)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))
            stats.columnconfigure(i, weight=1, uniform="stat")
            self._cards[key] = card

        body = ttk.Frame(tab)
        body.pack(fill="both", expand=True, pady=(14, 0))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)
        chart_card = Card(body, padding=(14, 12))
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._chart_title = ttk.Label(chart_card.inner, text="Doanh thu thực thu", style="H2.TLabel")
        self._chart_title.pack(anchor="w")
        self._chart = BarChart(chart_card.inner, height=200)
        self._chart.pack(fill="both", expand=True, pady=(8, 0))
        table_card = Card(body, padding=(14, 12))
        table_card.grid(row=0, column=1, sticky="nsew")
        ttk.Label(table_card.inner, text="Chi tiết", style="H2.TLabel").pack(anchor="w", pady=(0, 8))
        self._period_table = DataTable(table_card.inner, PERIOD_COLUMNS, height=8)
        self._period_table.pack(fill="both", expand=True)

    def _load_targets(self):
        """Nạp lại danh sách đối tượng (cửa hàng + từng tài khoản), giữ nguyên lựa chọn hiện tại nếu còn."""
        current = self._target.get()
        self._targets = {ALL_STAFF: None}
        for user, _orders in self.ctx.users.list_users():
            self._targets[f"{user.full_name} ({user.username})"] = user.id
        self._target_box.config(values=list(self._targets))
        self._target.set(current if current in self._targets else ALL_STAFF)

    def _on_granularity(self):
        """Đổi cách xem thì đặt khoảng mặc định hợp lý: theo ngày -> tháng này, theo tháng -> năm nay."""
        self._range.preset("month" if self._granularity.get() == "day" else "year", apply=False)
        self._refresh_time()

    def _refresh_time(self):
        try:
            start, end = self._range.get_range()
            user_id = self._targets.get(self._target.get())
            granularity = self._granularity.get()
            summary = self.ctx.reports.summary(start, end, user_id)
            series = self.ctx.reports.series(start, end, granularity, user_id)
        except (ValueError, AppError) as exc:  # ngày nhập sai, khoảng quá dài...: báo nhẹ nhàng, giữ nguyên số cũ
            self.warn("Không xem được doanh số", exc)
            return
        self._cards["orders"].set(str(summary.order_count),
                                  f"TB {format_money(summary.net / summary.order_count)}/đơn" if summary.order_count else "Chưa có đơn")
        self._cards["gross"].set(format_money(summary.gross), "Trước giảm giá")
        self._cards["discount"].set(format_money(summary.discount), "Tổng giảm giá đã áp dụng")
        self._cards["net"].set(format_money(summary.net), "Sau giảm giá")

        unit = "ngày" if granularity == "day" else "tháng"
        self._chart_title.config(text=f"Doanh thu thực thu theo {unit}")
        self._chart.set_data([p.label for p in series], [p.net for p in series],
                             [f"{p.label}: {format_money(p.net)} ({p.order_count} đơn)" for p in series])
        self._period_table.clear()
        for p in series:
            self._period_table.add((p.label, p.order_count, format_money(p.gross), format_money(p.discount),
                                    format_money(p.net)), tags=() if p.order_count else ("muted",))
        self._period_table.add(("Tổng", summary.order_count, format_money(summary.gross),
                                format_money(summary.discount), format_money(summary.net)), tags=("total",))

    # ================================================================ tab 2: so sánh nhân viên
    def _build_staff_tab(self):
        tab = self._staff_tab
        controls = Card(tab, padding=(16, 12))
        controls.pack(fill="x")
        self._staff_range = DateRangeBar(controls.inner, on_apply=self._refresh_staff, default="month",
                                         style="Card.TFrame")
        self._staff_range.pack(anchor="w")

        card = Card(tab, padding=(14, 12))
        card.pack(fill="both", expand=True, pady=(14, 0))
        top = ttk.Frame(card.inner, style="Card.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Xếp hạng theo doanh thu thực thu", style="H2.TLabel").pack(side="left")
        ttk.Label(top, text="Bấm đúp vào một người để xem chi tiết theo thời gian", style="CardMuted.TLabel").pack(
            side="right")
        self._staff_chart = BarChart(card.inner, height=150)
        self._staff_chart.pack(fill="x", pady=(8, 8))
        self._staff_table = DataTable(card.inner, STAFF_COLUMNS, height=6)
        self._staff_table.pack(fill="both", expand=True)
        self._staff_table.tree.bind("<Double-1>", lambda e: self._open_staff_detail())

    def _refresh_staff(self):
        try:
            start, end = self._staff_range.get_range()
            rows = self.ctx.reports.by_staff(start, end)
        except (ValueError, AppError) as exc:
            self.warn("Không xem được doanh số", exc)
            return
        self._staff_table.clear()
        for rank, r in enumerate(rows, 1):
            name = r.full_name + ("" if r.active else " (đã khóa)")
            self._staff_table.add(
                (rank, name, r.username, "Chủ cửa hàng" if r.role == "OWNER" else "Nhân viên", r.order_count,
                 format_money(r.gross), format_money(r.discount), format_money(r.net)),
                iid=str(r.user_id), tags=() if r.order_count else ("muted",))
        self._staff_chart.set_data([r.full_name for r in rows], [r.net for r in rows],
                                   [f"{r.full_name}: {format_money(r.net)} ({r.order_count} đơn)" for r in rows])

    def _open_staff_detail(self):
        """Bấm đúp một người: sang tab 1, chọn đúng người đó và dùng cùng khoảng ngày."""
        iid = self._staff_table.selected()
        if iid is None:
            return
        label = next((name for name, uid in self._targets.items() if uid is not None and str(uid) == iid), None)
        if label is None:
            return
        try:
            start, end = self._staff_range.get_range()
        except ValueError as exc:
            self.warn("Khoảng ngày không hợp lệ", exc)
            return
        self._target.set(label)
        self._range.set_range(start, end)
        self._tabs.select(self._time_tab)
        self._refresh_time()