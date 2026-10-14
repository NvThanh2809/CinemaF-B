"""Dữ liệu mẫu, nạp bằng Python để dùng chung cho SQL Server và SQLite."""
import config
from utils.security import hash_password

# (danh mục, [(tên sản phẩm, [(size, giá, tồn kho), ...]), ...])
CATALOG = [
    ("Bỏng ngô", [
        ("Bỏng ngô phô mai", [("M", 30000, 100), ("L", 50000, 100)]),
        ("Bỏng ngô caramen", [("M", 32000, 100), ("L", 52000, 100)]),
        ("Bỏng ngô vị mặn", [("M", 28000, 100), ("L", 45000, 100)]),
    ]),
    ("Nước uống", [
        ("Coca-Cola", [("S", 20000, 200), ("M", 25000, 200), ("L", 30000, 200)]),
        ("Pepsi", [("S", 20000, 200), ("M", 25000, 200), ("L", 30000, 200)]),
        ("Nước suối", [("M", 15000, 150)]),
        ("Trà đào", [("M", 35000, 80), ("L", 45000, 80)]),
    ]),
    ("Đồ ăn nhẹ", [
        ("Xúc xích nướng", [("M", 25000, 60)]),
        ("Khoai tây chiên", [("M", 30000, 60), ("L", 40000, 60)]),
    ]),
    ("Combo", [
        ("Combo 1 người", [("M", 65000, 50)]),
        ("Combo đôi", [("L", 119000, 50)]),
    ]),
]

# (mã, loại, giá trị, đơn tối thiểu, còn hiệu lực)
DISCOUNTS = [
    ("GIAM10", "PERCENT", 10, 100000, 1),
    ("GIAM20K", "FIXED", 20000, 80000, 1),
    ("COMBO15", "PERCENT", 15, 150000, 1),
    ("HETHAN", "PERCENT", 50, 0, 0),
]


def seed_catalog(db):
    with db.transaction():
        for category, products in CATALOG:
            category_id = db.insert("categories", {"name": category})
            for name, variants in products:
                product_id = db.insert("products", {"category_id": category_id, "name": name})
                for size, price, stock in variants:
                    db.insert("product_variants", {
                        "product_id": product_id, "size": size, "price": price, "stock": stock})
        for code, kind, value, minimum, active in DISCOUNTS:
            db.insert("discounts", {
                "code": code, "type": kind, "value": value,
                "min_order_value": minimum, "active": active})


def seed_users(db):
    with db.transaction():
        for account, role in ((config.DEFAULT_OWNER, "OWNER"), (config.DEFAULT_STAFF, "STAFF")):
            db.insert("users", {
                "username": account["username"],
                "password_hash": hash_password(account["password"]),
                "full_name": account["full_name"],
                "role": role,
                "active": 1,
            })
