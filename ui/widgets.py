"""Các thành phần giao diện dùng lại: thẻ, bảng, biểu đồ cột, thanh chọn khoảng ngày..."""
import tkinter as tk
from tkinter import ttk

from ui.theme import C, F_BASE, F_BIG, F_BOLD, F_H2, F_SMALL, F_TITLE, FONT
from utils.dates import add_months, first_of_month, format_date, month_start_end, parse_date
from utils.formatter import format_money, short_money

from datetime import date, timedelta


class Card(tk.Frame):
    """Khung trắng có viền mảnh."""

    def __init__(self, master, padding=14, **kw):
        super().__init__(master, bg=C["card"], highlightbackground=C["border"],
                         highlightcolor=C["border"], highlightthickness=1, **kw)
        self.inner = ttk.Frame(self, style="Card.TFrame", padding=padding)
        self.inner.pack(fill="both", expand=True)


class StatCard(Card):
    """Thẻ số liệu: tiêu đề nhỏ, số lớn, ghi chú."""

    def __init__(self, master, title, accent=None):
        super().__init__(master, padding=(16, 12))
        tk.Frame(self, bg=accent or C["primary"], width=4).place(x=0, y=0, relheight=1)
        ttk.Label(self.inner, text=title, style="CardMuted.TLabel").pack(anchor="w")
        self._value = ttk.Label(self.inner, text="-", style="Card.TLabel", font=F_BIG)
        self._value.pack(anchor="w", pady=(2, 0))
        self._note = ttk.Label(self.inner, text="", style="CardMuted.TLabel")
        self._note.pack(anchor="w")

    def set(self, value, note=""):
        self._value.config(text=value)
        self._note.config(text=note)


