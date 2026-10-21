import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from models.order import Order
from models.order_detail import OrderDetail
from utils import invoice_printer
from utils.invoice_printer import render_invoice_text, save_invoice


def make_order(discount_amount=10000, discount_code="GIAM10"):
    return Order(
        id=7,
        created_at=datetime(2026, 10, 9, 16, 40, 0),
        total_amount=100000,
        discount_amount=discount_amount,
        final_amount=100000 - discount_amount,
        discount_code=discount_code,
        seller_name="Lê Thu Ngân",
        details=[OrderDetail(2, "Bỏng ngô phô mai", "L", 50000, 2)],
    )


class InvoiceTest(unittest.TestCase):
    def test_invoice_contains_all_lines(self):
        text = render_invoice_text(make_order())
        for expected in ("000007", "09/10/2026 16:40:00", "Lê Thu Ngân", "Bỏng ngô phô mai (L)",
                         "2 x 50.000đ", "100.000đ", "GIAM10", "-10.000đ", "90.000đ"):
            self.assertIn(expected, text)

    def test_invoice_without_discount_has_no_discount_line(self):
        text = render_invoice_text(make_order(discount_amount=0, discount_code=None))
        self.assertNotIn("Giảm giá", text)
        self.assertIn("THANH TOÁN:", text)

    def test_save_invoice_writes_utf8_file(self):
        with tempfile.TemporaryDirectory() as folder:
            with mock.patch.object(invoice_printer, "INVOICE_DIR", Path(folder)):
                path = save_invoice(make_order())
            self.assertEqual(path.name, "hoadon_000007.txt")
            self.assertIn("Bỏng ngô phô mai", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
