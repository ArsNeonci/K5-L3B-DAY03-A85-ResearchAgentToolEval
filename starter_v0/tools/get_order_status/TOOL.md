---
name: get_order_status
track: bonus
kind: local_knowledge
provider: SQLite demo (Python standard library)
requires_env: []
inputs: ["order_id"]
outputs: [status]
side_effect: false
requires_confirmation: false
---
# get_order_status

Đọc thông tin và trạng thái đơn SQLite demo của tài khoản hiện tại theo order_id. Dùng khi hỏi đơn đang ở trạng thái nào; không tạo, sửa hoặc hủy đơn.

- Implementation: `tools/get_order_status/tool.py::getOrderStatus` (camelCase theo yêu cầu Linh).
- Ví dụ chuẩn bị/gọi trực tiếp: `getOrderStatus(order_id="DEMO-...")`.
- Output: ok + order; error + error/message.
- Cần `demoSession(database, user_id)` do host thiết lập; không có phiên thì trả `session_required`. Không phải cơ chế đăng nhập thật.
- Chỉ dữ liệu giả trong SQLite; không mạng, không API key, không dependency mới.

Xem `docs/TV2_LINH_HANDOFF.md` tại gốc repo để tích hợp registry, schema và nút xác nhận.
