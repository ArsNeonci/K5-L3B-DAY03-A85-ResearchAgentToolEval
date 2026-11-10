"""Manual console demo for Linh's six tools: no model/API/dependencies.

Run from starter_v0: python scripts/demo_tv2_tools.py
Each invocation creates and cleans up an isolated, real SQLite demo database.
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from commerce_demo import demoSession, initializeDemoDatabase, issueConfirmation


def tool(name, function):
    spec = importlib.util.spec_from_file_location(f"tv2_{name}", ROOT / "tools" / name / "tool.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function)


def show(result):
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def approve(pending):
    show(pending)
    if pending.get("status") != "needs_confirmation":
        return None
    if input("Xác nhận nội dung trên? Nhập YES (khác = dừng): ").strip() != "YES":
        print("Đã dừng theo lựa chọn người dùng.")
        return None
    action = pending["pending_action"]
    return issueConfirmation(action["action"], action["payload"])


def main():
    get = tool("get_my_profile", "getMyProfile")
    update = tool("update_profile", "updateProfile")
    preview = tool("preview_order", "previewOrder")
    place = tool("place_order", "placeOrder")
    status = tool("get_order_status", "getOrderStatus")
    cancel = tool("cancel_order", "cancelOrder")
    with tempfile.TemporaryDirectory(dir=ROOT / "runtime") as directory:
        database = Path(directory) / "demo.sqlite3"
        initializeDemoDatabase(database)
        with demoSession(database):
            show(get())
            key = approve(update("shipping_address", "Địa chỉ demo B"))
            if key is None:
                return
            show(update("shipping_address", "Địa chỉ demo B", key))
            show(get())
            quote = show(preview("DEMO-NOTEBOOK", 2))
            key = approve(place(quote["preview_id"], "manual-request-01"))
            if key is None:
                return
            order = show(place(quote["preview_id"], "manual-request-01", key))
            order_id = order["order"]["order_id"]
            show(status(order_id))
            key = approve(cancel(order_id))
            if key is None:
                return
            show(cancel(order_id, key))
            show(status(order_id))


if __name__ == "__main__":
    main()
