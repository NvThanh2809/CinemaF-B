"""Trang Bán hàng.

Người phụ trách: THÀNH VIÊN B (gọi hộp thoại của A: ProductSearchDialog, VariantDialog).
"""
from ui.pages.base import Page
from ui.widgets import PageHeader


class SalesPage(Page):
    """Tìm mặt hàng -> chọn size/số lượng -> hóa đơn tạm -> mã ưu đãi -> thanh toán."""

    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        PageHeader(self, "Bán hàng", "Lập đơn cho khách").pack(fill="x")
        self.show_todo("B", [
            "Ô tìm kiếm + nút Tìm: ctx.products.search(từ khóa) -> mở ProductSearchDialog (của A)",
            "Chọn mặt hàng -> VariantDialog (của A) trả OrderDetail -> CartService.add_item",
            "Bảng hóa đơn tạm (ui.widgets.DataTable): Mã, Tên, Kích cỡ, Đơn giá, Số lượng, Thành tiền; dòng cuối là TỔNG TIỀN",
            "Nút Sửa số lượng / Xóa dòng / Hủy đơn",
            "Ô chọn mã ưu đãi (chỉ 1 mã/đơn): ctx.discounts.get_applicable + CartService.apply_discount; hiện lý do khi bị từ chối",
            "Khu thanh toán: Tổng tiền hàng, Giảm giá, Khách cần trả; nút THANH TOÁN -> ctx.orders.checkout(cart) -> InvoiceView",
            "has_unsaved_work() trả True khi giỏ còn hàng (Shell dùng để cảnh báo khi đăng xuất)",
        ])

    def on_show(self):
        """TODO (B): đặt con trỏ vào ô tìm kiếm, nạp lại danh sách mã ưu đãi."""

    def has_unsaved_work(self):
        """TODO (B): True khi hóa đơn tạm còn mặt hàng chưa thanh toán."""
        return False
