"""Test của phần hạ tầng đã làm sẵn (CSDL, dữ liệu mẫu, tiện ích). Các test này PHẢI xanh ngay từ đầu.

Dùng làm mẫu: cách dựng `Env`, cách kiểm tra bằng SQL trực tiếp, cách kiểm tra rollback.
Nếu một test ở đây đỏ nghĩa là có người vừa làm hỏng phần dùng chung: báo cả nhóm trước khi sửa.
"""
import unittest

from app_context import DevLoginAuth
from tests.helpers import Env
from utils.exceptions import AuthError
from utils.dates import day_bounds, parse_date
from utils.formatter import format_money, short_money
from utils.security import hash_password, verify_password
from utils.text import normalize


class SeedDataTest(unittest.TestCase):
    def setUp(self):
        self.env = Env(login_as=None)

    def tearDown(self):
        self.env.close()

    def _count(self, table):
        return self.env.db.scalar(f"SELECT COUNT(*) FROM {table}")

    def test_catalog_and_accounts_are_seeded(self):
        self.assertEqual(self._count("categories"), 4)
        self.assertEqual(self._count("products"), 11)
        self.assertEqual(self._count("product_variants"), 20)
        self.assertEqual(self._count("discounts"), 4)
        self.assertEqual(self._count("users"), 2)
        self.assertEqual(self._count("orders"), 0)

    def test_default_accounts_have_expected_roles_and_hashed_passwords(self):
        rows = {r["username"]: r for r in self.env.db.query("SELECT username, role, password_hash FROM users")}
        self.assertEqual(rows["admin"]["role"], "OWNER")
        self.assertEqual(rows["nhanvien"]["role"], "STAFF")
        self.assertNotIn("admin123", rows["admin"]["password_hash"])  # không lưu mật khẩu gốc


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.env = Env(login_as=None)
        self.db = self.env.db

    def tearDown(self):
        self.env.close()

    def test_transaction_rolls_back_on_error(self):
        before = self.db.scalar("SELECT COUNT(*) FROM categories")
        with self.assertRaises(RuntimeError):
            with self.db.transaction():
                self.db.insert("categories", {"name": "Tạm"})
                raise RuntimeError("giả lập lỗi giữa chừng")
        self.assertEqual(self.db.scalar("SELECT COUNT(*) FROM categories"), before)

    def test_transaction_commits_when_ok_and_insert_returns_new_id(self):
        with self.db.transaction():
            new_id = self.db.insert("categories", {"name": "Kem"})
        self.assertEqual(self.db.scalar("SELECT name FROM categories WHERE id = ?", (new_id,)), "Kem")

    def test_dev_login_helper_signs_in_without_auth_service(self):
        env = Env("nhanvien")
        try:
            self.assertEqual(env.auth.require_login().username, "nhanvien")
            self.assertFalse(env.auth.current_user.is_owner)
        finally:
            env.close()


class DevLoginAnyNameTest(unittest.TestCase):
    """DEV_LOGIN = "ANY": màn hình đăng nhập nhận mọi tên, không kiểm tra mật khẩu."""

    def setUp(self):
        self.env = Env(login_as=None)
        self.dev = DevLoginAuth(self.env)  # Env có .db và .auth giống AppContext

    def tearDown(self):
        self.env.close()

    def test_any_name_becomes_staff_with_typed_name(self):
        user = self.dev.login("  Lan  ", "")
        self.assertEqual(user.username, "Lan")
        self.assertFalse(user.is_owner)
        self.assertIs(self.env.auth.require_login(), user)

    def test_admin_name_is_owner(self):
        self.assertTrue(self.dev.login("Admin", "bat-ky").is_owner)

    def test_empty_name_is_rejected(self):
        with self.assertRaises(AuthError):
            self.dev.login("   ", "x")

    def test_borrowed_user_id_exists_for_orders_foreign_key(self):
        user = self.dev.login("ai-do", "")
        self.assertEqual(self.env.db.scalar("SELECT COUNT(*) FROM users WHERE id = ?", (user.id,)), 1)


class UtilsTest(unittest.TestCase):
    def test_money_formats(self):
        self.assertEqual(format_money(50000), "50.000đ")
        self.assertEqual(format_money(1234567), "1.234.567đ")
        self.assertEqual(short_money(1500000), "1,5tr")
        self.assertEqual(short_money(50000), "50k")

    def test_password_hash_roundtrip(self):
        hashed = hash_password("matkhau123")
        self.assertTrue(verify_password("matkhau123", hashed))
        self.assertFalse(verify_password("sai-roi", hashed))
        self.assertNotEqual(hashed, hash_password("matkhau123"))  # mỗi lần băm có salt khác nhau

    def test_normalize_removes_vietnamese_accents(self):
        self.assertEqual(normalize("Bỏng NGÔ Phô Mai"), "bong ngo pho mai")
        self.assertEqual(normalize("Đồ ăn nhẹ"), "do an nhe")

    def test_date_helpers(self):
        self.assertEqual(parse_date("09/10/2026").isoformat(), "2026-10-09")
        with self.assertRaises(ValueError):
            parse_date("31/02/2026")
        start, end = day_bounds(parse_date("01/10/2026"), parse_date("02/10/2026"))
        self.assertEqual((start, end), ("2026-10-01 00:00:00", "2026-10-03 00:00:00"))  # nửa mở: gồm cả ngày cuối


if __name__ == "__main__":
    unittest.main()
