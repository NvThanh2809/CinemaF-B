"""Các lỗi nghiệp vụ. UI chỉ cần bắt AppError để hiện thông báo cho người dùng."""


class AppError(Exception):
    """Lỗi nghiệp vụ chung (thông điệp có thể hiển thị trực tiếp)."""


class EmptyCartError(AppError):
    pass


class DiscountError(AppError):
    pass


class InsufficientStockError(AppError):
    pass


class AuthError(AppError):
    """Sai thông tin đăng nhập, chưa đăng nhập, tài khoản bị khóa..."""


class PermissionDenied(AppError):
    """Tài khoản không đủ quyền thực hiện thao tác."""


class ValidationError(AppError):
    """Dữ liệu người dùng nhập không hợp lệ."""


class DatabaseConnectionError(Exception):
    """Không kết nối được CSDL (kèm hướng dẫn xử lý)."""
