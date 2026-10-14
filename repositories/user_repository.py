"""Truy vấn SQL cho tài khoản người dùng.

Người phụ trách: THÀNH VIÊN C.
Bảng users(id, username, password_hash, full_name, role ['OWNER'|'STAFF'], active, created_at).
"""
from models.user import User  # noqa: F401  (C dùng khi code)


class UserRepository:
    def __init__(self, db):
        self._db = db

    def find_by_username(self, username):
        """TODO (C): trả về User (kèm password_hash) hoặc None."""
        raise NotImplementedError("TODO (C): UserRepository.find_by_username")

    def find_by_id(self, user_id):
        """TODO (C): trả về User hoặc None."""
        raise NotImplementedError("TODO (C): UserRepository.find_by_id")

    def list_all(self):
        """TODO (C): list[User], chủ cửa hàng (OWNER) xếp trước, rồi theo họ tên."""
        raise NotImplementedError("TODO (C): UserRepository.list_all")

    def order_counts(self):
        """TODO (C): {user_id: số đơn đã lập} (GROUP BY trên bảng orders)."""
        raise NotImplementedError("TODO (C): UserRepository.order_counts")

    def count_orders(self, user_id):
        """TODO (C): số đơn của một tài khoản (để quyết định xóa hẳn hay chỉ khóa)."""
        raise NotImplementedError("TODO (C): UserRepository.count_orders")

    def count_active_owners(self, exclude_id=None):
        """TODO (C): số chủ cửa hàng đang hoạt động, có thể loại trừ một id."""
        raise NotImplementedError("TODO (C): UserRepository.count_active_owners")

    def insert(self, username, password_hash, full_name, role):
        """TODO (C): thêm tài khoản, trả về id mới."""
        raise NotImplementedError("TODO (C): UserRepository.insert")

    def update(self, user_id, full_name, role, active):
        raise NotImplementedError("TODO (C): UserRepository.update")

    def update_password(self, user_id, password_hash):
        raise NotImplementedError("TODO (C): UserRepository.update_password")

    def delete(self, user_id):
        raise NotImplementedError("TODO (C): UserRepository.delete")
