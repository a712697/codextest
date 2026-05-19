from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///./supermarket_api_test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

BACKEND_DIR = Path(__file__).resolve().parents[1] / "supermarket_system" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient

from app.main import app


class SupermarketApiSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_dashboard_uses_unified_response(self) -> None:
        response = self.client.get("/api/v1/dashboard")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["code"], 0)
        self.assertEqual(payload["message"], "success")
        self.assertIn("request_id", payload)
        self.assertIn("sku_count", payload["data"])

    def test_login_returns_access_and_refresh_tokens(self) -> None:
        response = self.client.post("/api/v1/auth/login", json={"username": "admin", "password": "secret"})
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["token_type"], "bearer")
        self.assertTrue(data["access_token"])
        self.assertTrue(data["refresh_token"])

    def test_product_create_validates_price(self) -> None:
        response = self.client.post(
            "/api/v1/products",
            json={"sku": "SKU-API", "name": "接口测试商品", "price": "-1.00"},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
