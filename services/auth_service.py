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
    """TODO (C): ném ValidationError nếu mật khẩu ngắn hơn MIN_PASSWORD_LENGTH ký tự (UserService cũng gọi hàm này)."""
    raise NotImplementedError("TODO (C): validate_password")


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

    # ---- phần C làm ----
    def login(self, username, password):
        """TODO (C): đăng nhập, trả về User và gán self._current.

        - Chuẩn hóa username (strip + chữ thường); trống thì AuthError("Vui lòng nhập tên đăng nhập và mật khẩu")
        - Sai tên hoặc sai mật khẩu: CÙNG MỘT thông báo "Sai tên đăng nhập hoặc mật khẩu" (không lộ tài khoản có tồn tại)
        - Tài khoản bị khóa (active = False): AuthError("Tài khoản đã bị khóa, ...")
        - Dùng utils.security.verify_password(password, user.password_hash)
        """
        raise NotImplementedError("TODO (C): AuthService.login")

    def change_password(self, old_password, new_password):
        """TODO (C): đổi mật khẩu của chính mình: kiểm tra mật khẩu cũ, validate_password mới, mới phải khác cũ,
        lưu hash mới (utils.security.hash_password) bằng UserRepository.update_password và cập nhật self._current."""
        raise NotImplementedError("TODO (C): AuthService.change_password")
