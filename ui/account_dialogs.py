"""Hộp thoại thêm/sửa tài khoản và đổi mật khẩu.

Người phụ trách: THÀNH VIÊN C.
Cả hai kế thừa ui.helpers.FormDialog: dựng form bằng self.add_field(...), viết collect() trả dict dữ liệu;
lỗi AppError do hàm `submit` ném ra sẽ tự hiện ngay trong hộp thoại.
"""
from tkinter import ttk

from ui.helpers import FormDialog


class AccountDialog(FormDialog):
    """Thêm tài khoản (user=None) hoặc sửa tài khoản (truyền User). is_self=True: không cho đổi vai trò/khóa."""

    def __init__(self, master, submit, user=None, is_self=False):
        self._user = user
        self.submit_text = "Lưu thay đổi" if user else "Tạo tài khoản"
        super().__init__(master, "Sửa tài khoản" if user else "Thêm tài khoản", submit)
        ttk.Label(self.body, text="TODO (C): form tài khoản", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        # TODO (C): các trường: Tên đăng nhập (khóa lại khi sửa), Họ tên, Vai trò (Combobox, giá trị ui lấy từ
        #           models.user.Role.LABELS), Mật khẩu + Nhập lại (khi sửa: để trống = không đổi),
        #           Trạng thái (Checkbutton, chỉ khi sửa). Dùng self.add_field("Nhãn", lambda p: widget).
        self.present()

    def collect(self):
        """TODO (C): trả về {"username", "full_name", "role" (mã 'OWNER'/'STAFF'), "password", "active"};
        hai lần nhập mật khẩu không khớp thì ném ValidationError."""
        raise NotImplementedError("TODO (C): AccountDialog.collect")


class ChangePasswordDialog(FormDialog):
    submit_text = "Đổi mật khẩu"

    def __init__(self, master, submit):
        super().__init__(master, "Đổi mật khẩu", submit)
        ttk.Label(self.body, text="TODO (C): form đổi mật khẩu", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        # TODO (C): 3 ô mật khẩu (hiện/ẩn bằng show="•"): hiện tại, mới, nhập lại mới
        self.present()

    def collect(self):
        """TODO (C): trả về {"old": ..., "new": ...}; hai lần nhập mật khẩu mới không khớp thì ValidationError."""
        raise NotImplementedError("TODO (C): ChangePasswordDialog.collect")
