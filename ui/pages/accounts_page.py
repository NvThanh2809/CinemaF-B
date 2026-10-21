"""Trang Quản lý tài khoản (chỉ chủ cửa hàng).
Trang chỉ lo hiển thị và gọi ctx.users (UserService). Mọi luật nghiệp vụ nằm ở service; lỗi AppError
mà service ném ra sẽ được ui/app.py hiện thành hộp thoại cảnh báo (xem App._on_callback_error).
"""
import tkinter as tk
from tkinter import messagebox, ttk

from ui.account_dialogs import AccountDialog
from ui.pages.base import Page
from ui.widgets import Card, DataTable, PageHeader
from utils.dates import format_date, to_datetime
from utils.text import normalize

COLUMNS = [
    ("username", "Tên đăng nhập", 150, "w"),
    ("full_name", "Họ tên", 210, "w"),
    ("role", "Vai trò", 120, "w"),
    ("status", "Trạng thái", 110, "w"),
    ("orders", "Số đơn đã bán", 110, "e"),
    ("created", "Ngày tạo", 110, "center"),
]


class AccountsPage(Page):
    def __init__(self, master, ctx, shell):
        super().__init__(master, ctx, shell)
        self._me = ctx.auth.require_owner()
        self._rows = []  # [(User, số đơn)] lần tải gần nhất

        header = PageHeader(self, "Quản lý tài khoản", "Cấp tài khoản và phân quyền người dùng")
        header.pack(fill="x")
        ttk.Button(header.actions, text="+  Thêm tài khoản", style="Primary.TButton",
                   command=self._add).pack()

        card = Card(self, padding=(18, 16))
        card.pack(fill="both", expand=True, pady=(16, 0))
        bar = ttk.Frame(card.inner, style="Card.TFrame")
        bar.pack(fill="x", pady=(0, 12))
        ttk.Label(bar, text="Tìm kiếm", style="Card.TLabel").pack(side="left")
        self._search = tk.StringVar()
        self._search.trace_add("write", lambda *_: self._render())
        ttk.Entry(bar, textvariable=self._search, width=28).pack(side="left", padx=(8, 0))
        self._count = ttk.Label(bar, text="", style="CardMuted.TLabel")
        self._count.pack(side="left", padx=14)
        self._btn_delete = ttk.Button(bar, text="Xóa", style="Danger.TButton", command=self._delete)
        self._btn_delete.pack(side="right")
        self._btn_edit = ttk.Button(bar, text="Sửa", command=self._edit)
        self._btn_edit.pack(side="right", padx=(0, 8))

        self._table = DataTable(card.inner, COLUMNS, height=12)
        self._table.pack(fill="both", expand=True)
        self._table.tree.bind("<<TreeviewSelect>>", lambda e: self._update_buttons())
        self._table.tree.bind("<Double-1>", lambda e: self._edit())
        self._update_buttons()

    def on_show(self):
        self._reload()

    # dữ liệu
    def _reload(self):
        self._rows = self.ctx.users.list_users()
        self._render()

    def _render(self):
        keyword = normalize(self._search.get())
        selected = self._table.selected()
        self._table.clear()
        shown = 0
        for user, orders in self._rows:
            if keyword and keyword not in normalize(f"{user.username} {user.full_name}"):
                continue
            name = user.username + ("  (bạn)" if user.id == self._me.id else "")
            created = to_datetime(user.created_at)
            self._table.add(
                (name, user.full_name, user.role_label, "Hoạt động" if user.active else "Đã khóa",
                 orders, format_date(created) if created else ""),
                iid=str(user.id), tags=() if user.active else ("muted",))
            shown += 1
        self._count.config(text=f"{shown}/{len(self._rows)} tài khoản")
        if selected and self._table.tree.exists(selected):
            self._table.tree.selection_set(selected)
        self._update_buttons()

    def _selected_user(self):
        iid = self._table.selected()
        if iid is None:
            return None
        return next((u for u, _ in self._rows if str(u.id) == iid), None)

    def _update_buttons(self):
        user = self._selected_user()
        self._btn_edit.state(["!disabled"] if user else ["disabled"])
        # Không cho bấm xóa chính mình (service cũng từ chối, đây chỉ để giao diện rõ ràng hơn)
        can_delete = user is not None and user.id != self._me.id
        self._btn_delete.state(["!disabled"] if can_delete else ["disabled"])

    # ---------------------------------------------------------------- thao tác
    def _add(self):
        def submit(data):
            self.ctx.users.create(data["username"], data["full_name"], data["role"], data["password"])

        dialog = AccountDialog(self, submit)
        self.wait_window(dialog)
        if dialog.saved:
            self._reload()

    def _edit(self):
        user = self._selected_user()
        if user is None:
            return
        is_self = user.id == self._me.id

        def submit(data):
            self.ctx.users.update(user.id, data["full_name"], data["role"], data["active"],
                                  new_password=data["password"] or None)
            if is_self:  # self._me chính là đối tượng phiên đăng nhập, cập nhật để thanh bên hiện tên mới
                self._me.full_name = data["full_name"].strip()

        dialog = AccountDialog(self, submit, user=user, is_self=is_self)
        self.wait_window(dialog)
        if dialog.saved:
            if is_self:
                self.shell.refresh_user()
            self._reload()

    def _delete(self):
        user = self._selected_user()
        if user is None:
            return
        if not messagebox.askyesno("Xóa tài khoản", f"Xóa tài khoản '{user.username}' ({user.full_name})?",
                                   icon="warning", parent=self):
            return
        result = self.ctx.users.delete(user.id)
        if result == "locked":
            messagebox.showinfo("Đã khóa tài khoản",
                                "Tài khoản này đã có đơn hàng nên chỉ bị khóa (không xóa hẳn) "
                                "để doanh số cũ vẫn đúng.", parent=self)
        self._reload()