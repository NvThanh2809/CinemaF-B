class Role:
    OWNER = "OWNER"
    STAFF = "STAFF"
    LABELS = {OWNER: "Chủ cửa hàng", STAFF: "Nhân viên"}

    @classmethod
    def label(cls, role):
        return cls.LABELS.get(role, role)


class User:
    def __init__(self, id, username, full_name, role, active=True, created_at=None, password_hash=""):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.active = bool(active)
        self.created_at = created_at
        self.password_hash = password_hash

    @property
    def is_owner(self):
        return self.role == Role.OWNER

    @property
    def role_label(self):
        return Role.label(self.role)

    def __repr__(self):
        return f"User({self.id}, {self.username!r}, {self.role})"
