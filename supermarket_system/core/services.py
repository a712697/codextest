from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from typing import Any

from .errors import BusinessRuleError, ConflictError, NotFoundError, ValidationError


@dataclass(frozen=True)
class ImportResult:
    created_count: int
    errors: list[dict[str, Any]]


class SupermarketService:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create_product(
        self,
        *,
        sku: str,
        name: str,
        price_cents: int,
        barcode: str | None = None,
        min_stock: int = 0,
        actor_id: int | None = None,
        actor_ip: str | None = None,
    ) -> int:
        sku = required(sku, "sku")
        name = required(name, "name")
        barcode = normalize_optional(barcode)
        if price_cents < 0:
            raise ValidationError("Product price must be greater than or equal to 0.")
        if min_stock < 0:
            raise ValidationError("Minimum stock must be greater than or equal to 0.")
        with self.conn:
            cur = self.conn.execute(
                """
                INSERT INTO products (sku, barcode, name, price_cents, min_stock, created_by, updated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (sku, barcode, name, price_cents, min_stock, actor_id, actor_id),
            )
            product_id = int(cur.lastrowid)
            self.conn.execute(
                "INSERT INTO inventory (product_id, quantity, created_by, updated_by) VALUES (?, 0, ?, ?)",
                (product_id, actor_id, actor_id),
            )
            self.audit(actor_id, actor_ip, "product", "create", "product", product_id, True, after={"sku": sku, "name": name})
            return product_id

    def import_products(self, rows: list[dict[str, Any]], *, actor_id: int | None = None) -> ImportResult:
        errors: list[dict[str, Any]] = []
        created = 0
        for index, row in enumerate(rows, start=1):
            try:
                self.create_product(
                    sku=str(row.get("sku") or ""),
                    name=str(row.get("name") or ""),
                    price_cents=int(row.get("price_cents")),
                    barcode=normalize_optional(row.get("barcode")),
                    min_stock=int(row.get("min_stock") or 0),
                    actor_id=actor_id,
                )
                created += 1
            except Exception as exc:
                errors.append({"row": index, "reason": str(exc), "data": row})
        return ImportResult(created, errors)

    def create_stock_in_order(self, *, order_no: str, items: list[dict[str, int]], actor_id: int | None = None) -> int:
        order_no = required(order_no, "order_no")
        if not items:
            raise ValidationError("Stock-in order must have at least one item.")
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO stock_in_orders (order_no, created_by, updated_by) VALUES (?, ?, ?)",
                (order_no, actor_id, actor_id),
            )
            order_id = int(cur.lastrowid)
            for item in items:
                product_id = int(item["product_id"])
                quantity = int(item["quantity"])
                unit_cost_cents = int(item.get("unit_cost_cents", 0))
                self._ensure_product_exists(product_id)
                if quantity <= 0:
                    raise ValidationError("Stock-in quantity must be greater than 0.")
                if unit_cost_cents < 0:
                    raise ValidationError("Unit cost must be greater than or equal to 0.")
                self.conn.execute(
                    """
                    INSERT INTO stock_in_order_items
                        (order_id, product_id, quantity, unit_cost_cents, created_by, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (order_id, product_id, quantity, unit_cost_cents, actor_id, actor_id),
                )
            self.audit(actor_id, None, "stock_in", "create", "stock_in_order", order_id, True)
            return order_id

    def approve_stock_in(self, order_id: int, *, actor_id: int | None = None, actor_ip: str | None = None) -> None:
        request_id = str(uuid.uuid4())
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            order = self._get_order_for_update("stock_in_orders", order_id)
            if order["status"] == "approved":
                self.conn.commit()
                return
            if order["status"] != "draft":
                raise BusinessRuleError("Only draft stock-in orders can be approved.")
            items = self.conn.execute(
                "SELECT * FROM stock_in_order_items WHERE order_id = ? AND is_deleted = 0",
                (order_id,),
            ).fetchall()
            if not items:
                raise ValidationError("Stock-in order has no items.")
            for item in items:
                inv = self._get_inventory(item["product_id"])
                before = int(inv["quantity"])
                after = before + int(item["quantity"])
                cur = self.conn.execute(
                    """
                    UPDATE inventory
                    SET quantity = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP, updated_by = ?
                    WHERE product_id = ? AND version = ?
                    """,
                    (after, actor_id, item["product_id"], inv["version"]),
                )
                if cur.rowcount != 1:
                    raise ConflictError("Inventory version conflict.")
                self._movement(item["product_id"], "stock_in", "stock_in_order", order_id, item["quantity"], before, after, "stock in approved", actor_id, request_id)
            self.conn.execute(
                """
                UPDATE stock_in_orders
                SET status = 'approved', approved_at = CURRENT_TIMESTAMP, approved_by = ?, updated_by = ?, version = version + 1
                WHERE id = ?
                """,
                (actor_id, actor_id, order_id),
            )
            self.audit(actor_id, actor_ip, "stock_in", "approve", "stock_in_order", order_id, True, request_id=request_id)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def create_stock_out_order(
        self,
        *,
        order_no: str,
        reason: str,
        items: list[dict[str, int]],
        actor_id: int | None = None,
    ) -> int:
        order_no = required(order_no, "order_no")
        reason = required(reason, "reason")
        if not items:
            raise ValidationError("Stock-out order must have at least one item.")
        with self.conn:
            cur = self.conn.execute(
                """
                INSERT INTO stock_out_orders (order_no, reason, created_by, updated_by)
                VALUES (?, ?, ?, ?)
                """,
                (order_no, reason, actor_id, actor_id),
            )
            order_id = int(cur.lastrowid)
            for item in items:
                product_id = int(item["product_id"])
                quantity = int(item["quantity"])
                self._ensure_product_exists(product_id)
                if quantity <= 0:
                    raise ValidationError("Stock-out quantity must be greater than 0.")
                self.conn.execute(
                    """
                    INSERT INTO stock_out_order_items (order_id, product_id, quantity, created_by, updated_by)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (order_id, product_id, quantity, actor_id, actor_id),
                )
            self.audit(actor_id, None, "stock_out", "create", "stock_out_order", order_id, True)
            return order_id

    def approve_stock_out(self, order_id: int, *, actor_id: int | None = None, actor_ip: str | None = None) -> None:
        request_id = str(uuid.uuid4())
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            order = self._get_order_for_update("stock_out_orders", order_id)
            if order["status"] == "approved":
                self.conn.commit()
                return
            if order["status"] != "draft":
                raise BusinessRuleError("Only draft stock-out orders can be approved.")
            items = self.conn.execute(
                "SELECT * FROM stock_out_order_items WHERE order_id = ? AND is_deleted = 0",
                (order_id,),
            ).fetchall()
            if not items:
                raise ValidationError("Stock-out order has no items.")
            for item in items:
                inv = self._get_inventory(item["product_id"])
                before = int(inv["quantity"])
                quantity = int(item["quantity"])
                if before < quantity:
                    raise BusinessRuleError("Insufficient inventory.")
                after = before - quantity
                cur = self.conn.execute(
                    """
                    UPDATE inventory
                    SET quantity = ?, version = version + 1, updated_at = CURRENT_TIMESTAMP, updated_by = ?
                    WHERE product_id = ? AND version = ?
                    """,
                    (after, actor_id, item["product_id"], inv["version"]),
                )
                if cur.rowcount != 1:
                    raise ConflictError("Inventory version conflict.")
                self._movement(item["product_id"], "stock_out", "stock_out_order", order_id, -quantity, before, after, order["reason"], actor_id, request_id)
            self.conn.execute(
                """
                UPDATE stock_out_orders
                SET status = 'approved', approved_at = CURRENT_TIMESTAMP, approved_by = ?, updated_by = ?, version = version + 1
                WHERE id = ?
                """,
                (actor_id, actor_id, order_id),
            )
            self.audit(actor_id, actor_ip, "stock_out", "approve", "stock_out_order", order_id, True, request_id=request_id)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def logical_delete_product(self, product_id: int, *, actor_id: int | None = None) -> None:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            product = self._ensure_product_exists(product_id)
            inv = self._get_inventory(product_id)
            if int(inv["quantity"]) > 0:
                raise BusinessRuleError("Cannot delete product with inventory.")
            refs = self.conn.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM stock_in_order_items WHERE product_id = ?) +
                    (SELECT COUNT(*) FROM stock_out_order_items WHERE product_id = ?) AS ref_count
                """,
                (product_id, product_id),
            ).fetchone()["ref_count"]
            if refs:
                raise BusinessRuleError("Cannot delete product with stock order history.")
            self.conn.execute(
                "UPDATE products SET is_deleted = 1, updated_by = ?, updated_at = CURRENT_TIMESTAMP, version = version + 1 WHERE id = ?",
                (actor_id, product_id),
            )
            self.audit(actor_id, None, "product", "delete", "product", product_id, True, before=dict(product))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def inventory_warnings(self) -> list[sqlite3.Row]:
        return self.conn.execute(
            """
            SELECT p.id, p.sku, p.name, p.min_stock, i.quantity
            FROM products p
            JOIN inventory i ON i.product_id = p.id
            WHERE p.is_deleted = 0 AND i.quantity < p.min_stock
            ORDER BY i.quantity ASC, p.name ASC
            """
        ).fetchall()

    def _get_order_for_update(self, table: str, order_id: int) -> sqlite3.Row:
        row = self.conn.execute(f"SELECT * FROM {table} WHERE id = ? AND is_deleted = 0", (order_id,)).fetchone()
        if row is None:
            raise NotFoundError("Order not found.")
        return row

    def _ensure_product_exists(self, product_id: int) -> sqlite3.Row:
        row = self.conn.execute(
            "SELECT * FROM products WHERE id = ? AND is_deleted = 0",
            (product_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("Product not found.")
        return row

    def _get_inventory(self, product_id: int) -> sqlite3.Row:
        row = self.conn.execute(
            "SELECT * FROM inventory WHERE product_id = ? AND is_deleted = 0",
            (product_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("Inventory not found.")
        return row

    def _movement(
        self,
        product_id: int,
        movement_type: str,
        source_type: str,
        source_id: int,
        quantity_delta: int,
        before: int,
        after: int,
        reason: str,
        actor_id: int | None,
        request_id: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO stock_movements
                (product_id, movement_type, source_type, source_id, quantity_delta, before_quantity, after_quantity, reason, created_by, request_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (product_id, movement_type, source_type, source_id, quantity_delta, before, after, reason, actor_id, request_id),
        )

    def audit(
        self,
        actor_id: int | None,
        actor_ip: str | None,
        module: str,
        action: str,
        target_type: str,
        target_id: int | None,
        success: bool,
        *,
        message: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO audit_logs
                (actor_id, actor_ip, module, action, target_type, target_id, success, message, before_data, after_data, request_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                actor_id,
                actor_ip,
                module,
                action,
                target_type,
                target_id,
                1 if success else 0,
                message,
                json.dumps(before, sort_keys=True) if before else None,
                json.dumps(after, sort_keys=True) if after else None,
                request_id or str(uuid.uuid4()),
            ),
        )


def required(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValidationError(f"{field} is required.")
    return text


def normalize_optional(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
