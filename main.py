"""Điểm khởi chạy: python main.py"""
import tkinter as tk
from tkinter import messagebox

from app_context import build_context
from database.connection import connect, init_db
from ui.app import App
from utils.exceptions import DatabaseConnectionError


def main():
    root = tk.Tk()
    root.withdraw()
    try:
        db = connect()
        init_db(db)
    except DatabaseConnectionError as exc:
        messagebox.showerror("Không kết nối được cơ sở dữ liệu", str(exc))
        return
    ctx = build_context(db)
    root.deiconify()
    App(root, ctx)
    root.mainloop()
    db.close()


if __name__ == "__main__":
    main()
