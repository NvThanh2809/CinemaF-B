# Cinema F&B – Quản lý bán đồ ăn, thức uống tại rạp chiếu phim

Ứng dụng **desktop** (Python + Tkinter) cho quầy bán đồ ăn, thức uống ở rạp chiếu phim: nhân viên lập đơn nhanh tại quầy,
chủ cửa hàng quản lý tài khoản và theo dõi doanh số. Dữ liệu lưu trên **SQL Server**.

> Bài tập lớn môn **Lập trình Python** – nhóm 3 thành viên.

---

## 1. Tính năng

### Dành cho mọi tài khoản (nhân viên và chủ cửa hàng)
| Chức năng | Mô tả |
|---|---|
| **Đăng nhập** | Tên đăng nhập + mật khẩu; thông báo lỗi chung khi sai (không lộ tài khoản có tồn tại), tài khoản bị khóa không vào được |
| **Tổng quan** | Doanh thu và số đơn hôm nay, doanh thu tháng này, giá trị đơn trung bình, biểu đồ 14 ngày gần nhất |
| **Bán hàng** | Tìm sản phẩm (không phân biệt hoa thường và dấu tiếng Việt), chọn size, thêm vào giỏ, áp mã ưu đãi, thanh toán |
| **Lịch sử đơn hàng** | Xem lại đơn đã bán và hóa đơn chi tiết; nhân viên chỉ thấy đơn của chính mình |
| **Đổi mật khẩu** | Nhập mật khẩu cũ, mật khẩu mới ít nhất 6 ký tự và phải khác mật khẩu cũ |

### Chỉ dành cho chủ cửa hàng
| Chức năng | Mô tả |
|---|---|
| **Quản lý tài khoản** | Thêm, sửa, khóa/mở khóa, xóa tài khoản; đặt lại mật khẩu; tìm kiếm không dấu |
| **Doanh số – theo thời gian** | Toàn cửa hàng hoặc từng nhân viên, xem **theo ngày** hoặc **theo tháng**, chọn khoảng ngày tùy ý, biểu đồ cột và bảng chi tiết |
| **Doanh số – so sánh nhân viên** | Xếp hạng nhân viên theo doanh thu thực thu, bấm đúp để xem chi tiết một người |

### Các quy tắc nghiệp vụ đáng chú ý
- Mã ưu đãi có hai loại: **giảm theo phần trăm** và **giảm số tiền cố định**, kèm giá trị đơn tối thiểu và trạng thái còn/hết hiệu lực.
- Thanh toán chạy trong **một transaction**: trừ tồn kho và ghi đơn cùng lúc, lỗi giữa chừng thì hoàn tác toàn bộ; không đủ hàng thì từ chối.
- Tài khoản **đã có đơn hàng** không bị xóa cứng mà chỉ bị khóa, để doanh số cũ vẫn đúng.
- Luôn còn ít nhất **một chủ cửa hàng đang hoạt động**; không ai tự hạ quyền, tự khóa hay tự xóa tài khoản đang đăng nhập.
- Khoảng ngày thống kê **gồm cả ngày cuối**; đơn lúc 00:00:00 và 23:59:59 được xếp đúng ngày.

---

## 2. Công nghệ

| Thành phần | Sử dụng |
|---|---|
| Ngôn ngữ | Python 3.9 trở lên |
| Giao diện | Tkinter / ttk (có sẵn trong Python), theme `clam` tự tinh chỉnh |
| Cơ sở dữ liệu | SQL Server (Express đủ dùng) qua **pyodbc** + *ODBC Driver 18 for SQL Server* |
| Dự phòng / kiểm thử | SQLite (có sẵn trong Python), chỉ dùng khi chạy test hoặc chưa có SQL Server |
| Băm mật khẩu | PBKDF2-HMAC-SHA256 + salt ngẫu nhiên (thư viện chuẩn `hashlib`) |
| Kiểm thử | `unittest` (thư viện chuẩn) |

Chỉ có **một thư viện ngoài** cần cài: `pyodbc`.

---

## 3. Kiến trúc

Dự án tổ chức theo **các tầng**, tương tự cách chia package của một dự án Java:

```
 Giao diện (ui/)  ──►  Service (services/)  ──►  Repository (repositories/)  ──►  Database (database/)
   Tkinter               luật nghiệp vụ,            câu lệnh SQL                      kết nối, transaction,
   hiển thị              phân quyền                                                   khác biệt SQL Server/SQLite
```

