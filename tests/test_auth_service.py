"""Test cho AuthService (đăng nhập, phân quyền, đổi mật khẩu).

Người phụ trách: THÀNH VIÊN C.
Dùng Env(login_as=None) rồi gọi env.auth.login('admin', 'admin123') THẬT (đường tắt của Env chỉ dành cho test module khác).

Cách làm: mỗi test bên dưới là MỘT hành vi cần kiểm tra. Viết xong test nào thì xóa dòng @TODO của test đó
và thay phần mô tả bằng code kiểm tra thật. Chạy: python -m unittest discover -s tests -t .
"""
import unittest

from tests.helpers import Env

TODO = unittest.skip("TODO (C): chưa viết test này")


class AuthServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    @TODO
    def test_login_success_for_both_roles(self):
        """admin đăng nhập được với vai trò chủ cửa hàng, nhanvien với vai trò nhân viên; current_user được gán."""

    @TODO
    def test_wrong_credentials_give_same_generic_message(self):
        """Sai tên đăng nhập và sai mật khẩu cho CÙNG một thông báo (không lộ tài khoản có tồn tại)."""

    @TODO
    def test_empty_fields_rejected(self):
        """Tên hoặc mật khẩu trống ném AuthError."""

    @TODO
    def test_username_is_trimmed_and_case_insensitive(self):
        """'  ADMIN ' vẫn đăng nhập được."""

    @TODO
    def test_locked_account_cannot_login(self):
        """Tài khoản active = 0 không đăng nhập được."""

    @TODO
    def test_logout_clears_session_and_blocks_requires(self):
        """Sau logout, require_login và require_owner ném AuthError."""

    @TODO
    def test_staff_cannot_pass_owner_check(self):
        """Nhân viên gọi require_owner ném PermissionDenied."""

    @TODO
    def test_change_password(self):
        """Đổi mật khẩu: sai mật khẩu cũ bị từ chối, mật khẩu mới quá ngắn hoặc trùng mật khẩu cũ bị từ chối, đổi xong đăng nhập lại bằng mật khẩu mới được."""


if __name__ == "__main__":
    unittest.main()
