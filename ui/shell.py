"""Khung chính sau khi đăng nhập: thanh điều hướng (dashboard) bên trái + vùng nội dung bên phải."""
import tkinter as tk
from tkinter import messagebox, ttk

from models.user import Role
from ui.account_dialogs import ChangePasswordDialog
from ui.pages.accounts_page import AccountsPage
from ui.pages.home_page import HomePage
from ui.pages.orders_page import OrdersPage
from ui.pages.reports_page import ReportsPage
from ui.pages.sales_page import SalesPage
from ui.theme import C, F_BOLD, F_SMALL, FONT
from utils.exceptions import AppError

# (khóa, nhãn, lớp trang, vai trò yêu cầu hoặc None = ai cũng dùng được)
NAV_MAIN = [
    ("home", "Tổng quan", HomePage, None),
    ("sales", "Bán hàng", SalesPage, None),
    ("orders", "Lịch sử đơn hàng", OrdersPage, None),
]
NAV_ADMIN = [
    ("reports", "Doanh số", ReportsPage, Role.OWNER),
    ("accounts", "Quản lý tài khoản", AccountsPage, Role.OWNER),
]


class NavButton(tk.Frame):
    """Mục điều hướng: vạch màu bên trái khi đang chọn, đổi nền khi rê chuột."""

    def __init__(self, master, text, command):
        super().__init__(master, bg=C["sidebar"], cursor="hand2")
        self._command = command
        self._active = False
        self._bar = tk.Frame(self, bg=C["sidebar"], width=4)
        self._bar.pack(side="left", fill="y")
        self._label = tk.Label(self, text=text, bg=C["sidebar"], fg=C["sidebar_text"], font=(FONT, 11),
                               anchor="w", padx=18, pady=11, cursor="hand2")
        self._label.pack(side="left", fill="x", expand=True)
        for w in (self, self._label, self._bar):
            w.bind("<Button-1>", lambda e: self._command())
            w.bind("<Enter>", lambda e: self._paint(hover=True))
            w.bind("<Leave>", lambda e: self._paint(hover=False))

    def set_active(self, active):
        self._active = active
        self._paint()

    def _paint(self, hover=False):
        bg = C["sidebar_hover"] if (self._active or hover) else C["sidebar"]
        self.config(bg=bg)
        self._label.config(bg=bg, fg="white" if self._active else C["sidebar_text"],
                           font=(FONT, 11, "bold") if self._active else (FONT, 11))
        self._bar.config(bg=C["primary"] if self._active else bg)


