from __future__ import annotations

import json
import secrets
import sqlite3
import time
from contextlib import closing, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DemoSession:
    database: Path
    user_id: str
    session_id: str


_session: ContextVar[DemoSession | None] = ContextVar("commerce_demo_session", default=None)
CONFIRMATION_TTL = 300
PREVIEW_TTL = 600


class DemoError(Exception):
    def __init__(self, code, message, **details):
        self.code, self.message, self.details = code, message, details
        super().__init__(message)


def initializeDemoDatabase(database: str | Path) -> None:
    """Explicit setup only. Refuses to overwrite an existing database."""
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create prevents accidental reset of existing demo state.
    with path.open("xb"):
        pass
    with closing(sqlite3.connect(path)) as db, db:
        db.executescript("""
            CREATE TABLE profiles (
                user_id TEXT PRIMARY KEY, display_name TEXT NOT NULL,
                shipping_address TEXT NOT NULL);
            CREATE TABLE products (
                product_id TEXT PRIMARY KEY, name TEXT NOT NULL,
                price_vnd INTEGER NOT NULL CHECK(price_vnd >= 0),
                stock INTEGER NOT NULL CHECK(stock >= 0));
            CREATE TABLE previews (
                preview_id TEXT PRIMARY KEY, user_id TEXT NOT NULL,
                payload TEXT NOT NULL, created_at REAL NOT NULL);
            CREATE TABLE orders (
                order_id TEXT PRIMARY KEY, user_id TEXT NOT NULL,
                request_id TEXT NOT NULL, preview_id TEXT NOT NULL,
                payload TEXT NOT NULL, status TEXT NOT NULL,
                UNIQUE(user_id, request_id));
            CREATE TABLE confirmations (
                token TEXT PRIMARY KEY, session_id TEXT NOT NULL,
                user_id TEXT NOT NULL, action TEXT NOT NULL, payload TEXT NOT NULL,
                expires_at REAL NOT NULL, used INTEGER NOT NULL DEFAULT 0);
        """)
        db.executemany("INSERT INTO profiles VALUES (?, ?, ?)", [
            ("demo-user-01", "Khách demo An", "Địa chỉ demo A"),
            ("demo-user-02", "Khách demo Bình", "Địa chỉ demo C"),
        ])
        db.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", [
            ("DEMO-NOTEBOOK", "Sổ demo", 25000, 20),
            ("DEMO-PEN", "Bút demo", 10000, 30),
        ])


@contextmanager
def demoSession(database: str | Path, user_id: str = "demo-user-01"):
    """Trusted host chooses the demo account; never expose this helper to the model.

    Keep the yielded context active for prepare -> UI approval -> execute.
    A new context is a new session and invalidates keys from previous contexts.
    This is demo account selection, NOT real login/authentication.
    """
    session = DemoSession(Path(database).resolve(), user_id, secrets.token_urlsafe(16))
    token = _session.set(session)
    try:
        yield session
    finally:
        _session.reset(token)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def currentSession():
    session = _session.get()
    if session is None:
        raise DemoError("session_required", "Cần phiên demo do code/UI thiết lập; chưa thực thi thao tác.")
    return session


@contextmanager
def connection():
    session = currentSession()
    # mode=rw prevents silently creating a database on a typo/missing setup.
    db = sqlite3.connect(session.database.as_uri() + "?mode=rw", uri=True, timeout=5)
    db.row_factory = sqlite3.Row
    try:
        db.execute("BEGIN IMMEDIATE")
        if not db.execute("SELECT 1 FROM profiles WHERE user_id=?", (session.user_id,)).fetchone():
            raise DemoError("session_required", "Tài khoản demo hiện tại không tồn tại.")
        yield db, session
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def issueConfirmation(action: str, payload: dict) -> str:
    """Host/UI calls ONLY after user clicks approval for the displayed payload.

    Return value is a capability key: pass directly to execution, never put in
    model prompt, tool descriptions, public logs, or transcripts.
    """
    if action not in {"update_profile", "place_order", "cancel_order"} or not isinstance(payload, dict):
        raise ValueError("Unknown confirmation action or invalid payload")
    key = secrets.token_urlsafe(32)
    with connection() as (db, session):
        db.execute("INSERT INTO confirmations VALUES (?, ?, ?, ?, ?, ?, 0)",
                   (key, session.session_id, session.user_id, action, canonical(payload),
                    time.time() + CONFIRMATION_TTL))
    return key


