"""Direct SQLite tool tests. No model, provider, HTTP, pytest or registry needed.

Run from starter_v0: python -m unittest discover -s tests -p test_tv2_tools.py -v
"""
from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from commerce_demo import demoSession, initializeDemoDatabase, issueConfirmation


def load(name, function):
    # Load wrappers directly: tools/__init__.py imports unrelated API dependencies.
    spec = importlib.util.spec_from_file_location(f"tv2_{name}", ROOT / "tools" / name / "tool.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function)


getMyProfile = load("get_my_profile", "getMyProfile")
updateProfile = load("update_profile", "updateProfile")
previewOrder = load("preview_order", "previewOrder")
placeOrder = load("place_order", "placeOrder")
getOrderStatus = load("get_order_status", "getOrderStatus")
cancelOrder = load("cancel_order", "cancelOrder")
ALL_TOOLS = [getMyProfile, updateProfile, previewOrder, placeOrder, getOrderStatus, cancelOrder]


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "runtime")
        self.addCleanup(self.temp.cleanup)
        self.database = Path(self.temp.name) / "demo.sqlite3"
        initializeDemoDatabase(self.database)
        self.context = demoSession(self.database)
        self.context.__enter__()
        self.addCleanup(self.context.__exit__, None, None, None)

    def approve(self, pending):
        self.assertEqual(pending["status"], "needs_confirmation")
        action = pending["pending_action"]
        return issueConfirmation(action["action"], action["payload"])

    def createOrder(self, request="req-01"):
        preview = previewOrder("DEMO-NOTEBOOK", 2)
        self.assertEqual(preview["status"], "preview")
        preview_id = preview["preview_id"]
        key = self.approve(placeOrder(preview_id, request))
        result = placeOrder(preview_id, request, key)
        self.assertEqual(result["status"], "created")
        return result["order"]["order_id"], preview_id, key

    def query(self, sql, params=()):
        with closing(sqlite3.connect(self.database)) as db, db:
            return db.execute(sql, params).fetchall()

    def mutate(self, sql, params=()):
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute(sql, params)

    def test_get_profile_success(self):
        result = getMyProfile()
        self.assertEqual(result["profile"], {"display_name": "Khách demo An", "shipping_address": "Địa chỉ demo A"})

    def test_get_profile_rejects_extra_field(self):
        self.assertEqual(getMyProfile(user_id="demo-user-02")["error"], "unsupported_fields")

    def test_get_profile_storage_error(self):
        with patch("commerce_demo.backend.sqlite3.connect", side_effect=sqlite3.OperationalError("demo")):
            self.assertEqual(getMyProfile()["error"], "storage_error")

    def test_update_profile_success_only_selected_field(self):
        key = self.approve(updateProfile("shipping_address", " Địa chỉ demo B "))
        self.assertEqual(updateProfile("shipping_address", "Địa chỉ demo B", key)["status"], "updated")
        self.assertEqual(getMyProfile()["profile"], {"display_name": "Khách demo An", "shipping_address": "Địa chỉ demo B"})
        self.assertEqual(self.query("SELECT shipping_address FROM profiles WHERE user_id='demo-user-02'")[0][0], "Địa chỉ demo C")

    def test_update_profile_invalid_values_do_not_write(self):
        before = getMyProfile()
        for field, value in [("email", "a@example.test"), ("display_name", " "), ("display_name", 123), ("display_name", "x"*201)]:
            with self.subTest(field=field, value=value):
                self.assertEqual(updateProfile(field, value)["status"], "error")
        self.assertEqual(getMyProfile(), before)

    def test_update_profile_missing_confirmation_does_not_write(self):
        before = getMyProfile()
        self.assertEqual(updateProfile("display_name", "Tên mới")["status"], "needs_confirmation")
        self.assertEqual(getMyProfile(), before)

    def test_update_profile_rejects_bool_fake_and_mismatched_keys(self):
        key = self.approve(updateProfile("display_name", "Tên A"))
        for candidate in (True, False, "true", "fake", key):
            self.assertEqual(updateProfile("display_name", "Tên B", candidate)["error"], "invalid_confirmation")
        self.assertEqual(updateProfile("display_name", "Tên A", key)["status"], "updated")
        self.assertEqual(updateProfile("display_name", "Tên A", key)["error"], "invalid_confirmation")

    def test_update_storage_failure_rolls_back_confirmation(self):
        key = self.approve(updateProfile("display_name", "Tên mới"))
        self.mutate("CREATE TRIGGER fail_update BEFORE UPDATE ON profiles BEGIN SELECT RAISE(ABORT, 'demo failure'); END")
        self.assertEqual(updateProfile("display_name", "Tên mới", key)["error"], "storage_error")
        self.assertEqual(self.query("SELECT used FROM confirmations WHERE token=?", (key,))[0][0], 0)
        self.assertEqual(getMyProfile()["profile"]["display_name"], "Khách demo An")

    def test_preview_success_computes_price_without_creating_order(self):
        result = previewOrder("DEMO-NOTEBOOK", 2)
        self.assertEqual(result["preview"]["total_vnd"], 60000)
        self.assertEqual(result["preview"]["shipping_address"], "Địa chỉ demo A")
        self.assertEqual(self.query("SELECT COUNT(*) FROM orders")[0][0], 0)
        self.assertEqual(self.query("SELECT stock FROM products WHERE product_id='DEMO-NOTEBOOK'")[0][0], 20)

    def test_preview_invalid_quantity(self):
        for quantity in (0, -1, 11, "2", True, 1.5):
            with self.subTest(quantity=quantity):
                self.assertEqual(previewOrder("DEMO-NOTEBOOK", quantity)["error"], "invalid_input")

    def test_preview_missing_fields_reported_together(self):
        result = previewOrder()
        self.assertEqual(result["missing_fields"], ["product_id", "quantity"])

    def test_preview_not_found_and_no_stock(self):
        self.assertEqual(previewOrder("unknown", 1)["error"], "product_not_found")
        self.mutate("UPDATE products SET stock=0")
        self.assertEqual(previewOrder("DEMO-NOTEBOOK", 1)["error"], "out_of_stock")

    def test_preview_storage_error(self):
        self.mutate("DROP TABLE previews")
        self.assertEqual(previewOrder("DEMO-PEN", 1)["error"], "storage_error")

    def test_place_success_and_retry_no_duplicate(self):
        order_id, preview_id, key = self.createOrder()
        again = placeOrder(preview_id, "req-01", key)
        self.assertEqual(again["status"], "already_exists")
        self.assertEqual(again["order"]["order_id"], order_id)
        self.assertEqual(self.query("SELECT COUNT(*) FROM orders")[0][0], 1)
        self.assertEqual(self.query("SELECT stock FROM products WHERE product_id='DEMO-NOTEBOOK'")[0][0], 18)

    def test_place_invalid_preview_and_request_conflict(self):
        self.assertEqual(placeOrder("missing", "req-x")["error"], "preview_not_found")
        self.createOrder()
        other = previewOrder("DEMO-PEN", 1)["preview_id"]
        self.assertEqual(placeOrder(other, "req-01")["error"], "request_conflict")

    def test_place_no_key_does_not_create_order(self):
        preview_id = previewOrder("DEMO-PEN", 1)["preview_id"]
        self.assertEqual(placeOrder(preview_id, "r")["status"], "needs_confirmation")
        self.assertEqual(self.query("SELECT COUNT(*) FROM orders")[0][0], 0)

    def test_place_changed_price_or_stock_needs_new_preview(self):
        preview_id = previewOrder("DEMO-NOTEBOOK", 2)["preview_id"]
        key = self.approve(placeOrder(preview_id, "r"))
        self.mutate("UPDATE products SET price_vnd=26000 WHERE product_id='DEMO-NOTEBOOK'")
        self.assertEqual(placeOrder(preview_id, "r", key)["error"], "preview_changed")
        self.assertEqual(self.query("SELECT COUNT(*) FROM orders")[0][0], 0)
        self.mutate("UPDATE products SET price_vnd=25000, stock=0 WHERE product_id='DEMO-NOTEBOOK'")
        self.assertEqual(placeOrder(preview_id, "r", key)["error"], "preview_changed")

    def test_place_expired_preview(self):
        preview_id = previewOrder("DEMO-PEN", 1)["preview_id"]
        self.mutate("UPDATE previews SET created_at=0")
        self.assertEqual(placeOrder(preview_id, "r")["error"], "preview_expired")

    def test_place_storage_failure_rolls_back_order_stock_and_key(self):
        preview_id = previewOrder("DEMO-PEN", 1)["preview_id"]
        key = self.approve(placeOrder(preview_id, "r"))
        self.mutate("CREATE TRIGGER fail_stock BEFORE UPDATE ON products BEGIN SELECT RAISE(ABORT, 'demo failure'); END")
        self.assertEqual(placeOrder(preview_id, "r", key)["error"], "storage_error")
        self.assertEqual(self.query("SELECT COUNT(*) FROM orders")[0][0], 0)
        self.assertEqual(self.query("SELECT used FROM confirmations WHERE token=?", (key,))[0][0], 0)

    def test_order_status_success(self):
        order_id, _, _ = self.createOrder()
        result = getOrderStatus(order_id)
        self.assertEqual(result["order"]["status"], "pending")
        self.assertEqual(result["order"]["total_vnd"], 60000)

    def test_order_status_invalid_or_missing(self):
        self.assertEqual(getOrderStatus()["error"], "missing_info")
        self.assertEqual(getOrderStatus(123)["error"], "invalid_input")
        self.assertEqual(getOrderStatus("missing")["error"], "order_not_found")

    def test_order_status_storage_error(self):
        self.mutate("DROP TABLE orders")
        self.assertEqual(getOrderStatus("missing")["error"], "storage_error")

    def test_cancel_success_and_retry_restores_stock_once(self):
        order_id, _, _ = self.createOrder()
        key = self.approve(cancelOrder(order_id))
        self.assertEqual(cancelOrder(order_id, key)["status"], "cancelled")
        self.assertEqual(cancelOrder(order_id, key)["status"], "already_cancelled")
        self.assertEqual(getOrderStatus(order_id)["order"]["status"], "cancelled")
        self.assertEqual(self.query("SELECT stock FROM products WHERE product_id='DEMO-NOTEBOOK'")[0][0], 20)

    def test_cancel_invalid_missing_or_shipped_order(self):
        self.assertEqual(cancelOrder()["error"], "missing_info")
        self.assertEqual(cancelOrder("missing")["error"], "order_not_found")
        order_id, _, _ = self.createOrder()
        self.mutate("UPDATE orders SET status='shipped'")
        self.assertEqual(cancelOrder(order_id)["error"], "cannot_cancel")

    def test_cancel_no_confirmation_leaves_pending(self):
        order_id, _, _ = self.createOrder()
        self.assertEqual(cancelOrder(order_id)["status"], "needs_confirmation")
        self.assertEqual(getOrderStatus(order_id)["order"]["status"], "pending")

    def test_cancel_storage_failure_rolls_back_order(self):
        order_id, _, _ = self.createOrder()
        key = self.approve(cancelOrder(order_id))
        self.mutate("CREATE TRIGGER fail_stock BEFORE UPDATE ON products BEGIN SELECT RAISE(ABORT, 'demo failure'); END")
        self.assertEqual(cancelOrder(order_id, key)["error"], "storage_error")
        self.assertEqual(getOrderStatus(order_id)["order"]["status"], "pending")

    def test_no_session_all_tools_refuse(self):
        from commerce_demo.backend import _session
        token = _session.set(None)
        try:
            for tool in ALL_TOOLS:
                with self.subTest(tool=tool.__name__):
                    self.assertEqual(tool()["error"], "session_required")
        finally:
            _session.reset(token)

    def test_nonexistent_account_and_cross_account_order(self):
        order_id, _, _ = self.createOrder()
        with demoSession(self.database, "unknown"):
            self.assertEqual(getMyProfile()["error"], "session_required")
        with demoSession(self.database, "demo-user-02"):
            self.assertEqual(getOrderStatus(order_id)["error"], "order_not_found")

    def test_confirmation_wrong_session_and_expired(self):
        key = self.approve(updateProfile("display_name", "Tên mới"))
        with demoSession(self.database):
            self.assertEqual(updateProfile("display_name", "Tên mới", key)["error"], "invalid_confirmation")
        self.mutate("UPDATE confirmations SET expires_at=0")
        self.assertEqual(updateProfile("display_name", "Tên mới", key)["error"], "invalid_confirmation")

    def test_setup_does_not_overwrite_existing_database(self):
        with self.assertRaises(FileExistsError):
            initializeDemoDatabase(self.database)
        self.assertEqual(getMyProfile()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
