"""Điều phối cửa sổ chính: màn hình đăng nhập <-> khung dashboard."""
import traceback
from tkinter import messagebox

import config
from app_context import DevLoginAuth, dev_login_mode, start_dev_session
from config import APP_TITLE
from ui.helpers import center_window
from ui.login_view import LoginView
from ui.shell import Shell
from ui.theme import setup_styles
from utils.exceptions import AppError


class App:
    def __init__(self, root, ctx):
        self.root = root
        self.ctx = ctx
        self._view = None
        root.title(APP_TITLE)
        root.report_callback_exception = self._on_callback_error
        setup_styles(root)
        if start_dev_session(ctx):  # config.DEV_LOGIN: vào thẳng dashboard, bỏ qua đăng nhập
            self.show_shell()
        else:
            self.show_login()

    def _swap(self, view, width, height, minsize):
        if self._view is not None:
            self._view.destroy()
        self.root.minsize(*minsize)
        center_window(self.root, width, height)
        self._view = view
        view.pack(fill="both", expand=True)

    def show_login(self):
        self.ctx.auth.logout()
        if dev_login_mode() == "ANY":  # đăng nhập thử: gõ tên nào cũng vào, chưa kiểm tra tài khoản
            auth = DevLoginAuth(self.ctx)
            hint = ("Chế độ đăng nhập thử: gõ tên bất kỳ, mật khẩu để trống cũng được. "
                    f"Tên \"{config.DEFAULT_OWNER['username']}\" vào với quyền chủ cửa hàng, tên khác là nhân viên.")
        else:
            auth, hint = self.ctx.auth, ""
        self._swap(LoginView(self.root, auth, on_success=lambda user: self.show_shell(), hint=hint),
                   900, 560, (820, 520))

    def show_shell(self):
        self._swap(Shell(self.root, self.ctx, on_logout=self.show_login), 1320, 800, (1180, 720))

    # Mọi lỗi xảy ra trong lúc bấm nút / mở trang đều đi qua đây thay vì chỉ in ra terminal.
    def _on_callback_error(self, exc_type, exc, tb):
        if issubclass(exc_type, NotImplementedError):
            messagebox.showinfo("Chức năng chưa được code", str(exc) or "Chức năng này chưa được code.",
                                parent=self.root)
        elif issubclass(exc_type, AppError):
            messagebox.showwarning("Thông báo", str(exc), parent=self.root)
        else:
            traceback.print_exception(exc_type, exc, tb)
            messagebox.showerror("Lỗi chưa xử lý", f"{exc_type.__name__}: {exc}\n\n(Chi tiết ở cửa sổ terminal)",
                                 parent=self.root)
