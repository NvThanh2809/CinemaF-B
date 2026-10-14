"""Xử lý chuỗi tiếng Việt."""
import unicodedata


def normalize(text):
    """Bỏ dấu + chữ thường, để tìm 'bong ngo' vẫn ra 'Bỏng ngô'."""
    text = (text or "").lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn").strip()


def like_escape(text):
    """Escape ký tự đặc biệt của LIKE (dùng với ESCAPE '\\')."""
    for ch in ("\\", "%", "_", "["):
        text = text.replace(ch, "\\" + ch)
    return text