- **`ui/`** chỉ hiển thị và gọi service; không viết SQL, không chứa luật nghiệp vụ.
- **`services/`** chứa luật nghiệp vụ và **kiểm tra quyền** (`require_login`, `require_owner`). Ẩn nút trên giao diện chỉ để cho gọn; chốt chặn thật nằm ở service.
- **`repositories/`** chỉ chứa SQL, luôn dùng tham số `?` (chống SQL injection).
- **`models/`** là các lớp dữ liệu (`User`, `Product`, `Order`, `Discount`, ...), có kế thừa và đa hình ở `Discount` (giảm theo % và giảm cố định).
- **`app_context.py`** là nơi duy nhất lắp ráp repository và service (kiểu "dependency injection" đơn giản).
- **`utils/`** chứa tiện ích dùng chung: lỗi nghiệp vụ, băm mật khẩu, ngày giờ, định dạng tiền, bỏ dấu tiếng Việt, in hóa đơn.

### Cấu trúc thư mục

```
cinema_fnb/
├── main.py                    # điểm khởi chạy
├── config.py                  # cấu hình chung (không chứa mật khẩu)
├── config_local.example.py    # mẫu cấu hình riêng từng máy -> copy thành config_local.py
├── app_context.py             # lắp ráp các tầng
├── requirements.txt
├── database/                  # kết nối SQL Server/SQLite, schema, dữ liệu mẫu
├── models/                    # lớp dữ liệu
├── repositories/              # truy vấn SQL
├── services/                  # nghiệp vụ + phân quyền
├── ui/
│   ├── app.py, shell.py       # cửa sổ chính, thanh điều hướng dashboard
│   ├── login_view.py          # màn hình đăng nhập
│   ├── theme.py, widgets.py   # màu, phông, thẻ, bảng, biểu đồ cột, chọn khoảng ngày
│   ├── pages/                 # Tổng quan, Bán hàng, Lịch sử đơn, Doanh số, Quản lý tài khoản
│   └── *_dialog.py ...        # hộp thoại tìm sản phẩm, chọn size, hóa đơn, tài khoản
└── utils/                     # tiện ích dùng chung
```

---

## 4. Cơ sở dữ liệu

Database `CinemaFnB`, gồm **7 bảng**, tự tạo ở lần chạy đầu:

| Bảng | Nội dung chính |
|---|---|
| `users` | Tài khoản: `username` (duy nhất), `password_hash`, `full_name`, `role` (`OWNER`/`STAFF`), `active`, `created_at` |
| `categories` | Danh mục: Bỏng ngô, Nước uống, Đồ ăn nhẹ, Combo |
| `products` | Sản phẩm, thuộc một danh mục |
| `product_variants` | Biến thể theo **size** (S/M/L): `price`, `stock`; duy nhất theo (sản phẩm, size) |
| `discounts` | Mã ưu đãi: `code`, `type` (`PERCENT`/`FIXED`), `value`, `min_order_value`, `active` |
| `orders` | Đơn hàng: `created_at`, `user_id` (người bán), `discount_id`, `total_amount`, `discount_amount`, `final_amount` |
| `order_details` | Dòng đơn: `variant_id`, `quantity`, `unit_price` (lưu giá tại thời điểm bán) |

Quan hệ: `categories 1–N products 1–N product_variants`, `users 1–N orders`, `discounts 1–N orders`, `orders 1–N order_details N–1 product_variants`.

Dữ liệu mẫu tự nạp: 4 danh mục, 11 sản phẩm (20 biến thể), 4 mã ưu đãi (`GIAM10`, `GIAM20K`, `COMBO15`, `HETHAN` là mã đã hết hạn để thử), và 2 tài khoản.

---

## 5. Cài đặt và chạy (Windows, PowerShell)

### Yêu cầu
1. **Python 3.9+** (khi cài tick *Add python.exe to PATH*; nếu lệnh `python` không nhận thì dùng `py`).
2. **SQL Server Express** và **ODBC Driver 18 for SQL Server** của Microsoft.

### Các bước
```powershell
pip install -r requirements.txt
copy config_local.example.py config_local.py
python main.py
```

Lần chạy đầu, ứng dụng **tự tạo database, các bảng và dữ liệu mẫu**.

### Khai báo kết nối SQL Server
`config.py` chỉ giữ giá trị mặc định (`localhost\SQLEXPRESS` + Windows Authentication). Nếu máy bạn khác, mở `config_local.py` và bỏ dấu `#` ở các dòng cần dùng:

```python
DB_SERVER = r"TEN-MAY-CUA-BAN\SQLEXPRESS"   # xem trong SSMS, hộp Connect > Server name
DB_USER = "sa"                               # để trống "" = Windows Authentication
DB_PASSWORD = "mat-khau-cua-ban"
```

