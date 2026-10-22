"""Trang Tổng quan (dashboard mở đầu).
Chủ cửa hàng thấy số liệu cả cửa hàng, nhân viên chỉ thấy số liệu của chính mình.
Trang chỉ hiển thị, mọi số liệu lấy từ ctx.reports (ReportService đã tự kiểm tra quyền).
"""
from datetime import timedelta
from tkinter import ttk

from ui.pages.base import WEEKDAYS, Page
from ui.theme import C
from ui.widgets import BarChart, Card, DataTable, PageHeader, StatCard
from utils.dates import first_of_month
from utils.formatter import format_money

DAYS_IN_CHART = 14
TOP_STAFF = 5


class HomePage(Page):
    """Chủ cửa hàng thấy số liệu cả cửa hàng, nhân viên thấy số liệu của chính mình."""

    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        self._me = ctx.auth.require_login()
        self._owner = self._me.is_owner
        scope = "toàn cửa hàng" if self._owner else "của riêng bạn"
        PageHeader(self, f"Xin chào, {self._me.full_name}",
                   f"Tổng quan hoạt động {scope} - {self._me.role_label}").pack(fill="x")

        stats = ttk.Frame(self)
        stats.pack(fill="x", pady=(16, 0))
        self._cards = {}
        for i, (key, title, accent) in enumerate((
                ("today_net", "Doanh thu hôm nay", C["success"]),
                ("today_orders", "Số đơn hôm nay", C["stat_card"]),
                ("month_net", "Doanh thu tháng này", C["success"]),
                ("month_avg", "Giá trị đơn trung bình (tháng)", C["warning"]))):
            card = StatCard(stats, title, accent=accent)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))
            stats.columnconfigure(i, weight=1, uniform="stat")
            self._cards[key] = card

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=(16, 0))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        chart_card = Card(body, padding=(16, 14))
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        ttk.Label(chart_card.inner, text=f"Doanh thu {DAYS_IN_CHART} ngày gần nhất", style="H2.TLabel").pack(anchor="w")
        self._chart = BarChart(chart_card.inner, height=240)
        self._chart.pack(fill="both", expand=True, pady=(8, 0))

        side = Card(body, padding=(16, 14))
        side.grid(row=0, column=1, sticky="nsew")
        if self._owner:
            ttk.Label(side.inner, text="Nhân viên nổi bật tháng này", style="H2.TLabel").pack(anchor="w")
            self._staff_table = DataTable(side.inner, [
                ("rank", "Hạng", 45, "center"), ("name", "Nhân viên", 150, "w"),
                ("orders", "Đơn", 50, "e"), ("net", "Thực thu", 110, "e")], height=6)
            self._staff_table.pack(fill="both", expand=True, pady=(10, 10))
            ttk.Button(side.inner, text="Xem báo cáo chi tiết  →", style="Primary.TButton",
                       command=lambda: self.shell.navigate("reports")).pack(anchor="e")
        else:
            ttk.Label(side.inner, text="Ca làm việc của bạn", style="H2.TLabel").pack(anchor="w")
            self._staff_note = ttk.Label(side.inner, text="", style="Card.TLabel", wraplength=300, justify="left")
            self._staff_note.pack(anchor="w", pady=(10, 14))
            ttk.Button(side.inner, text="Bắt đầu bán hàng  →", style="Primary.TButton",
                       command=lambda: self.shell.navigate("sales")).pack(anchor="w")

    def on_show(self):
        """Nạp lại số liệu mỗi khi mở trang (vừa bán xong quay về là thấy số mới)."""
        reports = self.ctx.reports
        today = reports.today()
        month_start = first_of_month(today)
        user_id = None if self._owner else self._me.id  # nhân viên: luôn lọc theo chính mình

        day = reports.summary(today, today, user_id)
        month = reports.summary(month_start, today, user_id)
        self._cards["today_net"].set(format_money(day.net), WEEKDAYS[today.weekday()] + ", " + today.strftime("%d/%m/%Y"))
        self._cards["today_orders"].set(str(day.order_count), "đơn đã thanh toán")
        self._cards["month_net"].set(format_money(month.net), f"{month.order_count} đơn từ đầu tháng")
        average = month.net / month.order_count if month.order_count else 0
        self._cards["month_avg"].set(format_money(average), "doanh thu thực thu / đơn")

        series = reports.series(today - timedelta(days=DAYS_IN_CHART - 1), today, "day", user_id)
        self._chart.set_data([p.label for p in series], [p.net for p in series],
                             [f"{p.label}: {format_money(p.net)} ({p.order_count} đơn)" for p in series])

        if self._owner:
            self._staff_table.clear()
            ranked = [r for r in reports.by_staff(month_start, today) if r.order_count > 0][:TOP_STAFF]
            for rank, r in enumerate(ranked, 1):
                self._staff_table.add((rank, r.full_name, r.order_count, format_money(r.net)))
            if not ranked:
                self._staff_table.add(("", "Chưa có đơn nào trong tháng", "", ""), tags=("muted",))
        else:
            self._staff_note.config(
                text=f"Hôm nay bạn đã bán {day.order_count} đơn, thực thu {format_money(day.net)}.\n"
                     f"Tháng này: {month.order_count} đơn, thực thu {format_money(month.net)}.")