"""Test cho UserService + UserRepository (quản lý tài khoản, chỉ chủ cửa hàng).

Người phụ trách: THÀNH VIÊN C.
Env() đăng nhập sẵn chủ cửa hàng; env.login('nhanvien') để thử quyền nhân viên.
"""
import unittest

from models.user import Role
from tests.helpers import Env
from utils.exceptions import AuthError, PermissionDenied, ValidationError


class UserServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    def test_create_account_and_login_with_it(self):
        """Tạo tài khoản mới xong đăng nhập được bằng chính tài khoản đó."""
        user_id = self.env.users.create("thungan", "Thu Ngân", Role.STAFF, "password123")
        self.assertIsNotNone(user_id)
        self.env.auth.logout()
        user = self.env.auth.login("thungan", "password123")
        self.assertEqual(user.username, "thungan")
        self.assertEqual(user.full_name, "Thu Ngân")
        self.assertEqual(user.role, Role.STAFF)

    def test_create_validation(self):
        """Tên đăng nhập sai định dạng, trùng, họ tên rỗng, vai trò lạ, mật khẩu ngắn: mỗi trường hợp bị từ chối."""
        # Sai định dạng username (quá ngắn < 3, có ký tự đặc biệt)
        with self.assertRaises(ValidationError):
            self.env.users.create("ab", "Nguyen Van A", Role.STAFF, "pass123")
        with self.assertRaises(ValidationError):
            self.env.users.create("a@b", "Nguyen Van A", Role.STAFF, "pass123")
        # Trùng username
        with self.assertRaises(ValidationError):
            self.env.users.create("admin", "Chủ Mới", Role.OWNER, "pass123")
        # Họ tên rỗng
        with self.assertRaises(ValidationError):
            self.env.users.create("user_test", "   ", Role.STAFF, "pass123")
        # Vai trò lạ
        with self.assertRaises(ValidationError):
            self.env.users.create("user_test", "Nguyen Van B", "ADMINISTRATOR", "pass123")
        # Mật khẩu ngắn (< 6 ký tự)
        with self.assertRaises(ValidationError):
            self.env.users.create("user_test", "Nguyen Van B", Role.STAFF, "123")

    def test_update_profile_role_and_reset_password(self):
        """Sửa họ tên / vai trò / trạng thái và đặt lại mật khẩu thành công."""
        uid = self.env.users.create("nhanvien2", "NV Cũ", Role.STAFF, "pass123")
        self.env.users.update(uid, "NV Mới", Role.OWNER, False, "newpass456")
        updated = self.env.user_repo.find_by_id(uid)
        self.assertEqual(updated.full_name, "NV Mới")
        self.assertEqual(updated.role, Role.OWNER)
        self.assertFalse(updated.active)
        # Kiểm tra mật khẩu mới hoạt động (khi mở khóa)
        self.env.db.execute("UPDATE users SET active = 1 WHERE id = ?", (uid,))
        self.env.auth.logout()
        user = self.env.auth.login("nhanvien2", "newpass456")
        self.assertIsNotNone(user)

    def test_update_without_password_keeps_old_password(self):
        """Sửa mà không nhập mật khẩu mới thì mật khẩu cũ vẫn dùng được."""
        uid = self.env.users.create("nhanvien3", "NV 3", Role.STAFF, "pass123")
        self.env.users.update(uid, "NV 3 Đã Đổi Tên", Role.STAFF, True, None)
        self.env.auth.logout()
        user = self.env.auth.login("nhanvien3", "pass123")
        self.assertEqual(user.full_name, "NV 3 Đã Đổi Tên")

    def test_cannot_demote_or_lock_yourself(self):
        """Tự hạ quyền hoặc tự khóa tài khoản đang đăng nhập bị từ chối."""
        me = self.env.auth.current_user
        with self.assertRaises(ValidationError):
            self.env.users.update(me.id, me.full_name, Role.STAFF, True)
        with self.assertRaises(ValidationError):
            self.env.users.update(me.id, me.full_name, Role.OWNER, False)

    def test_always_keeps_one_active_owner(self):
        """Không thể hạ quyền, khóa hay xóa chủ cửa hàng cuối cùng."""
        admin = self.env.auth.current_user
        with self.assertRaises(ValidationError):
            self.env.users.update(admin.id, admin.full_name, Role.STAFF, True)
        with self.assertRaises(ValidationError):
            self.env.users.delete(admin.id)

        owner2_id = self.env.users.create("owner2", "Chủ 2", Role.OWNER, "pass123")
        self.env.users.update(owner2_id, "Chủ 2", Role.OWNER, False)
        with self.assertRaises(ValidationError):
            self.env.users.update(admin.id, admin.full_name, Role.STAFF, True)

    def test_delete_unused_account_removes_row(self):
        """Tài khoản chưa bán gì: delete trả 'deleted' và dòng bị xóa hẳn."""
        uid = self.env.users.create("nhanvien_tam", "NV Tạm", Role.STAFF, "pass123")
        res = self.env.users.delete(uid)
        self.assertEqual(res, "deleted")
        self.assertIsNone(self.env.user_repo.find_by_id(uid))

    def test_delete_account_with_orders_only_locks_and_keeps_history(self):
        """Tài khoản đã có đơn: delete trả 'locked', chỉ bị khóa, đơn cũ vẫn còn."""
        staff = self.env.user_repo.find_by_username("nhanvien")
        self.env.db.insert("orders", {
            "created_at": "2026-10-10 10:00:00",
            "user_id": staff.id,
            "total_amount": 50000,
            "discount_amount": 0,
            "final_amount": 50000,
        })
        res = self.env.users.delete(staff.id)
        self.assertEqual(res, "locked")
        locked_user = self.env.user_repo.find_by_id(staff.id)
        self.assertIsNotNone(locked_user)
        self.assertFalse(locked_user.active)

    def test_cannot_delete_yourself(self):
        """Tự xóa tài khoản đang đăng nhập bị từ chối."""
        me = self.env.auth.current_user
        with self.assertRaises(ValidationError):
            self.env.users.delete(me.id)

    def test_staff_cannot_manage_accounts(self):
        """Nhân viên gọi bất kỳ hàm nào cũng bị PermissionDenied."""
        self.env.login("nhanvien")
        with self.assertRaises(PermissionDenied):
            self.env.users.list_users()
        with self.assertRaises(PermissionDenied):
            self.env.users.create("user_test", "NV Test", Role.STAFF, "pass123")
        with self.assertRaises(PermissionDenied):
            self.env.users.update(1, "Ten", Role.STAFF, True)
        with self.assertRaises(PermissionDenied):
            self.env.users.delete(1)

    def test_not_logged_in_is_rejected(self):
        """Chưa đăng nhập gọi hàm nào cũng bị AuthError."""
        self.env.auth.logout()
        with self.assertRaises(AuthError):
            self.env.users.list_users()
        with self.assertRaises(AuthError):
            self.env.users.create("user_test", "NV Test", Role.STAFF, "pass123")
        with self.assertRaises(AuthError):
            self.env.users.update(1, "Ten", Role.STAFF, True)
        with self.assertRaises(AuthError):
            self.env.users.delete(1)

    def test_list_users_includes_order_counts(self):
        """list_users trả về (User, số đơn đã lập) đúng cho từng người."""
        staff = self.env.user_repo.find_by_username("nhanvien")
        self.env.db.insert("orders", {
            "created_at": "2026-10-10 10:00:00",
            "user_id": staff.id,
            "total_amount": 50000,
            "discount_amount": 0,
            "final_amount": 50000,
        })
        self.env.db.insert("orders", {
            "created_at": "2026-10-10 11:00:00",
            "user_id": staff.id,
            "total_amount": 30000,
            "discount_amount": 0,
            "final_amount": 30000,
        })
        user_list = self.env.users.list_users()
        counts_by_username = {u.username: count for u, count in user_list}
        self.assertEqual(counts_by_username["nhanvien"], 2)
        self.assertEqual(counts_by_username["admin"], 0)


if __name__ == "__main__":
    unittest.main()
