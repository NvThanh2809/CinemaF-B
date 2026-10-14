from tkinter import messagebox, ttk

from ui.widgets import Card

WEEKDAYS = ["Thứ hai", "Thứ ba", "Thứ tư", "Thứ năm", "Thứ sáu", "Thứ bảy", "Chủ nhật"]


class Page(ttk.Frame):
    """Lớp cha của các trang trong dashboard. Shell giữ lại trang đã tạo và gọi on_show() mỗi lần mở trang."""

    def __init__(self, master, ctx, shell):
        super().__init__(master, padding=(28, 22))
        self.ctx = ctx
        self.shell = shell

    def on_show(self):
        """Nạp lại dữ liệu khi trang được mở."""

    def has_unsaved_work(self):
        return False

    def warn(self, title, message):
        messagebox.showwarning(title, str(message), parent=self)

    def show_todo(self, owner, items):
        """Khung tạm cho trang chưa code: hiện người phụ trách và việc cần làm.

        Khi code trang thật thì XÓA lời gọi này (và các dòng TODO).
        """
        card = Card(self, padding=(26, 22))
        card.pack(fill="both", expand=True, pady=(16, 0))
        ttk.Label(card.inner, text=f"Trang này do thành viên {owner} phụ trách", style="H2.TLabel").pack(anchor="w")
        ttk.Label(card.inner, text="Chưa code. Việc cần làm:", style="CardMuted.TLabel").pack(anchor="w", pady=(4, 12))
        for item in items:
            ttk.Label(card.inner, text="•  " + item, style="Card.TLabel", wraplength=760,
                      justify="left").pack(anchor="w", pady=3)
