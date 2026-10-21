"""Đăng nhập / đăng xuất và kiểm tra quyền của người đang đăng nhập.

Người phụ trách: THÀNH VIÊN C.

PHẦN ĐÃ LÀM SẴN (hợp đồng chung: module A, B, C đều gọi, nên phải chạy được ngay từ đầu):
    current_user, logout, require_login, require_owner, set_current_user (dùng cho chế độ dev)
PHẦN C CẦN LÀM: login, change_password.
"""
from models.user import Role
from utils.exceptions import AuthError, PermissionDenied, ValidationError  # noqa: F401
from utils.security import hash_password, verify_password  # noqa: F401

MIN_PASSWORD_LENGTH = 6


def validate_password(password):
    if len(password or "") < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Mật khẩu phải có ít nhất {MIN_PASSWORD_LENGTH} ký tự")


class AuthService:
    def __init__(self, user_repo):
        self._repo = user_repo
        self._current = None

    # ---- phiên đăng nhập (đã làm sẵn) ----
    @property
    def current_user(self):
        return self._current

    def set_current_user(self, user):
        """Chỉ dùng cho chế độ dev (config.DEV_LOGIN) và tests. Đăng nhập thật phải đi qua login()."""
        self._current = user

    def logout(self):
        self._current = None

    # ---- kiểm tra quyền (đã làm sẵn) ----
    def require_login(self):
        if self._current is None:
            raise AuthError("Bạn chưa đăng nhập")
        return self._current

    def require_owner(self):
        user = self.require_login()
        if user.role != Role.OWNER:
            raise PermissionDenied("Chỉ chủ cửa hàng mới được thực hiện thao tác này")
        return user

    def login(self, username, password):
        username = (username or "").strip().lower()
        if not username or not password:
            raise AuthError("Vui lòng nhập tên đăng nhập và mật khẩu")
        user = self._repo.find_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("Sai tên đăng nhập hoặc mật khẩu")
        if not user.active:
            raise AuthError("Tài khoản đã bị khóa, vui lòng liên hệ chủ cửa hàng")
        self._current = user
        return user

    def change_password(self, old_password, new_password):
        current = self.require_login()
        user = self._repo.find_by_id(current.id)   # đọc lại DB để lấy password mới nhất
        if user is None or not verify_password(old_password or "", user.password_hash):
            raise AuthError("Mật khẩu hiện tại không đúng")
        validate_password(new_password)
        if new_password == old_password:
            raise ValidationError("Mật khẩu mới phải khác mật khẩu hiện tại")
        new_hash = hash_password(new_password)
        self._repo.update_password(user.id, new_hash)
        current.password_hash = new_hash