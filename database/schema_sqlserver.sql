-- Schema SQL Server (T-SQL)
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
