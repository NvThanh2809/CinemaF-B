"""Test cho AuthService (đăng nhập, phân quyền, đổi mật khẩu).

Người phụ trách: THÀNH VIÊN C.
Dùng Env(login_as=None) rồi gọi env.auth.login('admin', 'admin123') THẬT (đường tắt của Env chỉ dành cho test module khác).
"""
import unittest

from tests.helpers import Env
from utils.exceptions import AuthError, PermissionDenied, ValidationError


class AuthServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env(login_as=None)

    def tearDown(self):
        self.env.close()

    def test_login_success_for_both_roles(self):
        """admin đăng nhập được với vai trò chủ cửa hàng, nhanvien với vai trò nhân viên; current_user được gán."""
        user_admin = self.env.auth.login("admin", "admin123")
        self.assertTrue(user_admin.is_owner)
        self.assertEqual(self.env.auth.current_user.username, "admin")

        self.env.auth.logout()
        self.assertIsNone(self.env.auth.current_user)

        user_staff = self.env.auth.login("nhanvien", "nv123456")
        self.assertFalse(user_staff.is_owner)
        self.assertEqual(self.env.auth.current_user.username, "nhanvien")

    def test_wrong_credentials_give_same_generic_message(self):
        """Sai tên đăng nhập và sai mật khẩu cho CÙNG một thông báo (không lộ tài khoản có tồn tại)."""
        with self.assertRaises(AuthError) as err1:
            self.env.auth.login("khong_ton_tai", "matkhau123")
        with self.assertRaises(AuthError) as err2:
            self.env.auth.login("admin", "sai_mat_khau")
        self.assertEqual(str(err1.exception), str(err2.exception))

    def test_empty_fields_rejected(self):
        """Tên hoặc mật khẩu trống ném AuthError."""
        for u, p in [("", "admin123"), ("   ", "admin123"), ("admin", ""), ("admin", "   ")]:
            with self.assertRaises(AuthError):
                self.env.auth.login(u, p)

    def test_username_is_trimmed_and_case_insensitive(self):
        """'  ADMIN ' vẫn đăng nhập được."""
        user = self.env.auth.login("  ADMIN  ", "admin123")
        self.assertEqual(user.username, "admin")

    def test_locked_account_cannot_login(self):
        """Tài khoản active = 0 không đăng nhập được."""
        self.env.db.execute("UPDATE users SET active = 0 WHERE username = 'nhanvien'")
        with self.assertRaises(AuthError) as err:
            self.env.auth.login("nhanvien", "nv123456")
        self.assertIn("khóa", str(err.exception))

    def test_logout_clears_session_and_blocks_requires(self):
        """Sau logout, require_login và require_owner ném AuthError."""
        self.env.auth.login("admin", "admin123")
        self.env.auth.logout()
        self.assertIsNone(self.env.auth.current_user)
        with self.assertRaises(AuthError):
            self.env.auth.require_login()
        with self.assertRaises(AuthError):
            self.env.auth.require_owner()

    def test_staff_cannot_pass_owner_check(self):
        """Nhân viên gọi require_owner ném PermissionDenied."""
        self.env.auth.login("nhanvien", "nv123456")
        with self.assertRaises(PermissionDenied):
            self.env.auth.require_owner()

    def test_change_password(self):
        """Đổi mật khẩu: sai mật khẩu cũ bị từ chối, mật khẩu mới quá ngắn hoặc trùng mật khẩu cũ bị từ chối, đổi xong đăng nhập lại bằng mật khẩu mới được."""
        self.env.auth.login("admin", "admin123")
        # Sai mk cũ
        with self.assertRaises(AuthError):
            self.env.auth.change_password("sai_mat_khau", "newpass123")
        # Trùng mk cũ
        with self.assertRaises(ValidationError):
            self.env.auth.change_password("admin123", "admin123")
        # Quá ngắn
        with self.assertRaises(ValidationError):
            self.env.auth.change_password("admin123", "123")
        # Đổi thành công
        self.env.auth.change_password("admin123", "newpass123")
        self.env.auth.logout()
        new_user = self.env.auth.login("admin", "newpass123")
        self.assertIsNotNone(new_user)


if __name__ == "__main__":
    unittest.main()