class Shell(tk.Frame):
    def __init__(self, master, ctx, on_logout):
        super().__init__(master, bg=C["bg"])
        self.ctx = ctx
        self._on_logout = on_logout
        self._user = ctx.auth.require_login()
        self._buttons = {}
        self._factories = {}
        self._pages = {}
        self._current = None

        self.sidebar = tk.Frame(self, bg=C["sidebar"], width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.content = ttk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)

        self._build_sidebar()
        self.navigate("home")

    # ------------------------------------------------------------ sidebar
    def _build_sidebar(self):
        brand = tk.Frame(self.sidebar, bg=C["sidebar"])
        brand.pack(fill="x", padx=18, pady=(22, 18))
        logo = tk.Canvas(brand, width=38, height=38, bg=C["sidebar"], highlightthickness=0)
        logo.create_oval(1, 1, 37, 37, fill=C["primary"], outline="")
        logo.create_polygon(15, 11, 15, 27, 28, 19, fill="white", outline="")
        logo.pack(side="left")
        names = tk.Frame(brand, bg=C["sidebar"])
        names.pack(side="left", padx=10)
        tk.Label(names, text="CINEMA F&B", bg=C["sidebar"], fg="white", font=(FONT, 13, "bold")).pack(anchor="w")
        tk.Label(names, text="Bán hàng tại quầy", bg=C["sidebar"], fg=C["sidebar_muted"], font=F_SMALL).pack(anchor="w")

        self._section("CHỨC NĂNG")
        for entry in NAV_MAIN:
            self._add_nav(*entry)
        if self._user.is_owner:
            self._section("QUẢN TRỊ")
            for entry in NAV_ADMIN:
                self._add_nav(*entry)

        # Khối người dùng ở đáy
        bottom = tk.Frame(self.sidebar, bg=C["sidebar"])
        bottom.pack(side="bottom", fill="x")
        tk.Frame(bottom, bg=C["sidebar_line"], height=1).pack(fill="x")
        info = tk.Frame(bottom, bg=C["sidebar"])
        info.pack(fill="x", padx=18, pady=(14, 8))
        initial = (self._user.full_name.strip()[:1] or "?").upper()
        avatar = tk.Canvas(info, width=38, height=38, bg=C["sidebar"], highlightthickness=0)
        avatar.create_oval(1, 1, 37, 37, fill=C["avatar"], outline="")
        avatar.create_text(19, 19, text=initial, fill="white", font=(FONT, 13, "bold"))
        avatar.pack(side="left")
        text = tk.Frame(info, bg=C["sidebar"])
        text.pack(side="left", padx=10, fill="x", expand=True)
        self._name_label = tk.Label(text, text=self._user.full_name, bg=C["sidebar"], fg="white",
                                    font=F_BOLD, anchor="w")
        self._name_label.pack(fill="x")
        tk.Label(text, text=self._user.role_label, bg=C["sidebar"],
                 fg=C["primary_soft"] if self._user.is_owner else C["sidebar_muted"],
                 font=F_SMALL, anchor="w").pack(fill="x")
        for label, command in (("Đổi mật khẩu", self._change_password), ("Đăng xuất", self._logout)):
            NavButton(bottom, label, command).pack(fill="x")
        tk.Frame(bottom, bg=C["sidebar"], height=8).pack()

    def _section(self, title):
        tk.Label(self.sidebar, text=title, bg=C["sidebar"], fg=C["sidebar_muted"], font=(FONT, 8, "bold"),
                 anchor="w").pack(fill="x", padx=22, pady=(14, 4))

    def _add_nav(self, key, label, page_cls, role):
        if role is not None and self._user.role != role:
            return
        button = NavButton(self.sidebar, label, lambda k=key: self.navigate(k))
        button.pack(fill="x")
        self._buttons[key] = button
        self._factories[key] = page_cls

    # --------------------------------------------------------- điều hướng
    def navigate(self, key):
        if key not in self._factories:
            return
        if self._current is not None:
            self._pages[self._current].pack_forget()
            self._buttons[self._current].set_active(False)
        if key not in self._pages:  # tạo trang lần đầu cần dùng, giữ lại để không mất dữ liệu đang nhập
            self._pages[key] = self._factories[key](self.content, self.ctx, self)
        self._current = key
        self._buttons[key].set_active(True)
        self._pages[key].pack(fill="both", expand=True)
        self._pages[key].on_show()

    def refresh_user(self):
        """Cập nhật tên hiển thị ở thanh bên sau khi sửa thông tin tài khoản đang đăng nhập."""
        self._name_label.config(text=self._user.full_name)

    # ------------------------------------------------------ tài khoản của tôi
    def _change_password(self):
        def submit(data):
            self.ctx.auth.change_password(data["old"], data["new"])

        dialog = ChangePasswordDialog(self, submit)
        self.wait_window(dialog)
        if dialog.saved:
            messagebox.showinfo("Đổi mật khẩu", "Đã đổi mật khẩu thành công.", parent=self)

    def _logout(self):
        sales = self._pages.get("sales")
        warning = "\n\nĐơn hàng đang lập chưa thanh toán sẽ bị hủy." if sales and sales.has_unsaved_work() else ""
        if messagebox.askyesno("Đăng xuất", "Bạn muốn đăng xuất khỏi hệ thống?" + warning, parent=self):
            self._on_logout()
