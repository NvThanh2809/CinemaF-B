"""Trang Lịch sử đơn hàng.

Người phụ trách: THÀNH VIÊN B.
"""
from ui.pages.base import Page
from ui.widgets import PageHeader


class OrdersPage(Page):
    """Chủ cửa hàng xem tất cả (lọc theo nhân viên); nhân viên chỉ thấy đơn của mình."""

    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        self._owner = ctx.auth.require_login().is_owner
        PageHeader(self, "Lịch sử đơn hàng",
                   "Tất cả đơn đã thanh toán" if self._owner else "Các đơn bạn đã bán").pack(fill="x")
        self.show_todo("B", [
            "Bộ lọc khoảng ngày: ui.widgets.DateRangeBar (có sẵn nút Hôm nay / 7 ngày / Tháng này...)",
            "Nếu là chủ cửa hàng: ô chọn nhân viên (lấy danh sách từ ctx.users.list_users() của C), mặc định 'Tất cả'",
            "Bảng đơn (DataTable): Số HĐ, Thời gian, Nhân viên, Tổng tiền, Giảm giá, Thực thu - nguồn ctx.orders.list_orders",
            "Dòng tổng kết dưới bảng (số đơn, tổng thực thu); cảnh báo nếu chạm giới hạn 500 đơn",
            "Nút / double-click 'Xem / in lại hóa đơn' -> ctx.orders.get_order -> InvoiceView",
        ])

    def on_show(self):
        """TODO (B): nạp lại danh sách đơn mỗi khi mở trang."""
