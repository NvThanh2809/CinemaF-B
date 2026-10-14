"""Test cho utils/invoice_printer.py (nội dung hóa đơn .txt).

Người phụ trách: THÀNH VIÊN B.
Dựng một Order thủ công với models.order.Order và OrderDetail rồi gọi render_invoice_text.

Cách làm: mỗi test bên dưới là MỘT hành vi cần kiểm tra. Viết xong test nào thì xóa dòng @TODO của test đó
và thay phần mô tả bằng code kiểm tra thật. Chạy: python -m unittest discover -s tests -t .
"""
import unittest

from tests.helpers import Env

TODO = unittest.skip("TODO (B): chưa viết test này")


class InvoiceTest(unittest.TestCase):
    def setUp(self):
        self.env = Env()

    def tearDown(self):
        self.env.close()

    @TODO
    def test_invoice_contains_all_lines(self):
        """Hóa đơn có số HĐ, ngày giờ, từng dòng hàng, tổng tiền, dòng giảm giá kèm mã, số tiền thanh toán."""

    @TODO
    def test_invoice_without_discount_has_no_discount_line(self):
        """Đơn không dùng mã thì không in dòng 'Giảm giá'."""

    @TODO
    def test_save_invoice_writes_utf8_file(self):
        """save_invoice ghi file hoadon_<id>.txt (UTF-8, giữ đủ dấu tiếng Việt) và trả về đường dẫn."""


if __name__ == "__main__":
    unittest.main()