def approve(db, session, action, payload, key):
    if key == "":
        return {"status": "needs_confirmation", "awaiting_user": True,
                "question": "Bạn xác nhận thực hiện nội dung trong pending_action chứ?",
                "pending_action": {"action": action, "payload": payload}}
    if not isinstance(key, str):
        raise DemoError("invalid_confirmation", "Khóa xác nhận phải là chuỗi do code/UI cấp.")
    row = db.execute("SELECT * FROM confirmations WHERE token=?", (key,)).fetchone()
    if (row is None or row["used"] or row["expires_at"] <= time.time()
            or row["session_id"] != session.session_id or row["user_id"] != session.user_id
            or row["action"] != action or row["payload"] != canonical(payload)):
        raise DemoError("invalid_confirmation", "Xác nhận thiếu, hết hạn, đã dùng hoặc không khớp nội dung/phiên.")
    db.execute("UPDATE confirmations SET used=1 WHERE token=?", (key,))
    return None


def text(value, name, max_length=200):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > max_length:
        raise DemoError("invalid_input", f"{name} phải là chuỗi không rỗng, tối đa {max_length} ký tự.")
    return value.strip()


def arguments(values, extra):
    if extra:
        raise DemoError("unsupported_fields", "Trường không hỗ trợ: " + ", ".join(sorted(extra))
                        + ". Bạn có đồng ý bỏ các trường này để tiếp tục không?",
                        unsupported_fields=sorted(extra), awaiting_user=True)
    missing = [name for name, value in values.items() if value is None or (isinstance(value, str) and not value.strip())]
    if missing:
        raise DemoError("missing_info", "Vui lòng cung cấp đầy đủ trong một lượt các trường còn thiếu: " + ", ".join(missing) + ".",
                        missing_fields=missing, awaiting_user=True)


def executeTool(action, **args):
    """Common exception boundary: tools always return a JSON-serializable dict."""
    try:
        with connection() as (db, session):
            result = _dispatch(db, session, action, args)
        return {"tool": action, **result}
    except DemoError as exc:
        return {"tool": action, "status": "error", "error": exc.code,
                "message": exc.message, **exc.details,
                **({"question": exc.message} if exc.details.get("awaiting_user") else {})}
    except (sqlite3.Error, OSError):
        return {"tool": action, "status": "error", "error": "storage_error",
                "message": "Không thể đọc/ghi SQLite demo; thao tác đã rollback. Kiểm tra cấu hình/kho dữ liệu."}
    except Exception:
        return {"tool": action, "status": "error", "error": "internal_error",
                "message": "Lỗi xử lý demo; không báo thành công. Kiểm tra code phía host."}


def _order(db, session, order_id):
    row = db.execute("SELECT * FROM orders WHERE order_id=? AND user_id=?", (order_id, session.user_id)).fetchone()
    if row is None:
        raise DemoError("order_not_found", "Không tìm thấy đơn của tài khoản demo hiện tại.")
    return row


def _orderOutput(row):
    return {"order_id": row["order_id"], "status": row["status"], **json.loads(row["payload"])}


