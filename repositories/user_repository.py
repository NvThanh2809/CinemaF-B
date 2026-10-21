from models.user import User, Role

_COLUMNS = "id, username, password_hash, full_name, role, active, created_at"
# Truy vấn SQL cho tài khoản người dùng.
def _to_user(row):
    # Một dòng bảng users (dict) -> đối tượng User
    return User(row["id"], row["username"], row["full_name"], row["role"],
                bool(row["active"]), row["created_at"], row["password_hash"])

class UserRepository:
    def __init__(self, db):
        self._db = db

    def find_by_username(self, username):
        row = self._db.query_one(
            f"SELECT {_COLUMNS} FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        return _to_user(row) if row else None

    def find_by_id(self, user_id):
        row = self._db.query_one(f"SELECT {_COLUMNS} FROM users WHERE id = ?", (user_id,))
        return _to_user(row) if row else None

    def list_all(self):
        rows = self._db.query(
            f"SELECT {_COLUMNS} FROM users "
            "ORDER BY CASE WHEN role = 'OWNER' THEN 0 ELSE 1 END, full_name")
        return [_to_user(r) for r in rows]

    def order_counts(self):
        rows = self._db.query("SELECT user_id, COUNT(*) AS n FROM orders GROUP BY user_id")
        return {r["user_id"]: r["n"] for r in rows}

    def count_orders(self, user_id):
        return self._db.scalar("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,), 0)

    def count_active_owners(self, exclude_id=None):
        sql = "SELECT COUNT(*) FROM users WHERE role = ? AND active = 1"
        params = [Role.OWNER]
        if exclude_id is not None:
            sql += " AND id <> ?"
            params.append(exclude_id)
        return self._db.scalar(sql, params, 0)

    def insert(self, username, password_hash, full_name, role):
        return self._db.insert("users", {
            "username": username, "password_hash": password_hash,
            "full_name": full_name, "role": role, "active": 1})

    def update(self, user_id, full_name, role, active):
        self._db.execute(
            "UPDATE users SET full_name = ?, role = ?, active = ? WHERE id = ?",
            (full_name, role, 1 if active else 0, user_id))

    def update_password(self, user_id, password_hash):
        self._db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))

    def delete(self, user_id):
        self._db.execute("DELETE FROM users WHERE id = ?", (user_id,))