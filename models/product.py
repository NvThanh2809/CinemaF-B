class Product:
    def __init__(self, id, category_id, name, category_name=""):
        self.id = id
        self.category_id = category_id
        self.name = name
        self.category_name = category_name

    def __repr__(self):
        return f"Product({self.id}, {self.name!r})"
