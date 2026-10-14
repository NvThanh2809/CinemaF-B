"""Test cho UserService + UserRepository (quản lý tài khoản, chỉ chủ cửa hàng).

Người phụ trách: THÀNH VIÊN C.
Env() đăng nhập sẵn chủ cửa hàng; env.login('nhanvien') để thử quyền nhân viên.

Cách làm: mỗi test bên dưới là MỘT hành vi cần kiểm tra. Viết xong test nào thì xóa dòng @TODO của test đó
và thay phần mô tả bằng code kiểm tra thật. Chạy: python -m unittest discover -s tests -t .
"""
import unittest

from tests.helpers import Env

TODO = unittest.skip("TODO (C): chưa viết test này")


class UserServiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    @TODO
    def test_create_account_and_login_with_it(self):
        """Tạo tài khoản mới xong đăng nhập được bằng chính tài khoản đó."""

    @TODO
    def test_create_validation(self):
        """Tên đăng nhập sai định dạng, trùng, họ tên rỗng, vai trò lạ, mật khẩu ngắn: mỗi trường hợp bị từ chối."""

    @TODO
    def test_update_profile_role_and_reset_password(self):
        """Sửa họ tên / vai trò / trạng thái và đặt lại mật khẩu thành công."""

    @TODO
    def test_update_without_password_keeps_old_password(self):
        """Sửa mà không nhập mật khẩu mới thì mật khẩu cũ vẫn dùng được."""

    @TODO
    def test_cannot_demote_or_lock_yourself(self):
        """Tự hạ quyền hoặc tự khóa tài khoản đang đăng nhập bị từ chối."""

    @TODO
    def test_always_keeps_one_active_owner(self):
        """Không thể hạ quyền, khóa hay xóa chủ cửa hàng cuối cùng."""

    @TODO
    def test_delete_unused_account_removes_row(self):
        """Tài khoản chưa bán gì: delete trả 'deleted' và dòng bị xóa hẳn."""

    @TODO
    def test_delete_account_with_orders_only_locks_and_keeps_history(self):
        """Tài khoản đã có đơn: delete trả 'locked', chỉ bị khóa, đơn cũ vẫn còn."""

    @TODO
    def test_cannot_delete_yourself(self):
        """Tự xóa tài khoản đang đăng nhập bị từ chối."""

    @TODO
    def test_staff_cannot_manage_accounts(self):
        """Nhân viên gọi bất kỳ hàm nào cũng bị PermissionDenied."""

    @TODO
    def test_not_logged_in_is_rejected(self):
        """Chưa đăng nhập gọi hàm nào cũng bị AuthError."""

    @TODO
    def test_list_users_includes_order_counts(self):
        """list_users trả về (User, số đơn đã lập) đúng cho từng người."""


if __name__ == "__main__":
    unittest.main()
