# Cinema F&B - Khung dự án (BTL Python, nhóm 3 người)

Ứng dụng desktop **Tkinter + SQL Server** cho quầy bán đồ ăn uống ở rạp chiếu phim. Đây là **khung ban đầu**:
giao diện chung và kết nối SQL Server đã chạy được, còn mọi chức năng của từng thành viên là **file rỗng có sẵn chữ ký hàm
và danh sách việc cần làm**. Mở file của mình, thấy `TODO (A|B|C)` là biết phải code gì.

## 1. Chạy lần đầu (Windows, PowerShell)

1. Cài **Python 3.9+** (tick *Add python.exe to PATH*; nếu lệnh `python` không nhận thì dùng `py`), **SQL Server Express** và
   **ODBC Driver 18 for SQL Server**.
2. Trong thư mục dự án:

```powershell
pip install -r requirements.txt
copy config_local.example.py config_local.py     # rồi mở config_local.py sửa cho đúng máy của bạn
python main.py
```

- `config.py` chỉ giữ giá trị **mặc định dùng chung** (`localhost\SQLEXPRESS` + Windows Authentication), tuyệt đối không ghi mật khẩu vào đó.
  Tên server, tài khoản `sa` và mật khẩu thật của máy bạn khai trong `config_local.py` (ghi đè `config.py`,
  đã nằm trong `.gitignore` nên không bị đẩy lên Git). Máy dùng đúng SQL Express mặc định với Windows Authentication thì không cần file này.
- Lần chạy đầu app **tự tạo database `CinemaFnB`**, 7 bảng, menu mẫu, 4 mã ưu đãi và 2 tài khoản
  (`admin` / `admin123` là chủ cửa hàng, `nhanvien` / `nv123456` là nhân viên).
- Chưa có SQL Server? Chạy tạm bằng SQLite: `$env:CINEMA_DB_ENGINE="sqlite"; python main.py`.

### Chế độ dev: đăng nhập thử
Đăng nhập thật là việc của thành viên C nên khung mặc định **hiện màn hình đăng nhập và cho vào bằng TÊN BẤT KỲ**
(`DEV_LOGIN = "ANY"` trong `config.py`), không kiểm tra mật khẩu, chưa cần tạo tài khoản.
Gõ `admin` = chủ cửa hàng (đủ 5 trang), gõ tên khác = nhân viên (3 trang, hiển thị đúng tên vừa gõ).

| `DEV_LOGIN` | Kết quả |
|---|---|
| `"ANY"` (mặc định) | Hiện màn hình đăng nhập, gõ tên nào cũng vào, bỏ qua mật khẩu |
| `"OWNER"` | Bỏ qua đăng nhập, vào thẳng với `admin`, thấy đủ 5 trang |
| `"STAFF"` | Bỏ qua đăng nhập, vào thẳng với `nhanvien`, chỉ thấy 3 trang (thử phân quyền) |
| `""` | Đăng nhập THẬT qua `AuthService`. **C đặt lại như vậy khi làm xong đăng nhập, và bắt buộc khi nộp bài** |

Đặt tạm cho một lần chạy: `$env:CINEMA_DEV_LOGIN="STAFF"; python main.py`.

Bấm vào chức năng chưa được code (ví dụ Đăng nhập) sẽ hiện hộp thoại *"Chức năng chưa được code"* kèm tên hàm cần làm, không văng lỗi.

## 2. Đã có sẵn và việc còn lại

| Đã xong, dùng luôn, không cần làm | Khung rỗng, thành viên tự code |
|---|---|
| `main.py`, `config.py`, `app_context.py` (nối các tầng, kèm hàm cho chế độ dev) | `repositories/*` (5 file) |
| `database/` (kết nối SQL Server/SQLite, schema, dữ liệu mẫu) | `services/*` (7 file) |
| `ui/`: `app.py`, `login_view.py`, `shell.py` (thanh điều hướng), `theme.py`, `widgets.py` (thẻ, bảng, biểu đồ cột, chọn khoảng ngày), `helpers.py` | `ui/pages/*` (5 trang), 5 hộp thoại / màn hình |
| `utils/`: lỗi, băm mật khẩu, ngày giờ, định dạng tiền, bỏ dấu tiếng Việt | `utils/invoice_printer.py`, logic của `models/discount.py`, `models/order_detail.py` |
| `models/` còn lại (chỉ chứa dữ liệu) và phiên đăng nhập trong `AuthService` | 60 test khung (đang `skip`) |