class PageHeader(ttk.Frame):
    """Tiêu đề trang + dòng mô tả; `actions` là khung bên phải để đặt nút."""

    def __init__(self, master, title, subtitle=""):
        super().__init__(master)
        left = ttk.Frame(self)
        left.pack(side="left")
        ttk.Label(left, text=title, style="Title.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(left, text=subtitle, style="Muted.TLabel").pack(anchor="w")
        self.actions = ttk.Frame(self)
        self.actions.pack(side="right")


class DataTable(ttk.Frame):
    """Treeview có thanh cuộn và tô xen kẽ dòng. columns = [(key, tiêu đề, độ rộng, căn lề)]."""

    def __init__(self, master, columns, height=10, selectmode="browse"):
        super().__init__(master, style="Card.TFrame")
        self.keys = [c[0] for c in columns]
        self.tree = ttk.Treeview(self, columns=self.keys, show="headings", height=height, selectmode=selectmode)
        for key, title, width, anchor in columns:
            self.tree.heading(key, text=title, anchor="w" if anchor == "w" else "e" if anchor == "e" else "center")
            self.tree.column(key, width=width, anchor=anchor, minwidth=40)
        self.tree.tag_configure("odd", background=C["stripe"])
        self.tree.tag_configure("total", background=C["total_row"], font=F_BOLD)
        self.tree.tag_configure("muted", foreground=C["muted"])
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self._count = 0

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        self._count = 0

    def add(self, values, iid=None, tags=()):
        tags = tuple(tags)
        if self._count % 2 == 1 and "total" not in tags:
            tags += ("odd",)
        self.tree.insert("", "end", iid=iid, values=values, tags=tags)
        self._count += 1

    def selected(self):
        sel = self.tree.selection()
        return sel[0] if sel else None


def _nice_max(value):
    """Làm tròn lên mốc 'đẹp' (1, 2, 2.5, 5, 10 x 10^k) cho trục tung."""
    if value <= 0:
        return 1
    magnitude = 10 ** (len(str(int(value))) - 1)
    for step in (1, 2, 2.5, 5, 10):
        if value <= step * magnitude:
            return step * magnitude
    return 10 * magnitude


class BarChart(tk.Canvas):
    """Biểu đồ cột đơn giản vẽ bằng Canvas, có đường lưới, nhãn trục và tooltip khi rê chuột."""

    PAD_L, PAD_R, PAD_T, PAD_B = 56, 14, 14, 30

    def __init__(self, master, height=220, color=None, empty_text="Chưa có dữ liệu"):
        super().__init__(master, height=height, bg=C["card"], highlightthickness=0)
        self._color = color or C["primary"]
        self._empty_text = empty_text
        self._labels, self._values, self._tips = [], [], []
        self._bars = []
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", lambda e: self.delete("tip"))

    def set_data(self, labels, values, tips=None):
        self._labels, self._values = list(labels), list(values)
        self._tips = list(tips) if tips else [f"{l}: {format_money(v)}" for l, v in zip(labels, values)]
        self._draw()

    def _draw(self):
        self.delete("all")
        self._bars = []
        w, h = self.winfo_width(), self.winfo_height()
        if w < 50 or h < 50:
            return
        if not self._values or max(self._values) <= 0:
            self.create_text(w / 2, h / 2, text=self._empty_text, fill=C["muted"], font=F_BASE)
            return
        left, right, top, bottom = self.PAD_L, w - self.PAD_R, self.PAD_T, h - self.PAD_B
        axis_max = _nice_max(max(self._values))
        for i in range(5):  # đường lưới + nhãn trục tung
            y = bottom - (bottom - top) * i / 4
            self.create_line(left, y, right, y, fill=C["border"])
            self.create_text(left - 8, y, text=short_money(axis_max * i / 4), anchor="e",
                             fill=C["muted"], font=F_SMALL)
        n = len(self._values)
        slot = (right - left) / n
        bar_w = max(2, min(48, slot * 0.62))
        fit = max(1, int((right - left) / 52))  # số nhãn tối đa đặt vừa trên trục (mỗi nhãn rộng ~52px)
        label_every = max(1, -(-n // fit))      # làm tròn LÊN để các nhãn không đè lên nhau
        for i, (label, value) in enumerate(zip(self._labels, self._values)):
            cx = left + slot * (i + 0.5)
            y = bottom - (bottom - top) * value / axis_max
            if value > 0:
                self.create_rectangle(cx - bar_w / 2, y, cx + bar_w / 2, bottom, fill=self._color, width=0)
            self._bars.append((cx - slot / 2, cx + slot / 2, i))
            if i % label_every == 0:
                self.create_text(cx, bottom + 14, text=label, fill=C["muted"], font=F_SMALL)
        self.create_line(left, bottom, right, bottom, fill=C["chart_axis"])

    def _on_motion(self, event):
        self.delete("tip")
        for x0, x1, i in self._bars:
            if x0 <= event.x < x1:
                text = self._tips[i]
                t = self.create_text(0, 0, text=text, fill="white", font=F_SMALL, tags="tip")
                x0_, y0_, x1_, y1_ = self.bbox(t)
                w = self.winfo_width()
                tx = min(max(event.x, (x1_ - x0_) / 2 + 10), w - (x1_ - x0_) / 2 - 10)
                ty = max(event.y - 22, 14)
                self.coords(t, tx, ty)
                bx0, by0, bx1, by1 = self.bbox(t)
                rect = self.create_rectangle(bx0 - 8, by0 - 4, bx1 + 8, by1 + 4, fill=C["sidebar_line"], width=0, tags="tip")
                self.tag_raise(t, rect)
                return


class DateRangeBar(ttk.Frame):
    """Chọn khoảng ngày (dd/mm/yyyy) + các nút chọn nhanh. Gọi `on_apply()` khi bấm Xem / nút chọn nhanh."""

    def __init__(self, master, on_apply, default="month", style="TFrame"):
        super().__init__(master, style=style)
        self._on_apply = on_apply
        self._bg = "Card.TLabel" if style == "Card.TFrame" else "TLabel"
        self._from, self._to = tk.StringVar(), tk.StringVar()

        ttk.Label(self, text="Từ ngày", style=self._bg).pack(side="left")
        self._e_from = ttk.Entry(self, textvariable=self._from, width=11, justify="center")
        self._e_from.pack(side="left", padx=(6, 10))
        ttk.Label(self, text="đến", style=self._bg).pack(side="left")
        self._e_to = ttk.Entry(self, textvariable=self._to, width=11, justify="center")
        self._e_to.pack(side="left", padx=(6, 10))
        for entry in (self._e_from, self._e_to):
            entry.bind("<Return>", lambda e: self._on_apply())
        ttk.Button(self, text="Xem", style="Primary.TButton", command=lambda: self._on_apply()).pack(side="left")

        self._quick = ttk.Frame(self, style=style)
        self._quick.pack(side="left", padx=(14, 0))
        for text, key in (("Hôm nay", "today"), ("7 ngày", "week"), ("Tháng này", "month"),
                          ("Tháng trước", "prev_month"), ("Năm nay", "year")):
            ttk.Button(self._quick, text=text, padding=(10, 6),
                       command=lambda k=key: self.preset(k)).pack(side="left", padx=2)
        self.preset(default, apply=False)

    def preset(self, key, apply=True):
        today = date.today()
        if key == "today":
            start = end = today
        elif key == "week":
            start, end = today - timedelta(days=6), today
        elif key == "month":
            start, end = first_of_month(today), today
        elif key == "prev_month":
            start, end = month_start_end(add_months(first_of_month(today), -1))
        elif key == "year":
            start, end = date(today.year, 1, 1), today
        else:
            raise ValueError(key)
        self.set_range(start, end)
        if apply:
            self._on_apply()

    def set_range(self, start, end):
        self._from.set(format_date(start))
        self._to.set(format_date(end))

    def get_range(self):
        """(start, end) hoặc ném ValueError với thông báo tiếng Việt."""
        start, end = parse_date(self._from.get()), parse_date(self._to.get())
        if start > end:
            raise ValueError("Ngày bắt đầu phải trước hoặc bằng ngày kết thúc")
        return start, end
