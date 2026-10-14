"""Trang Doanh số (chỉ chủ cửa hàng).

Người phụ trách: THÀNH VIÊN C.
"""
from ui.pages.base import Page
from ui.widgets import PageHeader


class ReportsPage(Page):
    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        self._me = ctx.auth.require_owner()
        PageHeader(self, "Doanh số", "Thống kê doanh thu theo thời gian và theo từng nhân viên").pack(fill="x")
        self.show_todo("C", [
            "Dùng ttk.Notebook với 2 tab: 'Theo thời gian' và 'So sánh nhân viên'",
            "Tab 1: ô chọn đối tượng (Toàn cửa hàng / từng nhân viên), chọn Theo ngày | Theo tháng, DateRangeBar",
            "Tab 1: 4 thẻ StatCard (Số đơn, Tổng tiền hàng, Giảm giá đã dùng, Doanh thu thực thu) - nguồn ctx.reports.summary",
            "Tab 1: biểu đồ ui.widgets.BarChart + bảng chi tiết từng ngày/tháng - nguồn ctx.reports.series",
            "Tab 2: bảng xếp hạng nhân viên theo doanh thu - nguồn ctx.reports.by_staff; double-click một người để xem chi tiết ở tab 1",
        ])

    def on_show(self):
        """TODO (C): nạp lại danh sách nhân viên và số liệu."""
