"""Quản lý tài khoản - chỉ chủ cửa hàng được dùng.
Mọi hàm đều bắt đầu bằng self._auth.require_owner() (quyền kiểm ở service, không chỉ ẩn nút trên UI).
"""
import re

from models.user import Role
from services.auth_service import validate_password
from utils.exceptions import ValidationError
from utils.security import hash_password

USERNAME_PATTERN = re.compile(r"^[a-z0-9_.]{3,30}$")


class UserService:
    def __init__(self, user_repo, auth):
        self._repo = user_repo
        self._auth = auth

    # đọc
    def list_users(self):
        self._auth.require_owner()
        counts = self._repo.order_counts()
        return [(user, counts.get(user.id, 0)) for user in self._repo.list_all()]

    # thêm
    def create(self, username, full_name, role, password):
        self._auth.require_owner()
        username = (username or "").strip().lower()
        full_name = (full_name or "").strip()
        if not USERNAME_PATTERN.match(username):
            raise ValidationError("Tên đăng nhập gồm 3-30 ký tự: chữ thường không dấu, số, dấu gạch dưới hoặc dấu chấm")
        if not full_name:
            raise ValidationError("Vui lòng nhập họ tên")
        self._check_role(role)
        validate_password(password)
        if self._repo.find_by_username(username) is not None:
            raise ValidationError(f"Tên đăng nhập '{username}' đã tồn tại")
        return self._repo.insert(username, hash_password(password), full_name, role)

    # sửa
    def update(self, user_id, full_name, role, active, new_password=None):
        """Sửa họ tên / vai trò / trạng thái; new_password (nếu có) thì đặt lại mật khẩu"""
        me = self._auth.require_owner()
        target = self._get(user_id)
        full_name = (full_name or "").strip()
        active = bool(active)
        if not full_name:
            raise ValidationError("Vui lòng nhập họ tên")
        self._check_role(role)
        if target.id == me.id and (role != Role.OWNER or not active):
            raise ValidationError("Bạn không thể tự hạ quyền hoặc tự khóa tài khoản đang đăng nhập")
        if self._is_last_active_owner(target) and (role != Role.OWNER or not active):
            raise ValidationError("Phải luôn còn ít nhất một chủ cửa hàng đang hoạt động")
        if new_password:  # kiểm tra xong mọi thứ rồi mới ghi để không bị lưu dở dang
            validate_password(new_password)
        self._repo.update(target.id, full_name, role, active)
        if new_password:
            self._repo.update_password(target.id, hash_password(new_password))

    # xóa
    def delete(self, user_id):
        """Trả 'deleted' (xóa hẳn) hoặc 'locked' (đã có đơn hàng nên chỉ khóa để doanh số cũ vẫn đúng)."""
        me = self._auth.require_owner()
        target = self._get(user_id)
        if target.id == me.id:
            raise ValidationError("Bạn không thể xóa tài khoản đang đăng nhập")
        if self._is_last_active_owner(target):
            raise ValidationError("Phải luôn còn ít nhất một chủ cửa hàng đang hoạt động")
        if self._repo.count_orders(target.id) > 0:
            self._repo.update(target.id, target.full_name, target.role, False)
            return "locked"
        self._repo.delete(target.id)
        return "deleted"

    # nội bộ
    def _get(self, user_id):
        user = self._repo.find_by_id(user_id)
        if user is None:
            raise ValidationError("Không tìm thấy tài khoản (có thể đã bị xóa)")
        return user

    @staticmethod
    def _check_role(role):
        if role not in (Role.OWNER, Role.STAFF):
            raise ValidationError("Vai trò không hợp lệ")

    def _is_last_active_owner(self, user):
        """True nếu `user` đang là chủ cửa hàng hoạt động và không còn chủ nào khác đang hoạt động."""
        return (user.role == Role.OWNER and user.active
                and self._repo.count_active_owners(exclude_id=user.id) == 0)