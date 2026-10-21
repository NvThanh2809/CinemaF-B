"""Cấu hình chung. Có thể sửa trực tiếp ở đây hoặc đặt biến môi trường CINEMA_*."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INVOICE_DIR = BASE_DIR / "invoices"

APP_TITLE = "Cinema F&B - Bán đồ ăn uống tại rạp"
CINEMA_NAME = "RẠP CHIẾU PHIM DEMO"
CINEMA_ADDRESS = "123 Đường ABC, Hà Nội"

# ---------------------------------------------------------------- Cơ sở dữ liệu
# "sqlserver": SQL Server qua ODBC (mặc định, dùng khi chạy thật)
# "sqlite"   : file SQLite, chỉ để dev nhanh / chạy test khi chưa có SQL Server
DB_ENGINE = os.getenv("CINEMA_DB_ENGINE", "sqlserver")

# SQL Server. Đây chỉ là giá trị MẶC ĐỊNH dùng chung cho cả nhóm, KHÔNG ghi tên máy hay mật khẩu thật vào đây.
# Tên server, tài khoản và mật khẩu thật của từng máy khai báo trong config_local.py (không bị đẩy lên Git).
# Mặc định: SQL Server Express cài mặc định (localhost\SQLEXPRESS) + Windows Authentication (không cần mật khẩu).
DB_SERVER = os.getenv("CINEMA_DB_SERVER", r"LAPTOP-C2U5EVHV\SQLEXPRESS01")
DB_NAME = os.getenv("CINEMA_DB_NAME", "CinemaFnB")      # tự tạo nếu chưa có
DB_USER = os.getenv("CINEMA_DB_USER", "sa")               # để trống = Windows Authentication
DB_PASSWORD = os.getenv("CINEMA_DB_PASSWORD", "Warehouse@123")
DB_DRIVER = os.getenv("CINEMA_DB_DRIVER", "")           # để trống = tự chọn driver ODBC mới nhất

SQLITE_PATH = Path(os.getenv("CINEMA_SQLITE_PATH", BASE_DIR / "data" / "cinema_fnb.db"))

# Tài khoản mặc định tạo ở lần chạy đầu tiên (khi bảng users còn trống). HÃY ĐỔI MẬT KHẨU SAU KHI ĐĂNG NHẬP.
DEFAULT_OWNER = {"username": "admin", "password": "admin123", "full_name": "Chủ cửa hàng"}
DEFAULT_STAFF = {"username": "nhanvien", "password": "nv123456", "full_name": "Nhân viên mẫu"}

# ---------------------------------------------------------------- Dành cho nhóm phát triển (phần thêm vào)
# Cách vào app khi đang code, vì AuthService.login (đăng nhập thật) do thành viên C làm:
#   "ANY"  : (mặc định) hiện màn hình đăng nhập, gõ TÊN BẤT KỲ là vào được, không kiểm tra mật khẩu.
#            Tên "admin" = chủ cửa hàng (đủ 5 trang), tên khác = nhân viên (3 trang)
#   "OWNER": bỏ qua màn hình đăng nhập, vào thẳng với tài khoản chủ cửa hàng (admin)
#   "STAFF": bỏ qua màn hình đăng nhập, vào thẳng với tài khoản nhân viên (nhanvien)
#   ""     : đăng nhập THẬT qua AuthService (đặt như vậy khi C làm xong đăng nhập và BẮT BUỘC khi nộp bài)
DEV_LOGIN = ""

# Cấu hình riêng từng máy (tên server, tài khoản SQL, mật khẩu SQL, DEV_LOGIN...): tạo file config_local.py
# cùng thư mục với config.py (xem config_local.example.py). File này nằm trong .gitignore nên không bị đẩy lên Git,
# và các giá trị trong đó GHI ĐÈ lên các giá trị ở trên (kể cả biến môi trường CINEMA_*).
# try:
#     from config_local import *  # noqa: F401,F403
# except ImportError:
#     pass