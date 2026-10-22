-- Schema SQL Server (T-SQL) kèm dữ liệu mẫu khởi tạo ban đầu
-- Quan hệ: categories 1-N products 1-N product_variants 1-N order_details N-1 orders
--           discounts 1-N orders ; users 1-N orders (nhân viên bán)

-- 1. TẠO CẤU TRÚC CÁC BẢNG

CREATE TABLE dbo.users (
    id            INT IDENTITY(1,1) PRIMARY KEY,
    username      NVARCHAR(50)  NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    full_name     NVARCHAR(100) NOT NULL,
    role          VARCHAR(10)   NOT NULL CONSTRAINT ck_users_role CHECK (role IN ('OWNER', 'STAFF')),
    active        BIT           NOT NULL CONSTRAINT df_users_active DEFAULT 1,
    created_at    DATETIME2(0)  NOT NULL CONSTRAINT df_users_created DEFAULT SYSDATETIME()
);
GO

CREATE TABLE dbo.categories (
    id   INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE
);
GO

CREATE TABLE dbo.products (
    id          INT IDENTITY(1,1) PRIMARY KEY,
    category_id INT         NOT NULL REFERENCES dbo.categories(id),
    name        NVARCHAR(150) NOT NULL
);
GO

CREATE TABLE dbo.product_variants (
    id         INT IDENTITY(1,1) PRIMARY KEY,
    product_id INT         NOT NULL REFERENCES dbo.products(id),
    size       NVARCHAR(10) NOT NULL,
    price      INT         NOT NULL CONSTRAINT ck_variants_price CHECK (price >= 0),
    stock      INT         NOT NULL CONSTRAINT df_variants_stock DEFAULT 0 CONSTRAINT ck_variants_stock CHECK (stock >= 0),
    CONSTRAINT uq_variants_product_size UNIQUE (product_id, size)
);
GO

CREATE TABLE dbo.discounts (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    code            NVARCHAR(30) NOT NULL UNIQUE,
    type            VARCHAR(10)  NOT NULL CONSTRAINT ck_discounts_type CHECK (type IN ('PERCENT', 'FIXED')),
    value           INT          NOT NULL CONSTRAINT ck_discounts_value CHECK (value > 0),
    min_order_value INT          NOT NULL CONSTRAINT df_discounts_min DEFAULT 0,
    active          BIT          NOT NULL CONSTRAINT df_discounts_active DEFAULT 1
);
GO

CREATE TABLE dbo.orders (
    id              INT IDENTITY(1,1) PRIMARY KEY,
    created_at      DATETIME2(0) NOT NULL,
    user_id         INT          NOT NULL REFERENCES dbo.users(id),      -- nhân viên lập đơn
    discount_id     INT          NULL REFERENCES dbo.discounts(id),      -- NULL = không dùng mã
    total_amount    BIGINT       NOT NULL,                               -- tổng tiền hàng
    discount_amount BIGINT       NOT NULL CONSTRAINT df_orders_discount DEFAULT 0,
    final_amount    BIGINT       NOT NULL                                -- khách phải trả
);
GO

CREATE INDEX ix_orders_created_at ON dbo.orders (created_at);
CREATE INDEX ix_orders_user_created ON dbo.orders (user_id, created_at);
GO

CREATE TABLE dbo.order_details (
    id         INT IDENTITY(1,1) PRIMARY KEY,
    order_id   INT NOT NULL REFERENCES dbo.orders(id) ON DELETE CASCADE,
    variant_id INT NOT NULL REFERENCES dbo.product_variants(id),
    quantity   INT NOT NULL CONSTRAINT ck_details_qty CHECK (quantity > 0),
    unit_price INT NOT NULL                                             -- giá tại thời điểm bán
);
GO


--------------------------------------------------------------------------------
-- 2. NẠP DỮ LIỆU MẪU (SEED DATA)
--------------------------------------------------------------------------------

-- Thêm các mã giảm giá
INSERT INTO dbo.discounts (code, type, value, min_order_value, active) VALUES
(N'GIAM10', 'PERCENT', 10, 100000, 1),
(N'GIAM20K', 'FIXED', 20000, 80000, 1),
(N'COMBO15', 'PERCENT', 15, 150000, 1),
(N'HETHAN', 'PERCENT', 50, 0, 0);
GO

-- Thêm Danh mục, Sản phẩm và Biến thể sản phẩm
DECLARE @cat_bongngo INT, @cat_nuoc INT, @cat_doan INT, @cat_combo INT;
DECLARE @prod INT;

-- 1. Bỏng ngô
INSERT INTO dbo.categories (name) VALUES (N'Bỏng ngô');
SET @cat_bongngo = SCOPE_IDENTITY();

INSERT INTO dbo.products (category_id, name) VALUES (@cat_bongngo, N'Bỏng ngô phô mai');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'M', 30000, 100), (@prod, 'L', 50000, 100);

INSERT INTO dbo.products (category_id, name) VALUES (@cat_bongngo, N'Bỏng ngô caramen');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'M', 32000, 100), (@prod, 'L', 52000, 100);

INSERT INTO dbo.products (category_id, name) VALUES (@cat_bongngo, N'Bỏng ngô vị mặn');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'M', 28000, 100), (@prod, 'L', 45000, 100);


-- 2. Nước uống
INSERT INTO dbo.categories (name) VALUES (N'Nước uống');
SET @cat_nuoc = SCOPE_IDENTITY();

INSERT INTO dbo.products (category_id, name) VALUES (@cat_nuoc, N'Coca-Cola');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'S', 20000, 200), (@prod, 'M', 25000, 200), (@prod, 'L', 30000, 200);

INSERT INTO dbo.products (category_id, name) VALUES (@cat_nuoc, N'Pepsi');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'S', 20000, 200), (@prod, 'M', 25000, 200), (@prod, 'L', 30000, 200);

INSERT INTO dbo.products (category_id, name) VALUES (@cat_nuoc, N'Nước suối');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'M', 15000, 150);

INSERT INTO dbo.products (category_id, name) VALUES (@cat_nuoc, N'Trà đào');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'M', 35000, 80), (@prod, 'L', 45000, 80);


-- 3. Đồ ăn nhẹ
INSERT INTO dbo.categories (name) VALUES (N'Đồ ăn nhẹ');
SET @cat_doan = SCOPE_IDENTITY();

INSERT INTO dbo.products (category_id, name) VALUES (@cat_doan, N'Xúc xích nướng');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'M', 25000, 60);

INSERT INTO dbo.products (category_id, name) VALUES (@cat_doan, N'Khoai tây chiên');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'M', 30000, 60), (@prod, 'L', 40000, 60);


-- 4. Combo
INSERT INTO dbo.categories (name) VALUES (N'Combo');
SET @cat_combo = SCOPE_IDENTITY();

INSERT INTO dbo.products (category_id, name) VALUES (@cat_combo, N'Combo 1 người');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'M', 65000, 50);

INSERT INTO dbo.products (category_id, name) VALUES (@cat_combo, N'Combo đôi');
SET @prod = SCOPE_IDENTITY();
INSERT INTO dbo.product_variants (product_id, size, price, stock) VALUES (@prod, 'L', 119000, 50);
GO