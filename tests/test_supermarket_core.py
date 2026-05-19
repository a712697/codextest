from __future__ import annotations

import sqlite3
import unittest

from supermarket_system.core import SupermarketService, initialize_database
from supermarket_system.core.db import connect
from supermarket_system.core.errors import BusinessRuleError, ValidationError


class SupermarketCoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = connect(":memory:")
        initialize_database(self.conn)
        self.service = SupermarketService(self.conn)

    def tearDown(self) -> None:
        self.conn.close()

    def product(self, sku: str = "SKU-001", barcode: str | None = "690000000001") -> int:
        return self.service.create_product(
            sku=sku,
            barcode=barcode,
            name="测试牛奶",
            price_cents=1299,
            min_stock=5,
            actor_id=1,
            actor_ip="127.0.0.1",
        )

    def test_sku_must_be_unique(self) -> None:
        self.product()
        with self.assertRaises(sqlite3.IntegrityError):
            self.product()

    def test_barcode_is_unique_but_nullable(self) -> None:
        first = self.product("SKU-001", None)
        second = self.product("SKU-002", None)
        self.product("SKU-003", "690000000001")
        self.assertNotEqual(first, second)
        with self.assertRaises(sqlite3.IntegrityError):
            self.product("SKU-004", "690000000001")

    def test_price_must_not_be_negative(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.create_product(sku="SKU-N", name="错误价格", price_cents=-1)

    def test_stock_in_approval_increases_inventory_and_generates_movement(self) -> None:
        product_id = self.product()
        order_id = self.service.create_stock_in_order(
            order_no="IN-001",
            items=[{"product_id": product_id, "quantity": 10, "unit_cost_cents": 800}],
            actor_id=1,
        )
        self.service.approve_stock_in(order_id, actor_id=1, actor_ip="127.0.0.1")

        inv = self.conn.execute("SELECT quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchone()
        movements = self.conn.execute("SELECT COUNT(*) AS c FROM stock_movements WHERE product_id = ?", (product_id,)).fetchone()
        self.assertEqual(inv["quantity"], 10)
        self.assertEqual(movements["c"], 1)

    def test_stock_in_approval_is_idempotent(self) -> None:
        product_id = self.product()
        order_id = self.service.create_stock_in_order(
            order_no="IN-001",
            items=[{"product_id": product_id, "quantity": 10}],
        )
        self.service.approve_stock_in(order_id)
        self.service.approve_stock_in(order_id)

        inv = self.conn.execute("SELECT quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchone()
        movements = self.conn.execute("SELECT COUNT(*) AS c FROM stock_movements WHERE product_id = ?", (product_id,)).fetchone()
        self.assertEqual(inv["quantity"], 10)
        self.assertEqual(movements["c"], 1)

    def test_stock_out_cannot_exceed_inventory(self) -> None:
        product_id = self.product()
        order_id = self.service.create_stock_out_order(
            order_no="OUT-001",
            reason="报损",
            items=[{"product_id": product_id, "quantity": 1}],
        )

        with self.assertRaises(BusinessRuleError):
            self.service.approve_stock_out(order_id)

    def test_stock_out_approval_decreases_inventory_and_generates_movement(self) -> None:
        product_id = self.product()
        stock_in = self.service.create_stock_in_order(order_no="IN-001", items=[{"product_id": product_id, "quantity": 10}])
        self.service.approve_stock_in(stock_in)
        stock_out = self.service.create_stock_out_order(order_no="OUT-001", reason="门店领用", items=[{"product_id": product_id, "quantity": 3}])
        self.service.approve_stock_out(stock_out, actor_id=2, actor_ip="10.0.0.2")

        inv = self.conn.execute("SELECT quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchone()
        out_move = self.conn.execute("SELECT * FROM stock_movements WHERE movement_type = 'stock_out'").fetchone()
        self.assertEqual(inv["quantity"], 7)
        self.assertEqual(out_move["quantity_delta"], -3)

    def test_inventory_warning_when_below_min_stock(self) -> None:
        self.product()
        warnings = self.service.inventory_warnings()
        self.assertEqual(len(warnings), 1)

    def test_delete_product_with_inventory_or_history_is_blocked(self) -> None:
        product_id = self.product()
        stock_in = self.service.create_stock_in_order(order_no="IN-001", items=[{"product_id": product_id, "quantity": 1}])
        self.service.approve_stock_in(stock_in)

        with self.assertRaises(BusinessRuleError):
            self.service.logical_delete_product(product_id)

    def test_import_products_returns_row_errors(self) -> None:
        result = self.service.import_products(
            [
                {"sku": "SKU-1", "name": "苹果", "barcode": "", "price_cents": 399, "min_stock": 10},
                {"sku": "", "name": "坏数据", "price_cents": 100},
                {"sku": "SKU-2", "name": "负价格", "price_cents": -1},
            ]
        )
        self.assertEqual(result.created_count, 1)
        self.assertEqual([e["row"] for e in result.errors], [2, 3])


if __name__ == "__main__":
    unittest.main()
