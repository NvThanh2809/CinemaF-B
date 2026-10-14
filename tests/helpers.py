"""Dùng chung cho các test: CSDL SQLite trong bộ nhớ + đầy đủ service.

`Env()` dựng cả hệ thống trên một DB tạm (đã có menu mẫu + 2 tài khoản admin / nhanvien) và ĐĂNG NHẬP SẴN
bằng tài khoản được chọn. Việc đăng nhập đi đường tắt (app_context.load_session_user), KHÔNG qua AuthService.login,
nên test của module A và B chạy được ngay cả khi thành viên C chưa làm xong đăng nhập.

    env = Env()                     # đăng nhập sẵn là chủ cửa hàng (admin)
    env = Env("nhanvien")           # đăng nhập sẵn là nhân viên
    env = Env(login_as=None)        # chưa đăng nhập (test của C dùng env.auth.login("admin", "admin123") thật)
    env.login("nhanvien")           # đổi người đang đăng nhập giữa chừng
"""
from app_context import load_session_user
from database.connection import connect_sqlite, init_db
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
from utils import security

security.ITERATIONS = 1000  # băm nhanh cho test (hash lưu kèm số vòng lặp nên vẫn kiểm tra được)


class Env:
    def __init__(self, login_as="admin"):
        self.db = connect_sqlite(":memory:")
        init_db(self.db)
        self.user_repo = UserRepository(self.db)
        self.product_repo = ProductRepository(self.db)
        self.order_repo = OrderRepository(self.db)
        self.report_repo = ReportRepository(self.db)
        self.auth = AuthService(self.user_repo)
        self.users = UserService(self.user_repo, self.auth)
        self.products = ProductService(self.product_repo)
        self.discounts = DiscountService(DiscountRepository(self.db))
        self.orders = OrderService(self.db, self.order_repo, self.product_repo, self.auth)
        self.reports = ReportService(self.report_repo, self.auth)
        if login_as:
            self.login(login_as)

    def login(self, username):
        """Đăng nhập nhanh bằng tài khoản có sẵn trong DB (không kiểm tra mật khẩu)."""
        user = load_session_user(self.db, username)
        self.auth.set_current_user(user)
        return user

    def close(self):
        self.db.close()