`python -m unittest discover -s tests -t .` hiện cho **69 test: 9 chạy thật (hạ tầng) và 60 đang skip**. Mỗi người viết dần cho phần mình
và xóa dòng `@TODO` của test đã viết xong.

Tìm việc của mình: `Get-ChildItem -Recurse -Filter *.py | Select-String "TODO \(B\)"` (đổi `B` thành `A` hoặc `C`).

## 3. Phân công

### Thành viên A - Sản phẩm và tìm kiếm
| Tầng | File |
|---|---|
| Repository | `repositories/product_repository.py` (`search_products`, `get_variants`, `decrease_stock`) |
| Service | `services/product_service.py` |
| Giao diện | `ui/product_search_dialog.py`, `ui/variant_dialog.py` |
| Test | `tests/test_product_service.py` (7 test) |
| Người gác file chung | `database/*`, `config.py`, `app_context.py`, `main.py`, `ui/app.py`, `ui/helpers.py`, `ui/pages/base.py`, `ui/theme.py`, `ui/widgets.py`, `requirements.txt` |

Thứ tự gợi ý: repository + service tìm kiếm, rồi `decrease_stock` (B cần để thanh toán, nên làm sớm), rồi hai hộp thoại.

### Thành viên B - Bán hàng, ưu đãi, hóa đơn
| Tầng | File |
|---|---|
| Model | `models/discount.py` (Percent/Fixed), `models/order_detail.py` (`models/order.py` đã có) |
| Repository | `repositories/discount_repository.py`, `repositories/order_repository.py` |
| Service | `services/cart_service.py`, `services/discount_service.py`, `services/order_service.py` |
| Giao diện | `ui/pages/sales_page.py`, `ui/pages/orders_page.py`, `ui/invoice_view.py` |
| Tiện ích | `utils/invoice_printer.py` |
| Test | `test_cart_service.py` (11), `test_order_service.py` (8), `test_invoice.py` (3) |
| Người gác file chung | `utils/exceptions.py`, `utils/dates.py` |

Thứ tự gợi ý: `Discount` + `OrderDetail` + `CartService` (không cần DB, làm và test được ngay), rồi `DiscountService`,
rồi `OrderRepository` + `OrderService.checkout`, rồi `SalesPage` (cần A xong hai hộp thoại), cuối cùng hóa đơn và `OrdersPage`.

### Thành viên C - Tài khoản, phân quyền, báo cáo
| Tầng | File |
|---|---|
| Model | `models/user.py`, `models/report.py` (đã có sẵn dữ liệu) |
| Repository | `repositories/user_repository.py`, `repositories/report_repository.py` |
| Service | `services/auth_service.py` (`login`, `change_password`, `validate_password`), `services/user_service.py`, `services/report_service.py` |
| Giao diện | `ui/pages/home_page.py`, `ui/pages/reports_page.py`, `ui/pages/accounts_page.py`, `ui/account_dialogs.py` |
| Test | `test_auth_service.py` (8), `test_user_service.py` (12), `test_report_service.py` (11) |
| Người gác file chung | `ui/shell.py`, `ui/login_view.py`, `tests/helpers.py`, `README.md`, `.gitignore` |

Thứ tự gợi ý: `UserRepository` + `AuthService.login` (xong thì đặt `DEV_LOGIN = ""` và thử đăng nhập thật), rồi `UserService` +
trang Quản lý tài khoản, rồi `ReportRepository`/`ReportService` + trang Doanh số, cuối cùng trang Tổng quan.

> **Lưu ý cân tải:** vì `theme.py` và `widgets.py` đã làm sẵn nên A hiện nhẹ hơn B và C khá nhiều. Nếu nhóm muốn cân lại, cách gọn nhất là
> chuyển cả "Lịch sử đơn hàng" (`ui/pages/orders_page.py` + `OrderRepository.list_orders/find_by_id` + `OrderService.list_orders/get_order`) từ B sang A.

