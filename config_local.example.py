"""Mẫu cấu hình riêng cho từng máy.

Cách dùng: sao chép file này thành `config_local.py` (cùng thư mục với config.py), bỏ dấu # ở các dòng cần dùng rồi sửa
cho đúng máy của bạn. Chỉ cần ghi những giá trị khác với config.py.
File config_local.py đã nằm trong .gitignore nên KHÔNG bị đẩy lên Git: đây là nơi duy nhất được ghi mật khẩu SQL thật.
"""
# --- Kết nối SQL Server ---
# DB_SERVER = r"TEN-MAY-CUA-BAN\SQLEXPRESS"   # xem trong SSMS, hộp Connect > Server name
# DB_USER = "sa"                               # để trống "" = dùng Windows Authentication (không cần mật khẩu)
# DB_PASSWORD = "mat-khau-cua-ban"

# --- Chế độ dev ---
# DEV_LOGIN = "OWNER"                          # "ANY" (mặc định: gõ tên nào cũng vào) | "OWNER" | "STAFF" | "" (đăng nhập thật)
