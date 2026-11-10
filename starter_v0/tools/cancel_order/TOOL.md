---
name: cancel_order
track: bonus
kind: action
provider: SQLite demo (Python standard library)
requires_env: []
inputs: ["order_id", "confirmation_key"]
outputs: [status]
side_effect: local_file_write
requires_confirmation: true
---
# cancel_order

Đề nghị hủy đơn SQLite demo pending của tài khoản hiện tại; cần phê duyệt nút UI đúng đơn. Không hủy đơn shipped hoặc đơn người khác. Retry đơn đã cancelled chỉ trả trạng thái cũ, không hoàn tồn kho hai lần.

- Implementation: `tools/cancel_order/tool.py::cancelOrder` (camelCase theo yêu cầu Linh).
- Ví dụ chuẩn bị/gọi trực tiếp: `cancelOrder(order_id="DEMO-...")`.
- Output: needs_confirmation + pending_action; cancelled/already_cancelled + order_id; error + error/message.
- Cần `demoSession(database, user_id)` do host thiết lập; không có phiên thì trả `session_required`. Không phải cơ chế đăng nhập thật.
- Chỉ dữ liệu giả trong SQLite; không mạng, không API key, không dependency mới.
- `confirmation_key` chỉ code/UI truyền sau khi người dùng bấm đồng ý. Không khai báo key trong schema model, không log hoặc đưa key vào prompt. Không truyền key: trả `pending_action`, `awaiting_user=true`; dữ liệu nghiệp vụ không đổi.
- Khóa dùng một lần, hết hạn sau 300 giây, ràng buộc phiên/tài khoản/action/payload. Từ chối thì không cấp key và không gọi lại action.

Xem `docs/TV2_LINH_HANDOFF.md` tại gốc repo để tích hợp registry, schema và nút xác nhận.
