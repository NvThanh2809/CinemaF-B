import tkinter as tk
from tkinter import ttk

from ui.theme import C


def center_on_parent(win, parent):
    """Đặt cửa sổ con vào giữa cửa sổ cha."""
    win.update_idletasks()
    top = parent.winfo_toplevel()
    x = top.winfo_rootx() + (top.winfo_width() - win.winfo_reqwidth()) // 2
    y = top.winfo_rooty() + (top.winfo_height() - win.winfo_reqheight()) // 2
    win.geometry(f"+{max(x, 0)}+{max(y, 0)}")


def center_window(win, width, height):
    win.update_idletasks()
    x = (win.winfo_screenwidth() - width) // 2
    y = max((win.winfo_screenheight() - height) // 2 - 20, 0)
    win.geometry(f"{width}x{height}+{x}+{y}")


class BaseDialog(tk.Toplevel):
    """Hộp thoại modal: nền đồng bộ theme, đặt giữa cửa sổ cha. Lớp con gọi self.present() sau khi dựng xong."""

    def __init__(self, master, title):
        super().__init__(master, bg=C["bg"])
        self.title(title)
        self.resizable(False, False)
        self.withdraw()
        self._parent = master

    def present(self):
        self.transient(self._parent.winfo_toplevel())
        center_on_parent(self, self._parent)
        self.deiconify()
        self.wait_visibility()
        self.grab_set()
        self.focus_set()


class FormDialog(BaseDialog):
    """Khung hộp thoại biểu mẫu: lớp con dựng `build(body)` và `collect()`.

    `submit(data)` do bên gọi truyền vào; nếu ném AppError thì lỗi hiện ngay trong hộp thoại
    và hộp thoại vẫn mở để người dùng sửa. Thành công thì hộp thoại đóng, self.saved = True.
    """

    submit_text = "Lưu"

    def __init__(self, master, title, submit):
        super().__init__(master, title)
        self._submit = submit
        self.saved = False

        card = ttk.Frame(self, style="Card.TFrame", padding=(22, 20))
        card.pack(fill="both", expand=True, padx=14, pady=14)
        ttk.Label(card, text=title, style="H2.TLabel").pack(anchor="w", pady=(0, 12))
        self.body = ttk.Frame(card, style="Card.TFrame")
        self.body.pack(fill="x")
        self.body.columnconfigure(1, weight=1)
        self._row = 0

        self._error = ttk.Label(card, text="", style="Error.TLabel", wraplength=380, justify="left")
        self._error.pack(anchor="w", pady=(10, 0))
        buttons = ttk.Frame(card, style="Card.TFrame")
        buttons.pack(fill="x", pady=(12, 0))
        self._ok = ttk.Button(buttons, text=self.submit_text, style="Primary.TButton", command=self._on_submit)
        self._ok.pack(side="right")
        ttk.Button(buttons, text="Hủy", command=self.destroy).pack(side="right", padx=(0, 8))
        self.bind("<Return>", lambda e: self._on_submit())
        self.bind("<Escape>", lambda e: self.destroy())

    # ---- tiện ích dựng form ----
    def add_field(self, label, widget_factory, hint=""):
        ttk.Label(self.body, text=label, style="Card.TLabel").grid(row=self._row, column=0, sticky="w",
                                                                    padx=(0, 16), pady=6)
        widget = widget_factory(self.body)
        widget.grid(row=self._row, column=1, sticky="ew", pady=6)
        self._row += 1
        if hint:
            ttk.Label(self.body, text=hint, style="CardMuted.TLabel").grid(
                row=self._row, column=1, sticky="w", pady=(0, 4))
            self._row += 1
        return widget

    def collect(self):
        raise NotImplementedError

    def show_error(self, message):
        self._error.config(text=message)

    def _on_submit(self):
        from utils.exceptions import AppError
        try:
            self._submit(self.collect())
        except AppError as exc:
            self.show_error(str(exc))
            return
        self.saved = True
        self.destroy()
