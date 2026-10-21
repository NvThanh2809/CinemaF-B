"""Hộp thoại thêm/sửa tài khoản và đổi mật khẩu.
Cả hai kế thừa ui.helpers.FormDialog: dựng form bằng self.add_field(...), viết collect() trả dict dữ liệu;
lỗi AppError do hàm `submit` ném ra sẽ tự hiện ngay trong hộp thoại.
"""
import tkinter as tk
from tkinter import ttk

from models.user import Role
from ui.helpers import FormDialog
from utils.exceptions import ValidationError

_LABEL_TO_ROLE = {label: role for role, label in Role.LABELS.items()}  # "Nhân viên" -> "STAFF"


class AccountDialog(FormDialog):
    """Thêm tài khoản (user=None) hoặc sửa tài khoản (truyền User). is_self=True: không cho đổi vai trò/khóa."""

    def __init__(self, master, submit, user=None, is_self=False):
        self._user = user
        self.submit_text = "Lưu thay đổi" if user else "Tạo tài khoản"
        super().__init__(master, "Sửa tài khoản" if user else "Thêm tài khoản", submit)
        editing = user is not None

        self._username = tk.StringVar(value=user.username if editing else "")
        self._full_name = tk.StringVar(value=user.full_name if editing else "")
        self._role = tk.StringVar(value=Role.label(user.role if editing else Role.STAFF))
        self._password = tk.StringVar()
        self._confirm = tk.StringVar()
        self._active = tk.BooleanVar(value=user.active if editing else True)

        username_entry = self.add_field(
            "Tên đăng nhập", lambda p: ttk.Entry(p, textvariable=self._username, width=30),
            hint="" if editing else "3-30 ký tự: chữ thường không dấu, số, _ hoặc .")
        if editing:
            username_entry.config(state="readonly")  # không cho đổi tên đăng nhập sau khi tạo
        name_entry = self.add_field("Họ tên", lambda p: ttk.Entry(p, textvariable=self._full_name))
        role_box = self.add_field("Vai trò", lambda p: ttk.Combobox(
            p, textvariable=self._role, values=list(Role.LABELS.values()), state="readonly"))
        pass_hint = "Để trống nếu không muốn đổi mật khẩu" if editing else "Ít nhất 6 ký tự"
        self.add_field("Mật khẩu" if not editing else "Mật khẩu mới",
                       lambda p: ttk.Entry(p, textvariable=self._password, show="•"), hint=pass_hint)
        self.add_field("Nhập lại mật khẩu", lambda p: ttk.Entry(p, textvariable=self._confirm, show="•"))
        if editing:
            self._active_check = self.add_field(
                "Trạng thái", lambda p: ttk.Checkbutton(p, text="Đang hoạt động",
                                                         variable=self._active))
        if is_self:  # tự hạ quyền hoặc tự khóa mình sẽ bị service từ chối, nên khóa luôn các ô này
            role_box.config(state="disabled")
            self._active_check.state(["disabled"])
            ttk.Label(self.body, text="Đây là tài khoản của bạn nên không đổi được vai trò hoặc trạng thái.",
                      style="CardMuted.TLabel", wraplength=360, justify="left").grid(
                row=self._row, column=0, columnspan=2, sticky="w", pady=(4, 0))
        (name_entry if editing else username_entry).focus_set()
        self.present()

    def collect(self):
        """{"username", "full_name", "role" (mã 'OWNER'/'STAFF'), "password", "active"}."""
        password, confirm = self._password.get(), self._confirm.get()
        if password != confirm:
            raise ValidationError("Hai lần nhập mật khẩu không khớp")
        return {
            "username": self._username.get(),
            "full_name": self._full_name.get(),
            "role": _LABEL_TO_ROLE.get(self._role.get()),
            "password": password,
            "active": self._active.get(),
        }


class ChangePasswordDialog(FormDialog):
    submit_text = "Đổi mật khẩu"

    def __init__(self, master, submit):
        super().__init__(master, "Đổi mật khẩu", submit)
        self._old, self._new, self._confirm = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self._entries = []

        def entry(var):
            def make(parent):
                e = ttk.Entry(parent, textvariable=var, show="•", width=30)
                self._entries.append(e)
                return e
            return make

        first = self.add_field("Mật khẩu hiện tại", entry(self._old))
        self.add_field("Mật khẩu mới", entry(self._new), hint="Ít nhất 6 ký tự và khác mật khẩu hiện tại")
        self.add_field("Nhập lại mật khẩu mới", entry(self._confirm))
        self._show = tk.BooleanVar(value=False)
        self.add_field("", lambda p: ttk.Checkbutton(p, text="Hiện mật khẩu", variable=self._show,
                                                      command=self._toggle))
        first.focus_set()
        self.present()

    def _toggle(self):
        for e in self._entries:
            e.config(show="" if self._show.get() else "•")

    def collect(self):
        """{"old": ..., "new": ...}; hai lần nhập mật khẩu mới không khớp thì ValidationError."""
        if self._new.get() != self._confirm.get():
            raise ValidationError("Hai lần nhập mật khẩu mới không khớp")
        return {"old": self._old.get(), "new": self._new.get()}