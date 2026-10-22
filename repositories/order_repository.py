"""Truy vấn SQL cho đơn hàng và chi tiết đơn.

Người phụ trách: THÀNH VIÊN B.
Bảng orders(id, created_at, user_id, discount_id, total_amount, discount_amount, final_amount)
Bảng order_details(id, order_id, variant_id, quantity, unit_price)
Lưu ý: module C (ReportRepository) đọc các cột created_at, user_id, total_amount, discount_amount, final_amount
của bảng orders. Đổi tên/kiểu các cột này phải báo C.
"""
from models.order import Order
from models.order_detail import OrderDetail
from utils.dates import db_datetime, day_bounds, to_datetime


class OrderRepository:
    def __init__(self, db):
        self._db = db

    def insert(self, order):
        order.id = self._db.insert("orders", {
            "created_at": db_datetime(order.created_at),
            "user_id": order.user_id,
            "discount_id": order.discount_id,
            "total_amount": order.total_amount,
            "discount_amount": order.discount_amount,
            "final_amount": order.final_amount,
        })
        for d in order.details:
            self._db.insert("order_details", {
                "order_id": order.id,
                "variant_id": d.variant_id,
                "quantity": d.quantity,
                "unit_price": d.unit_price,
            })
        return order.id

    def find_by_id(self, order_id):
        """Trả về Order đầy đủ (kèm details, seller_name, discount_code) hoặc None."""
        row = self._db.query_one(
            "SELECT o.id, o.created_at, o.user_id, u.full_name AS seller_name, "
            "o.discount_id, d.code AS discount_code, "
            "o.total_amount, o.discount_amount, o.final_amount "
            "FROM orders o "
            "JOIN users u ON u.id = o.user_id "
            "LEFT JOIN discounts d ON d.id = o.discount_id "
            "WHERE o.id = ?",
            (order_id,),
        )
        if not row:
            return None
        detail_rows = self._db.query(
            "SELECT od.variant_id, p.name AS product_name, v.size, od.unit_price, od.quantity "
            "FROM order_details od "
            "JOIN product_variants v ON v.id = od.variant_id "
            "JOIN products p ON p.id = v.product_id "
            "WHERE od.order_id = ? "
            "ORDER BY od.id",
            (order_id,),
        )
        details = [
            OrderDetail(
                variant_id=d["variant_id"],
                product_name=d["product_name"],
                size=d["size"],
                unit_price=d["unit_price"],
                quantity=d["quantity"],
            )
            for d in detail_rows
        ]
        return Order(
            id=row["id"],
            created_at=to_datetime(row["created_at"]),
            user_id=row["user_id"],
            seller_name=row["seller_name"],
            total_amount=row["total_amount"],
            discount_amount=row["discount_amount"],
            final_amount=row["final_amount"],
            details=details,
            discount_id=row["discount_id"],
            discount_code=row["discount_code"],
        )

    def list_orders(self, start, end, user_id=None, limit=500):
        """Đơn trong khoảng ngày [start, end] (kiểu date, gồm cả ngày end), mới nhất trước.

        user_id=None là tất cả nhân viên. Dùng utils.dates.day_bounds và self._db.top(limit)/limit(limit).
        """
        lo, hi = day_bounds(start, end)
        sql = (
            f"SELECT {self._db.top(limit)}o.id, o.created_at, o.user_id, u.full_name AS seller_name, "
            "o.discount_id, d.code AS discount_code, "
            "o.total_amount, o.discount_amount, o.final_amount "
            "FROM orders o "
            "JOIN users u ON u.id = o.user_id "
            "LEFT JOIN discounts d ON d.id = o.discount_id "
            "WHERE o.created_at >= ? AND o.created_at < ? "
        )
        params = [lo, hi]
        if user_id is not None:
            sql += "AND o.user_id = ? "
            params.append(user_id)
        sql += f"ORDER BY o.created_at DESC, o.id DESC{self._db.limit(limit)}"
        rows = self._db.query(sql, params)
        return [
            Order(
                id=r["id"],
                created_at=to_datetime(r["created_at"]),
                user_id=r["user_id"],
                seller_name=r["seller_name"],
                total_amount=r["total_amount"],
                discount_amount=r["discount_amount"],
                final_amount=r["final_amount"],
                discount_id=r["discount_id"],
                discount_code=r["discount_code"],
            )
            for r in rows
        ]
