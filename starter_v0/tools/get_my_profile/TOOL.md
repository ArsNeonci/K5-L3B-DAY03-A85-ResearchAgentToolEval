---
name: get_my_profile
track: bonus
kind: local_knowledge
provider: SQLite demo (Python standard library)
requires_env: []
inputs: []
outputs: [status]
side_effect: false
requires_confirmation: false
---
# get_my_profile

Đọc tên hiển thị và địa chỉ giao hàng của tài khoản demo hiện tại. Dùng khi hỏi xem hồ sơ; không cập nhật và không đọc tài khoản khác.

- Implementation: `tools/get_my_profile/tool.py::getMyProfile` (camelCase theo yêu cầu Linh).
- Ví dụ chuẩn bị/gọi trực tiếp: `getMyProfile()`.
- Output: ok + profile; error + error/message.
- Cần `demoSession(database, user_id)` do host thiết lập; không có phiên thì trả `session_required`. Không phải cơ chế đăng nhập thật.
- Chỉ dữ liệu giả trong SQLite; không mạng, không API key, không dependency mới.

Xem `docs/TV2_LINH_HANDOFF.md` tại gốc repo để tích hợp registry, schema và nút xác nhận.
