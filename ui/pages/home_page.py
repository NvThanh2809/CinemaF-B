"""Trang Tổng quan (dashboard mở đầu).

Người phụ trách: THÀNH VIÊN C.
"""
from ui.pages.base import Page
from ui.widgets import PageHeader


class HomePage(Page):
    """Chủ cửa hàng thấy số liệu cả cửa hàng, nhân viên thấy số liệu của chính mình."""

    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        self._me = ctx.auth.require_login()
        PageHeader(self, f"Xin chào, {self._me.full_name}", f"Tổng quan hoạt động - {self._me.role_label}").pack(fill="x")
        self.show_todo("C", [
            "4 thẻ StatCard: Doanh thu hôm nay, Số đơn hôm nay, Doanh thu tháng này, Giá trị đơn trung bình (tháng)",
            "Biểu đồ BarChart doanh thu 14 ngày gần nhất - nguồn ctx.reports.series(..., 'day')",
            "Chủ cửa hàng: bảng 'Nhân viên nổi bật tháng này' (ctx.reports.by_staff) và nút 'Xem báo cáo chi tiết' -> self.shell.navigate('reports')",
            "Nhân viên: chỉ hiện số liệu của chính mình (ctx.reports.my_summary)",
        ])

    def on_show(self):
        """TODO (C): nạp lại số liệu mỗi khi mở trang."""
