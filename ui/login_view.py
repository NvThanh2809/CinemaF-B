import tkinter as tk
from tkinter import ttk

from config import CINEMA_NAME
from ui.theme import C, F_BOLD, F_SMALL, FONT
from utils.exceptions import AppError


class LoginView(tk.Frame):
    """Màn hình đăng nhập: bên trái giới thiệu, bên phải biểu mẫu."""

    def __init__(self, master, auth, on_success, hint=""):
        """`auth` chỉ cần có hàm login(username, password) trả User (hoặc ném AppError).
        `hint`: dòng ghi chú nhỏ dưới tiêu đề (dùng cho chế độ đăng nhập thử), để trống thì không hiện."""
        super().__init__(master, bg=C["bg"])
        self._auth = auth
        self._on_success = on_success
        self._hint = hint

        self.columnconfigure(0, weight=5, uniform="c")
        self.columnconfigure(1, weight=6, uniform="c")
        self.rowconfigure(0, weight=1)
        self._build_brand_panel().grid(row=0, column=0, sticky="nsew")
        self._build_form_panel().grid(row=0, column=1, sticky="nsew")
        self._user_entry.focus_set()

    # ---------------------------------------------------------------- trái
    def _build_brand_panel(self):
        panel = tk.Frame(self, bg=C["sidebar"])
        box = tk.Frame(panel, bg=C["sidebar"])
        box.place(relx=0.5, rely=0.5, anchor="center")

        logo = tk.Canvas(box, width=84, height=84, bg=C["sidebar"], highlightthickness=0)
        logo.create_oval(2, 2, 82, 82, fill=C["primary"], outline="")
        logo.create_polygon(33, 24, 33, 60, 62, 42, fill="white", outline="")  # biểu tượng "play"
        logo.pack()
        tk.Label(box, text="CINEMA F&B", bg=C["sidebar"], fg="white", font=(FONT, 26, "bold")).pack(pady=(18, 2))
        tk.Label(box, text=CINEMA_NAME.title(), bg=C["sidebar"], fg=C["sidebar_text"],
                 font=(FONT, 11)).pack()
        tk.Frame(box, bg=C["primary"], height=3, width=48).pack(pady=18)
        for line in ("Bán đồ ăn, thức uống tại quầy nhanh chóng",
                     "Quản lý tài khoản và phân quyền",
                     "Theo dõi doanh số theo ngày, tháng, nhân viên"):
            tk.Label(box, text="•  " + line, bg=C["sidebar"], fg=C["sidebar_text"], font=(FONT, 10),
                     anchor="w").pack(fill="x", pady=3)
        return panel

    # ---------------------------------------------------------------- phải
    def _build_form_panel(self):
        panel = tk.Frame(self, bg=C["card"])
        form = ttk.Frame(panel, style="Card.TFrame")
        form.place(relx=0.5, rely=0.5, anchor="center", width=340)

        ttk.Label(form, text="Đăng nhập", style="Card.TLabel", font=(FONT, 22, "bold")).pack(anchor="w")
        ttk.Label(form, text="Nhập tài khoản được cấp để bắt đầu ca làm việc",
                  style="CardMuted.TLabel").pack(anchor="w", pady=(2, 22 if not self._hint else 10))
        if self._hint:
            tk.Label(form, text=self._hint, bg=C["card"], fg=C["warning"], font=F_SMALL, wraplength=340,
                     justify="left", anchor="w").pack(anchor="w", pady=(0, 14))

        ttk.Label(form, text="Tên đăng nhập", style="Card.TLabel", font=F_BOLD).pack(anchor="w")
        self._user = tk.StringVar()
        self._user_entry = ttk.Entry(form, textvariable=self._user, font=(FONT, 11))
        self._user_entry.pack(fill="x", pady=(4, 14))

        ttk.Label(form, text="Mật khẩu", style="Card.TLabel", font=F_BOLD).pack(anchor="w")
        self._pass = tk.StringVar()
        self._pass_entry = ttk.Entry(form, textvariable=self._pass, show="•", font=(FONT, 11))
        self._pass_entry.pack(fill="x", pady=(4, 6))

        self._show = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, text="Hiện mật khẩu", variable=self._show,
                        command=self._toggle_password).pack(anchor="w")

        self._error = ttk.Label(form, text="", style="Error.TLabel", wraplength=340, justify="left")
        self._error.pack(anchor="w", pady=(12, 0))

        self._button = ttk.Button(form, text="Đăng nhập", style="Big.Primary.TButton", command=self._login)
        self._button.pack(fill="x", pady=(10, 0))

        for entry in (self._user_entry, self._pass_entry):
            entry.bind("<Return>", lambda e: self._login())
            entry.bind("<Key>", lambda e: self._error.config(text=""), add="+")
        return panel

    def _toggle_password(self):
        self._pass_entry.config(show="" if self._show.get() else "•")

    def _login(self):
        try:
            user = self._auth.login(self._user.get(), self._pass.get())
        except AppError as exc:
            self._error.config(text=str(exc))
            self._pass.set("")
            self._pass_entry.focus_set()
            return
        self._pass.set("")
        self._on_success(user)
