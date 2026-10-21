import tkinter as tk
from tkinter import messagebox, ttk

from ui.helpers import BaseDialog
from ui.theme import C
from utils.invoice_printer import open_invoice, render_invoice_text, save_invoice


class InvoiceView(BaseDialog):
    def __init__(self, master, order):
        super().__init__(master, f"Hóa đơn #{order.id:06d}")
        self._path = None
        self._save_error = None
        try:
            self._path = save_invoice(order)
        except OSError as exc:
            self._save_error = exc

        card = ttk.Frame(self, style="Card.TFrame", padding=(18, 16))
        card.pack(fill="both", expand=True, padx=14, pady=14)

        paper = tk.Text(
            card, width=54, height=24, font=("Consolas", 10), wrap="none", relief="flat",
            bg=C["stripe"], highlightthickness=1, highlightbackground=C["border"], padx=10, pady=10,
        )
        paper.insert("1.0", render_invoice_text(order))
        paper.config(state="disabled")
        paper.pack(fill="both", expand=True)

        if self._path is not None:
            status = f"Đã lưu: {self._path}"
        else:
            status = f"Không lưu được file hóa đơn: {self._save_error}"
        ttk.Label(card, text=status, style="CardMuted.TLabel", wraplength=430).pack(anchor="w", pady=(8, 0))

        buttons = ttk.Frame(card, style="Card.TFrame")
        buttons.pack(fill="x", pady=(10, 0))
        ttk.Button(buttons, text="Đóng", command=self.destroy).pack(side="right")
        print_button = ttk.Button(buttons, text="In hóa đơn", style="Primary.TButton",
                                  command=lambda: self._open(True))
        print_button.pack(side="right", padx=8)
        open_button = ttk.Button(buttons, text="Mở file", command=lambda: self._open(False))
        open_button.pack(side="right")
        if self._path is None:
            print_button.state(["disabled"])
            open_button.state(["disabled"])

        self.bind("<Escape>", lambda e: self.destroy())
        self.present()

    def _open(self, print_it):
        try:
            open_invoice(self._path, print_it=print_it)
        except Exception as exc:
            messagebox.showerror(
                "Không thể mở",
                f"{exc}\n\nBạn có thể mở thủ công file:\n{self._path}",
                parent=self,
            )
