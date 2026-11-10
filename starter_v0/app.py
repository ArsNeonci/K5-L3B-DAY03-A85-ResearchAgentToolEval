"""Streamlit interface for research chat and the TV2 SQLite demo."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote, quote_plus

import streamlit as st

import chat
from chat import (
    ARTIFACTS_DIR,
    assistant_tool_message,
    execute_tool_call,
    json_text,
    tool_results_message,
    trim_history,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools


PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TV2_TOOLS_PATH = ARTIFACTS_DIR / "tools_tv2.fragment.json"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4
UI_LANGUAGE_INSTRUCTION = (
    "Trong giao diện chat này, hãy trả lời, hỏi bổ sung và xin xác nhận bằng tiếng Việt. "
    "Giữ nguyên tên riêng, tiêu đề nguồn và giá trị kỹ thuật khi cần."
)
EXAMPLES = (
    ("01 · Tra cứu nghiên cứu", "Tìm 2 bài trên arXiv về đánh giá agent gọi tool. Tóm tắt mỗi bài một câu và kèm link."),
    ("02 · Bổ sung thông tin", "Cho mình xem bài mới nhất trên X."),
    ("03 · Xin xác nhận", "Gửi lên Telegram nội dung: Bản tin thử nghiệm CP5."),
)


def redact_credentials(text: str) -> str:
    secrets = {
        value
        for name, value in os.environ.items()
        if value and name.endswith(("_API_KEY", "_TOKEN", "_CHAT_ID"))
    }
    for secret in sorted(secrets, key=len, reverse=True):
        for variant in {secret, quote(secret, safe=""), quote_plus(secret), json_text(secret)[1:-1]}:
            text = text.replace(variant, "[đã ẩn]")
    return text


def render_tool_event(index: int, event: dict) -> None:
    result = event["result"]
    label = "Kết quả"
    if isinstance(result, dict):
        if result.get("error") or result.get("status") == "error":
            label = "Lỗi"
        elif result.get("awaiting_user") or result.get("status") == "needs_confirmation":
            label = "Chờ phản hồi"
    with st.expander(f"{index:02d} · {redact_credentials(event['tool'])} · {label}", expanded=label == "Lỗi"):
        st.caption("Tham số agent đã truyền")
        st.code(redact_credentials(json_text(event["args"])), language="json")
        st.caption("Phản hồi từ tool")
        st.code(redact_credentials(json_text(result)), language="json")


def render_answer(turn: dict) -> None:
    status = turn["status"]
    if status == "provider_error":
        st.error(turn["assistant_text"])
    elif status == "max_tool_rounds":
        st.warning(f"Lượt này đã đạt giới hạn {MAX_TOOL_ROUNDS} vòng gọi tool.")
    elif status == "waiting_for_user":
        st.info(turn["assistant_text"] or "Agent đang chờ bạn bổ sung thông tin.")
    else:
        st.markdown(turn["assistant_text"] or "Agent trả về câu trả lời trống.")

    events = turn["tool_events"]
    if events:
        st.caption(f"NHẬT KÝ TOOL · {len(events)} LẦN GỌI")
        for index, event in enumerate(events, start=1):
            render_tool_event(index, event)
    else:
        st.caption("Lượt này chưa gọi tool.")


def render_user(text: str) -> None:
    with st.chat_message("user"):
        st.markdown(redact_credentials(text))


def run_ui_tool_loop(provider, model, messages, tools, events) -> tuple[str, str]:
    for _ in range(MAX_TOOL_ROUNDS):
        response = provider.complete(messages, tools, model=model, temperature=0.0)
        calls = response.tool_calls
        if not calls:
            return "answered", response.text or ""

        messages.append(assistant_tool_message(response.text, calls))
        round_events = []
        for call in calls:
            if call.name == "send" and call.args.get("confirmed"):
                event = {
                    "tool": call.name,
                    "args": call.args,
                    "result": {"error": "blocked_in_demo", "message": "Gửi Telegram đã tắt trong UI demo."},
                }
            else:
                event = execute_tool_call(call)
            events.append(event)
            round_events.append(event)
            result = event["result"]
            if isinstance(result, dict) and result.get("awaiting_user"):
                question = result.get("question") or call.args.get("question") or "Bạn bổ sung thêm thông tin nhé."
                return "waiting_for_user", question
        messages.append(tool_results_message(round_events))

    return "max_tool_rounds", f"Lượt này đã đạt giới hạn {MAX_TOOL_ROUNDS} vòng gọi tool."


def run_turn(provider, model: str | None, declarations: list[dict], user_text: str) -> dict:
    user_message = {"role": "user", "content": user_text}
    events = []
    try:
        status, answer = run_ui_tool_loop(
            provider=provider,
            messages=[
                {
                    "role": "system",
                    "content": f"{PROMPT_PATH.read_text(encoding='utf-8')}\n\n{UI_LANGUAGE_INSTRUCTION}",
                },
                *trim_history(st.session_state.history, HISTORY_WINDOW),
                user_message,
            ],
            tools=to_openai_tools(declarations),
            model=model,
            events=events,
        )
    except Exception as exc:
        status_code = getattr(exc, "status_code", None)
        error = f"Không hoàn tất lượt chat ({type(exc).__name__})."
        if isinstance(status_code, int):
            error += f" HTTP {status_code}."
        error += " Kiểm tra provider và cấu hình trên máy chạy UI."
        return {"user": user_text, "status": "provider_error", "assistant_text": error, "tool_events": events}

    assistant_text = redact_credentials(answer)
    st.session_state.history = trim_history([
        *st.session_state.history,
        user_message,
        {"role": "assistant", "content": assistant_text},
    ], HISTORY_WINDOW)
    return {
        "user": user_text,
        "status": status,
        "assistant_text": assistant_text,
        "tool_events": events,
    }


def show_examples() -> None:
    st.subheader("Thử một tình huống")
    for label, prompt in EXAMPLES:
        with st.container(border=True):
            st.markdown(f"**{label}**")
            st.write(prompt)
            st.button(f"Chạy tình huống {label[:2]}", key=label, on_click=queue_example, args=(prompt,))
    st.caption("Ở tình huống 02, nếu agent hỏi tài khoản, hãy nhập @OpenAI trong cùng phiên.")


def queue_example(prompt: str) -> None:
    st.session_state.example_prompt = prompt


def demo_database() -> Path:
    from commerce_demo import initializeDemoDatabase

    if "commerce_directory" not in st.session_state:
        directory = TemporaryDirectory(prefix="day03-commerce-")
        initializeDemoDatabase(Path(directory.name) / "demo.sqlite3")
        st.session_state.commerce_directory = directory
    return Path(st.session_state.commerce_directory.name) / "demo.sqlite3"


def run_action(action: str, arguments: dict, *, approved_payload: dict | None = None) -> None:
    from commerce_demo import demoSession, issueConfirmation
    from tools.cancel_order.tool import cancelOrder
    from tools.get_my_profile.tool import getMyProfile
    from tools.get_order_status.tool import getOrderStatus
    from tools.place_order.tool import placeOrder
    from tools.preview_order.tool import previewOrder
    from tools.update_profile.tool import updateProfile

    tools = {
        "get_my_profile": getMyProfile,
        "update_profile": updateProfile,
        "preview_order": previewOrder,
        "place_order": placeOrder,
        "get_order_status": getOrderStatus,
        "cancel_order": cancelOrder,
    }

    try:
        with demoSession(demo_database()):
            if approved_payload is None:
                result = tools[action](**arguments)
            else:
                key = issueConfirmation(action, approved_payload)
                result = tools[action](**arguments, confirmation_key=key)
    except OSError:
        result = {"status": "error", "error": "storage_error", "message": "Không mở được dữ liệu SQLite demo."}

    st.session_state.commerce_event = {"tool": action, "args": arguments, "result": result}
    if result["status"] == "preview":
        st.session_state.commerce_preview = result["preview_id"]
    if "order" in result:
        st.session_state.commerce_order = result["order"]["order_id"]


def show_approval(event: dict) -> None:
    pending = event["result"]["pending_action"]
    action, payload = pending["action"], pending["payload"]
    # Select only normalized invocation fields; the remaining payload describes
    # the price, address and order snapshot the user is approving.
    fields = {
        "update_profile": ("field", "new_value"),
        "place_order": ("preview_id", "request_id"),
        "cancel_order": ("order_id",),
    }
    st.warning("Xem nội dung bên dưới trước khi quyết định.")
    st.json(payload, expanded=True)
    approve, reject = st.columns(2)
    if approve.button("Đồng ý thực hiện", type="primary"):
        arguments = {field: payload[field] for field in fields[action]}
        run_action(action, arguments, approved_payload=payload)
        st.rerun()
    if reject.button("Từ chối"):
        st.session_state.commerce_event = {
            **event, "result": {"status": "rejected", "message": "Bạn đã từ chối thao tác."},
        }
        st.rerun()


def render_commerce_demo() -> None:
    st.header("Hồ sơ và đơn hàng")
    st.caption("Dữ liệu giả trong SQLite riêng cho phiên trình duyệt này. Các thao tác dùng tool trực tiếp.")
    event = st.session_state.get("commerce_event")
    if event:
        result = event["result"]
        if result["status"] == "error":
            st.error(result["message"])
        with st.expander(f"{event['tool']} · {result['status']}", expanded=result["status"] != "needs_confirmation"):
            st.caption("Tham số")
            st.json(event["args"])
            st.caption("Kết quả")
            st.json(result)
        if result["status"] == "needs_confirmation":
            show_approval(event)
            return

    labels = {
        "get_my_profile": "Xem hồ sơ",
        "update_profile": "Cập nhật hồ sơ",
        "preview_order": "Xem trước đơn",
        "place_order": "Tạo đơn từ bản xem trước",
        "get_order_status": "Xem trạng thái đơn",
        "cancel_order": "Hủy đơn",
    }
    action = st.selectbox("Chọn thao tác", list(labels), format_func=labels.__getitem__)
    with st.form(f"commerce_{action}"):
        arguments = {}
        if action == "update_profile":
            field = st.selectbox("Trường cần sửa", ["display_name", "shipping_address"],
                                 format_func={"display_name": "Tên hiển thị", "shipping_address": "Địa chỉ giao hàng"}.get)
            arguments = {"field": field, "new_value": st.text_input("Giá trị mới", max_chars=200)}
        elif action == "preview_order":
            product_id = st.selectbox("Sản phẩm", ["DEMO-NOTEBOOK", "DEMO-PEN"],
                                      format_func={"DEMO-NOTEBOOK": "Sổ demo", "DEMO-PEN": "Bút demo"}.get)
            arguments = {"product_id": product_id, "quantity": st.number_input("Số lượng", 1, 10, 1)}
        elif action == "place_order":
            preview_id = st.text_input("Mã bản xem trước", value=st.session_state.get("commerce_preview", ""), max_chars=80)
            arguments = {"preview_id": preview_id, "request_id": preview_id}
        elif action in {"get_order_status", "cancel_order"}:
            order_id = st.text_input("Mã đơn", value=st.session_state.get("commerce_order", ""), max_chars=80)
            arguments = {"order_id": order_id}
        if st.form_submit_button(labels[action]):
            run_action(action, arguments)
            st.rerun()


def main() -> None:
    st.set_page_config(page_title="Research Agent · Day 03", page_icon="🔎")
    app_directory = Path(__file__).resolve().parent
    if Path(chat.__file__).resolve().parent != app_directory:
        st.error("Streamlit đang nạp chat.py từ bản repo khác. Dừng app rồi chạy lại từ thư mục của app.")
        st.code(f'cd "{app_directory}"\npython -m streamlit run app.py', language="bash")
        return
    st.caption("Day 03 · CP5")
    st.title("Research Agent")
    st.write("Tra cứu nguồn, tóm tắt kết quả và xem agent gọi tool theo từng lượt.")

    if TV2_TOOLS_PATH.is_file():
        page = st.radio("Khu vực demo", ["Chat nghiên cứu", "Hồ sơ & đơn hàng"], horizontal=True)
        if page == "Hồ sơ & đơn hàng":
            render_commerce_demo()
            return

    provider_name = os.getenv("DAY03_PROVIDER", "openrouter")
    model = os.getenv("DAY03_MODEL") or None
    try:
        provider = make_provider(provider_name)
        declarations = load_tool_declarations(TOOLS_PATH)
    except Exception:
        st.error("Không tải được cấu hình provider hoặc artifact. Kiểm tra cấu hình trên máy chạy UI.")
        return

    if "turns" not in st.session_state:
        st.session_state.turns = []
        st.session_state.history = []
    with st.sidebar:
        st.header("Phiên demo")
        if st.button("＋ Chat mới", type="primary"):
            st.session_state.turns.clear()
            st.session_state.history.clear()
        st.caption("Demo chặn gửi Telegram thật.")

    example = st.session_state.pop("example_prompt", "")
    if not st.session_state.turns and not example:
        show_examples()
    for turn in st.session_state.turns:
        render_user(turn["user"])
        with st.chat_message("assistant"):
            render_answer(turn)

    waiting = st.session_state.turns and st.session_state.turns[-1]["status"] == "waiting_for_user"
    placeholder = "Nhập thông tin agent vừa hỏi…" if waiting else "Nhập câu hỏi nghiên cứu…"
    user_text = (st.chat_input(placeholder) or example).strip()
    if user_text:
        render_user(user_text)
        with st.chat_message("assistant"):
            with st.spinner("Agent đang xử lý…"):
                turn = run_turn(provider, model, declarations, user_text)
            st.session_state.turns.append(turn)
        st.rerun()


if __name__ == "__main__":
    main()