def _dispatch(db, session, action, args):
    extra = args.pop("extra", {})
    required = {
        "get_my_profile": [], "update_profile": ["field", "new_value"],
        "preview_order": ["product_id", "quantity"],
        "place_order": ["preview_id", "request_id"],
        "get_order_status": ["order_id"], "cancel_order": ["order_id"],
    }[action]
    arguments({name: args[name] for name in required}, extra)
    if action == "get_my_profile":
        row = db.execute("SELECT display_name,shipping_address FROM profiles WHERE user_id=?", (session.user_id,)).fetchone()
        return {"status": "ok", "profile": dict(row)}

    if action == "update_profile":
        field, value = text(args["field"], "field"), text(args["new_value"], "new_value")
        if field not in {"display_name", "shipping_address"}:
            raise DemoError("invalid_field", "Chỉ hỗ trợ display_name và shipping_address; hỏi lại trước khi bỏ trường không hỗ trợ.",
                            awaiting_user=True)
        payload = {"field": field, "new_value": value}
        pending = approve(db, session, action, payload, args["confirmation_key"])
        if pending:
            return pending
        # Field is selected from the strict allowlist above; values remain bound parameters.
        db.execute(f"UPDATE profiles SET {field}=? WHERE user_id=?", (value, session.user_id))
        return {"status": "updated", "field": field, "message": "Đã cập nhật hồ sơ demo hiện tại."}

    if action == "preview_order":
        product_id = text(args["product_id"], "product_id", 80)
        quantity = args["quantity"]
        if type(quantity) is not int or not 1 <= quantity <= 10:
            raise DemoError("invalid_input", "quantity phải là số nguyên từ 1 đến 10, không nhận boolean/chuỗi.")
        product = db.execute("SELECT * FROM products WHERE product_id=?", (product_id,)).fetchone()
        if product is None:
            raise DemoError("product_not_found", "Không tìm thấy sản phẩm demo.")
        if product["stock"] < quantity:
            raise DemoError("out_of_stock", "Sản phẩm demo không đủ tồn kho.")
        address = args["shipping_address"]
        if address == "":
            address = db.execute("SELECT shipping_address FROM profiles WHERE user_id=?", (session.user_id,)).fetchone()[0]
        address = text(address, "shipping_address")
        preview_id = "PREVIEW-" + secrets.token_hex(8)
        payload = {"product_id": product_id, "product_name": product["name"], "quantity": quantity,
                   "unit_price_vnd": product["price_vnd"], "shipping_fee_vnd": 10000,
                   "total_vnd": product["price_vnd"] * quantity + 10000,
                   "currency": "VND", "shipping_address": address, "payment_method": "demo_cod"}
        created = time.time()
        db.execute("INSERT INTO previews VALUES (?, ?, ?, ?)", (preview_id, session.user_id, canonical(payload), created))
        return {"status": "preview", "preview_id": preview_id, "expires_at": created + PREVIEW_TTL,
                "preview": payload, "message": "Chỉ lưu bản xem trước; chưa tạo đơn, chưa thu tiền."}

    if action == "place_order":
        preview_id = text(args["preview_id"], "preview_id", 80)
        request_id = text(args["request_id"], "request_id", 80)
        existing = db.execute("SELECT * FROM orders WHERE user_id=? AND request_id=?", (session.user_id, request_id)).fetchone()
        if existing:
            if existing["preview_id"] != preview_id:
                raise DemoError("request_conflict", "request_id đã được dùng cho một bản xem trước khác.")
            return {"status": "already_exists", "order": _orderOutput(existing), "message": "Trả đơn cũ, không tạo thêm."}
        preview = db.execute("SELECT * FROM previews WHERE preview_id=? AND user_id=?", (preview_id, session.user_id)).fetchone()
        if preview is None:
            raise DemoError("preview_not_found", "Không tìm thấy bản xem trước của tài khoản hiện tại.")
        if preview["created_at"] + PREVIEW_TTL <= time.time():
            raise DemoError("preview_expired", "Bản xem trước hết hạn; xem trước và xác nhận lại.")
        payload = json.loads(preview["payload"])
        product = db.execute("SELECT * FROM products WHERE product_id=?", (payload["product_id"],)).fetchone()
        if product is None or product["price_vnd"] != payload["unit_price_vnd"] or product["stock"] < payload["quantity"]:
            raise DemoError("preview_changed", "Giá/tồn kho thay đổi; xem trước và xác nhận lại.")
        approval = {"preview_id": preview_id, "request_id": request_id, "order": payload}
        pending = approve(db, session, action, approval, args["confirmation_key"])
        if pending:
            return pending
        order_id = "DEMO-" + secrets.token_hex(8)
        db.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, 'pending')",
                   (order_id, session.user_id, request_id, preview_id, canonical(payload)))
        db.execute("UPDATE products SET stock=stock-? WHERE product_id=?", (payload["quantity"], payload["product_id"]))
        return {"status": "created", "order": {"order_id": order_id, "status": "pending", **payload},
                "message": "Đã tạo đơn trong SQLite demo; không đặt hàng hoặc thu tiền thật."}

    order_id = text(args["order_id"], "order_id", 80)
    row = _order(db, session, order_id)
    if action == "get_order_status":
        return {"status": "ok", "order": _orderOutput(row)}
    if row["status"] == "cancelled":
        return {"status": "already_cancelled", "order_id": order_id}
    if row["status"] != "pending":
        raise DemoError("cannot_cancel", "Chỉ hủy đơn demo pending, chưa giao.")
    payload = {"order_id": order_id, "order": _orderOutput(row)}
    pending = approve(db, session, action, payload, args["confirmation_key"])
    if pending:
        return pending
    db.execute("UPDATE orders SET status='cancelled' WHERE order_id=?", (order_id,))
    order = json.loads(row["payload"])
    db.execute("UPDATE products SET stock=stock+? WHERE product_id=?", (order["quantity"], order["product_id"]))
    return {"status": "cancelled", "order_id": order_id, "message": "Đã hủy đơn demo và hoàn tồn kho."}
