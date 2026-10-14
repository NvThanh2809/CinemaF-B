"""Quản lý tài khoản - chỉ chủ cửa hàng được dùng.

Người phụ trách: THÀNH VIÊN C.
Mọi hàm đều bắt đầu bằng self._auth.require_owner() (quyền kiểm ở service, không chỉ ẩn nút trên UI).
"""
from models.user import Role  # noqa: F401  (C dùng khi code)
from services.auth_service import validate_password  # noqa: F401
from utils.exceptions import PermissionDenied, ValidationError  # noqa: F401
from utils.security import hash_password  # noqa: F401


class UserService:
    def __init__(self, user_repo, auth):
        self._repo = user_repo
        self._auth = auth

    def list_users(self):
        """TODO (C): trả về [(User, số đơn đã lập)]. (Module B cũng gọi hàm này để đổ ô lọc nhân viên.)"""
        raise NotImplementedError("TODO (C): UserService.list_users")

    def create(self, username, full_name, role, password):
        """TODO (C): thêm tài khoản. Kiểm tra: username 3-30 ký tự [a-z0-9_.], họ tên không rỗng, role hợp lệ,
        mật khẩu hợp lệ, username chưa tồn tại. Băm mật khẩu bằng hash_password trước khi lưu."""
        raise NotImplementedError("TODO (C): UserService.create")

    def update(self, user_id, full_name, role, active, new_password=None):
        """TODO (C): sửa họ tên / vai trò / trạng thái, new_password (nếu có) thì đặt lại mật khẩu.
        Quy tắc: không tự hạ quyền hoặc khóa chính mình; luôn còn ít nhất 1 chủ cửa hàng đang hoạt động."""
        raise NotImplementedError("TODO (C): UserService.update")

    def delete(self, user_id):
        """TODO (C): xóa tài khoản; trả 'deleted' hoặc 'locked'.
        Không xóa chính mình; không xóa chủ cửa hàng cuối cùng; tài khoản ĐÃ CÓ ĐƠN HÀNG thì chỉ khóa
        (active = False) để doanh số cũ vẫn đúng."""
        raise NotImplementedError("TODO (C): UserService.delete")
