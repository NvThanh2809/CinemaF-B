"""Băm và kiểm tra mật khẩu (PBKDF2-HMAC-SHA256, thư viện chuẩn)."""
import hashlib
import hmac
import os

SCHEME = "pbkdf2_sha256"
ITERATIONS = 200_000  # test có thể hạ xuống cho nhanh; số vòng lặp được lưu kèm trong chuỗi băm


def hash_password(password, iterations=None):
    iterations = iterations or ITERATIONS
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{SCHEME}${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    try:
        scheme, iterations, salt_hex, digest_hex = stored.split("$")
        if scheme != SCHEME:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, AttributeError):
        return False