## 4. Hợp đồng giữa các module (đổi chữ ký phải báo nhau trước)

| Bên gọi | Bên được gọi | Nội dung cần giữ |
|---|---|---|
| B (`SalesPage`) | A | `ProductService.search(keyword)` trả `list[Product]`; `get_variants(product_id)` trả `list[ProductVariant]`; `ProductSearchDialog(master, products, keyword)` và `VariantDialog(master, product, variants)` trả kết quả qua `.result` |
| A (`VariantDialog`) | B | Tạo `OrderDetail(variant_id, product_name, size, unit_price, quantity)` |
| B (`OrderService.checkout`) | A | Gọi `ProductRepository.decrease_stock` trong `with db.transaction():`; thiếu hàng thì `InsufficientStockError` |
| B (`OrderService`) | C | `AuthService.require_login()` cho biết người bán; `orders.user_id` trỏ tới bảng `users` |
| C (`ReportRepository`) | B | Đọc các cột `created_at`, `user_id`, `total_amount`, `discount_amount`, `final_amount` của bảng `orders` |
| B (`OrdersPage`) | C | `UserService.list_users()` để đổ ô lọc nhân viên |
| Mọi trang | C | Thêm trang mới phải đăng ký trong `ui/shell.py` |

## 5. Quy tắc làm việc bắt buộc

1. **Một chiều phụ thuộc:** `ui` → `services` → `repositories` → `database`. `ui/` không import `repositories` hay `database`, không viết SQL;
   `services`, `repositories`, `models`, `utils` không import `tkinter`. Repository và service chỉ được tạo trong `app_context.py`.
2. **Quyền kiểm ở service** (`auth.require_login()` / `auth.require_owner()` ở đầu hàm), không chỉ ẩn nút trên giao diện.
3. **SQL luôn dùng tham số `?`**; khác biệt SQL Server và SQLite chỉ đi qua các hàm của `Database` (`top`, `limit`, `day_expr`, `month_expr`, `like_no_accent`).
4. **Ghi nhiều bước thì bọc `with db.transaction():`** (mẫu: thanh toán). Lỗi giữa chừng phải rollback hết.
5. **Tiền là số nguyên đồng**, hiển thị bằng `format_money`; ngày giờ chỉ xử lý qua `utils/dates.py`.
6. **Lỗi nghiệp vụ ném lớp con của `AppError`** với thông báo tiếng Việt; giao diện chỉ bắt `AppError`. Không `except Exception: pass`.
7. **Màu và phông lấy từ `ui/theme.py`**, không gõ mã màu rải rác; hộp thoại kế thừa `BaseDialog`/`FormDialog`, trang mới kế thừa `Page`.
8. **Đổi bảng/cột phải sửa cả `schema_sqlserver.sql` và `schema_sqlite.sql` trong cùng một PR và báo cả nhóm.** `init_db` chỉ tạo bảng khi chưa có
   bảng `users`, nên database đã tạo sẽ không tự cập nhật: mọi người xóa database tạo lại, hoặc PR kèm script `ALTER`.
9. **Không commit** mật khẩu thật, `config_local.py`, `data/`, `invoices/`, `__pycache__`, file `.db`.
10. **Git:** nhánh `feature/<module>-<mô-tả>`; không push thẳng vào `main`; mỗi PR có ít nhất 1 người khác review, riêng file chung và schema
    phải có người gác file duyệt; test xanh mới mở PR. Test chạy trên SQLite nên không bắt được lỗi cú pháp T-SQL: PR có câu SQL mới phải tự chạy thử trên SQL Server thật.

## 6. Trước khi nộp bài

- [ ] `DEV_LOGIN = ""` trong `config.py` (tắt chế độ gõ tên nào cũng vào), đăng nhập thật bằng `admin` và `nhanvien` đều chạy.
- [ ] Đổi mật khẩu mặc định (`admin123`, `nv123456`).
- [ ] `config.py` không chứa tên máy hay mật khẩu SQL thật (chỉ để trong `config_local.py`), và `config_local.py` không có trong repo Git.
- [ ] Toàn bộ test xanh, không còn test `@TODO` và không còn `raise NotImplementedError`.
