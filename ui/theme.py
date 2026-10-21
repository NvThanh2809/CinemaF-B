"""Màu sắc, phông chữ và style ttk dùng chung cho toàn bộ giao diện."""
import sys
import tkinter as tk
from tkinter import ttk

C = {
    "bg": "#f1f5f9",              # nền trang
    "card": "#ffffff",            # nền thẻ
    "border": "#e2e8f0",
    "text": "#0f172a",
    "muted": "#64748b",
    "primary": "#2563eb",         # SỬ DỤNG CHO: Thành tiền, Nút primary
    "primary_dark": "#1d4ed8",
    "primary_soft": "#dbeafe",
    "danger": "#dc2626",
    "danger_dark": "#b91c1c",
    "success": "#16a34a",
    "warning": "#d97706",
    "stripe": "#f8fafc",
    "sidebar": "#0f172a",
    "sidebar_hover": "#1e293b",
    "sidebar_text": "#cbd5e1",
    "sidebar_muted": "#64748b",
    "sidebar_line": "#1e293b",    # vạch ngăn trong thanh bên
    "avatar": "#334155",          # nền ảnh đại diện chữ cái
    "total_row": "#e0e7ff",       # nền dòng tổng của bảng
    "chart_axis": "#94a3b8",      # SỬ DỤNG CHO: trục biểu đồ
    "chart_tooltip": "#1e293b",   # SỬ DỤNG CHO: nền tooltip biểu đồ (Bổ sung theo yêu cầu)
    "invoice_bg": "#fffef7",      # SỬ DỤNG CHO: nền giấy hóa đơn (Thành viên B cần)
    "stat_card": "#7c3aed"        # SỬ DỤNG CHO: thẻ số liệu (Thành viên C cần)
}

# Chọn phông theo hệ điều hành (cả 3 đều hiển thị đủ tiếng Việt có dấu)
if sys.platform.startswith("win"):
    FONT = "Segoe UI"
elif sys.platform == "darwin":
    FONT = "Helvetica Neue"
else:
    FONT = "DejaVu Sans"

F_BASE = (FONT, 10)
F_BOLD = (FONT, 10, "bold")
F_SMALL = (FONT, 9)
F_TITLE = (FONT, 20, "bold")
F_H2 = (FONT, 13, "bold")
F_BIG = (FONT, 22, "bold")
F_HUGE = (FONT, 28, "bold")

def setup_styles(root: tk.Tk):
    root.configure(bg=C["bg"])
    root.option_add("*Font", F_BASE)
    root.option_add("*TCombobox*Listbox.font", F_BASE)
    root.option_add("*TCombobox*Listbox.selectBackground", C["primary"])

    s = ttk.Style(root)
    try:
        s.theme_use("clam")
    except Exception:
        pass

    s.configure(".", font=F_BASE, background=C["bg"], foreground=C["text"])
    s.configure("TFrame", background=C["bg"])
    s.configure("Card.TFrame", background=C["card"])
    s.configure("TLabel", background=C["bg"], foreground=C["text"])
    s.configure("Card.TLabel", background=C["card"], foreground=C["text"])
    s.configure("Muted.TLabel", background=C["bg"], foreground=C["muted"])
    s.configure("CardMuted.TLabel", background=C["card"], foreground=C["muted"], font=F_SMALL)
    s.configure("Title.TLabel", background=C["bg"], font=F_TITLE)
    s.configure("H2.TLabel", background=C["card"], font=F_H2)
    s.configure("Error.TLabel", background=C["card"], foreground=C["danger"], font=F_SMALL)
    s.configure("Success.TLabel", background=C["card"], foreground=C["success"])

    # Nút (Fix hardcode colors)
    s.configure("TButton", padding=(14, 7), relief="flat", borderwidth=0,
                background=C["border"], foreground=C["text"], focuscolor="none")
    s.map("TButton",
          background=[("disabled", C["bg"]), ("pressed", C["sidebar_text"]), ("active", C["primary_soft"])],
          foreground=[("disabled", C["chart_axis"])])

    s.configure("Primary.TButton", background=C["primary"], foreground="white", font=F_BOLD)
    s.map("Primary.TButton",
          background=[("disabled", "#93c5fd"), ("pressed", "#1e40af"), ("active", C["primary_dark"])],
          foreground=[("disabled", "white")])

    s.configure("Danger.TButton", background=C["danger"], foreground="white", font=F_BOLD)
    s.map("Danger.TButton",
          background=[("disabled", "#fca5a5"), ("pressed", "#991b1b"), ("active", C["danger_dark"])],
          foreground=[("disabled", "white")])

    s.configure("Big.Primary.TButton", padding=(14, 12), font=(FONT, 12, "bold"))

    # Ô nhập (Fix hardcode colors)
    for name in ("TEntry", "TCombobox", "TSpinbox"):
        s.configure(name, padding=6, fieldbackground="white", bordercolor=C["border"],
                    lightcolor=C["border"], darkcolor=C["border"], borderwidth=1, arrowsize=14)
        s.map(name, bordercolor=[("focus", C["primary"])], lightcolor=[("focus", C["primary"])],
              darkcolor=[("focus", C["primary"])])

    s.map("TCombobox", fieldbackground=[("readonly", "white")], selectbackground=[("readonly", "white")],
          selectforeground=[("readonly", C["text"])])

    s.configure("TRadiobutton", background=C["card"], focuscolor="none")
    s.configure("TCheckbutton", background=C["card"], focuscolor="none")
    s.configure("Bg.TRadiobutton", background=C["bg"])

    # Bảng (Fix hardcode colors)
    s.configure("Treeview", rowheight=32, font=F_BASE, background="white", fieldbackground="white",
                borderwidth=0, relief="flat")
    s.configure("Treeview.Heading", font=F_BOLD, background=C["bg"], foreground=C["muted"],
                relief="flat", padding=(8, 8), borderwidth=0)
    s.map("Treeview.Heading", background=[("active", C["border"])])
    s.map("Treeview", background=[("selected", C["primary_soft"])], foreground=[("selected", C["text"])])
    s.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})]) # bỏ viền ngoài

    # Tab (Fix hardcode colors)
    s.configure("TNotebook", background=C["bg"], borderwidth=0, tabmargins=(0, 0, 0, 0))
    s.configure("TNotebook.Tab", padding=(18, 9), font=F_BOLD, background=C["border"], foreground=C["muted"],
                borderwidth=0)
    s.map("TNotebook.Tab", background=[("selected", C["card"])], foreground=[("selected", C["primary"])])

    # Scrollbar (Fix hardcode colors)
    s.configure("Vertical.TScrollbar", background=C["sidebar_text"], troughcolor=C["bg"], borderwidth=0, arrowsize=12)

    return s
