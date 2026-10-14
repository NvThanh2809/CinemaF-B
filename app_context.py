"""Lắp ráp các tầng (repository -> service) thành một đối tượng dùng chung cho giao diện.

Đây là NƠI DUY NHẤT tạo repository và service. Khi thêm service mới, khai báo thêm ở đây.
"""
from dataclasses import dataclass

from models.user import User
from repositories.discount_repository import DiscountRepository
from repositories.order_repository import OrderRepository
from repositories.product_repository import ProductRepository
from repositories.report_repository import ReportRepository
from repositories.user_repository import UserRepository
from services.auth_service import AuthService
from services.discount_service import DiscountService
from services.order_service import OrderService
from services.product_service import ProductService
from services.report_service import ReportService
from services.user_service import UserService
from utils.exceptions import AuthError


@dataclass
class AppContext:
    db: object
    auth: AuthService
    products: ProductService
    discounts: DiscountService
    orders: OrderService
    users: UserService
    reports: ReportService


def build_context(db):
    user_repo = UserRepository(db)
    product_repo = ProductRepository(db)
    order_repo = OrderRepository(db)
    auth = AuthService(user_repo)
    return AppContext(
        db=db,
        auth=auth,
        products=ProductService(product_repo),
        discounts=DiscountService(DiscountRepository(db)),
        orders=OrderService(db, order_repo, product_repo, auth),
        users=UserService(user_repo, auth),
        reports=ReportService(ReportRepository(db), auth),
    )


# ------------------------------------------------------------------ chế độ dev
def load_session_user(db, username):
    """Đọc một tài khoản có sẵn trong DB thành User, KHÔNG kiểm tra mật khẩu.

    Chỉ dùng cho chế độ dev (config.DEV_LOGIN) và cho tests/helpers.py, để các module khác
    chạy được dù AuthService.login (thành viên C) chưa xong.
    """
    row = db.query_one(
        "SELECT id, username, full_name, role, active FROM users WHERE username = ?", (username,))
    if row is None:
        raise LookupError(f"Không có tài khoản '{username}' trong CSDL (bảng users trống?)")
    return User(row["id"], row["username"], row["full_name"], row["role"], bool(row["active"]))


def dev_login_mode():
    """Giá trị config.DEV_LOGIN đã chuẩn hóa: "ANY" | "OWNER" | "STAFF" | "" (đăng nhập thật qua AuthService)."""
    import config
    return (config.DEV_LOGIN or "").strip().upper()


def start_dev_session(ctx):
    """Nếu DEV_LOGIN là "OWNER" hoặc "STAFF" thì đăng nhập sẵn (bỏ qua màn hình đăng nhập) và trả về True."""
    import config
    role = dev_login_mode()
    if role not in ("OWNER", "STAFF"):
        return False
    account = config.DEFAULT_OWNER if role == "OWNER" else config.DEFAULT_STAFF
    ctx.auth.set_current_user(load_session_user(ctx.db, account["username"]))
    return True


class DevLoginAuth:
    """Đăng nhập THỬ (DEV_LOGIN = "ANY"): màn hình đăng nhập nhận MỌI tên, KHÔNG kiểm tra mật khẩu.

    Dùng thay AuthService.login trong lúc thành viên C chưa làm xong đăng nhập thật. Quy ước:
      - tên "admin"   -> chủ cửa hàng (thấy đủ 5 trang)
      - tên khác      -> nhân viên (thấy 3 trang), hiển thị đúng tên vừa gõ
    Người bán vẫn được gắn vào tài khoản có thật trong bảng users (admin hoặc nhanvien) để khóa ngoại
    orders.user_id luôn hợp lệ khi thanh toán.
    """

    def __init__(self, ctx):
        self._ctx = ctx

    def login(self, username, password):  # noqa: ARG002  (mật khẩu bị bỏ qua có chủ ý)
        import config
        name = (username or "").strip()
        if not name:
            raise AuthError("Vui lòng nhập tên đăng nhập")
        owner_name = config.DEFAULT_OWNER["username"]
        staff_name = config.DEFAULT_STAFF["username"]
        if name.lower() == owner_name:
            user = load_session_user(self._ctx.db, owner_name)
        elif name.lower() == staff_name:
            user = load_session_user(self._ctx.db, staff_name)
        else:
            base = load_session_user(self._ctx.db, staff_name)  # mượn id của nhân viên mẫu để lưu đơn hợp lệ
            user = User(base.id, name, name, base.role, True)
        self._ctx.auth.set_current_user(user)
        return user
