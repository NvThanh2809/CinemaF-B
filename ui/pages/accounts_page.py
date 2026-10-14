"""Trang Quản lý tài khoản (chỉ chủ cửa hàng).

Người phụ trách: THÀNH VIÊN C.
"""
from ui.pages.base import Page
from ui.widgets import PageHeader


class AccountsPage(Page):
    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        self._me = ctx.auth.require_owner()
        PageHeader(self, "Quản lý tài khoản", "Cấp tài khoản và phân quyền cho nhân viên").pack(fill="x")
        self.show_todo("C", [
            "Bảng tài khoản (DataTable): Tên đăng nhập, Họ tên, Vai trò, Trạng thái, Số đơn đã bán, Ngày tạo - nguồn ctx.users.list_users()",
            "Ô tìm kiếm lọc theo tên đăng nhập / họ tên",
            "Nút Thêm / Sửa / Xóa -> AccountDialog (file ui/account_dialogs.py) -> ctx.users.create / update / delete",
            "Xóa: hỏi xác nhận; nếu trả 'locked' thì báo 'tài khoản đã có đơn hàng nên chỉ bị khóa'",
            "Đánh dấu tài khoản đang đăng nhập; sửa chính mình thì gọi self.shell.refresh_user()",
        ])

    def on_show(self):
        """TODO (C): nạp lại danh sách tài khoản."""