> `config_local.py` nằm trong `.gitignore` nên **không bị đẩy lên Git**. Đây là nơi duy nhất được ghi mật khẩu SQL thật.

### Chưa có SQL Server?
Chạy tạm bằng SQLite (dữ liệu lưu trong thư mục `data/`):
```powershell
$env:CINEMA_DB_ENGINE="sqlite"; python main.py
```

### Lỗi thường gặp
| Hiện tượng | Cách xử lý |
|---|---|
| `Python was not found` | Cài Python từ python.org, tick *Add to PATH*; hoặc dùng lệnh `py` |
| Không kết nối được SQL Server | Kiểm tra dịch vụ **SQL Server (SQLEXPRESS)** đang chạy, tên server trong `config_local.py` đúng, đã cài ODBC Driver 18 |
| Báo thiếu `tkinter` (Linux) | `sudo apt install python3-tk` |

---

## 6. Tài khoản mặc định

| Tên đăng nhập | Mật khẩu | Vai trò |
|---|---|---|
| `admin` | `admin123` | Chủ cửa hàng (thấy đủ 5 trang) |
| `nhanvien` | `nv123456` | Nhân viên (thấy 3 trang) |

**Hãy đổi mật khẩu ngay sau khi đăng nhập** (nút *Đổi mật khẩu* ở góc trái dưới).

### Phân quyền

| Trang / thao tác | Nhân viên | Chủ cửa hàng |
|---|:---:|:---:|
| Tổng quan (số liệu của chính mình) | ✔ | ✔ (cả cửa hàng) |
| Bán hàng | ✔ | ✔ |
| Lịch sử đơn hàng | Chỉ đơn của mình | Tất cả đơn |
| Đổi mật khẩu của mình | ✔ | ✔ |
| Doanh số | ✘ | ✔ |
| Quản lý tài khoản | ✘ | ✔ |

---

## 7. Hướng dẫn sử dụng nhanh

**Bán hàng:** vào *Bán hàng* → gõ tên món (ví dụ `bong ngo`, không cần dấu) → chọn size và số lượng → nhập mã ưu đãi nếu có → *Thanh toán* → xem hóa đơn.

**Quản lý tài khoản (chủ cửa hàng):** vào *Quản lý tài khoản* → *Thêm tài khoản* (tên đăng nhập 3–30 ký tự gồm chữ thường không dấu, số, `_` hoặc `.`); chọn một dòng → *Sửa* để đổi họ tên, vai trò, khóa/mở khóa, đặt lại mật khẩu; *Xóa* hỏi xác nhận, tài khoản đã có đơn hàng sẽ chỉ bị khóa.

**Xem doanh số (chủ cửa hàng):** vào *Doanh số* → tab *Theo thời gian* chọn đối tượng, cách xem (ngày/tháng) và khoảng ngày; tab *So sánh nhân viên* xem bảng xếp hạng và bấm đúp để xem chi tiết một người.

---

## 8. Bảo mật

- Mật khẩu **không lưu dạng gốc**: lưu PBKDF2-SHA256 với salt ngẫu nhiên và số vòng lặp kèm theo chuỗi băm.
- Toàn bộ truy vấn dùng **tham số `?`**, không nối chuỗi.
- Quyền được **kiểm ở tầng service**, không chỉ ẩn nút trên giao diện.
- Thông tin kết nối thật nằm ở `config_local.py` (bị `.gitignore` loại), không có trong mã nguồn đẩy lên Git.

### Chế độ phát triển (không dùng khi nộp/chạy thật)
Trong lúc code có thể bỏ qua đăng nhập thật bằng biến `DEV_LOGIN` (`config.py` hoặc `config_local.py`):

| `DEV_LOGIN` | Kết quả |
|---|---|
| `"ANY"` | Hiện màn hình đăng nhập, gõ tên nào cũng vào, **bỏ qua mật khẩu** |
| `"OWNER"` / `"STAFF"` | Vào thẳng với `admin` / `nhanvien` |
| `""` | **Đăng nhập thật** – bắt buộc đặt như vậy khi nộp bài và khi dùng thật |

---

## 9. Thành viên nhóm

| Thành viên | Phụ trách |
|---|---|
| *Nguyễn Văn Thành* | Đăng nhập, phân quyền, quản lý tài khoản, thống kê doanh số, trang Tổng quan, kết nối CSDL, cấu hình, giao diện chung (theme, widget)  |
| *Trần Ngọc Hải* | Sản phẩm và tìm kiếm, lịch sử đơn hàng  |
| *Phạm Văn Hiệp* | Bán hàng, giỏ hàng, mã ưu đãi, thanh toán, hóa đơn|

---