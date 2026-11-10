---
name: update_profile
track: bonus
kind: action
provider: SQLite demo (Python standard library)
requires_env: []
inputs: ["field", "new_value", "confirmation_key"]
outputs: [status]
side_effect: local_file_write
requires_confirmation: true
---
# update_profile

Đề nghị cập nhật display_name hoặc shipping_address của tài khoản demo hiện tại. Thiếu dữ liệu thì hỏi đủ trong một lượt; trường ngoài phạm vi phải hỏi trước khi bỏ. Chưa có phê duyệt bằng nút UI thì chỉ trả needs_confirmation; không dùng để xem hồ sơ hay sửa email/mật khẩu.

- Implementation: `tools/update_profile/tool.py::updateProfile` (camelCase theo yêu cầu Linh).
- Ví dụ chuẩn bị/gọi trực tiếp: `updateProfile(field="shipping_address", new_value="Địa chỉ demo B")`.
- Output: needs_confirmation + pending_action; updated + field; error + error/message.
- Cần `demoSession(database, user_id)` do host thiết lập; không có phiên thì trả `session_required`. Không phải cơ chế đăng nhập thật.
- Chỉ dữ liệu giả trong SQLite; không mạng, không API key, không dependency mới.
- `confirmation_key` chỉ code/UI truyền sau khi người dùng bấm đồng ý. Không khai báo key trong schema model, không log hoặc đưa key vào prompt. Không truyền key: trả `pending_action`, `awaiting_user=true`; dữ liệu nghiệp vụ không đổi.
- Khóa dùng một lần, hết hạn sau 300 giây, ràng buộc phiên/tài khoản/action/payload. Từ chối thì không cấp key và không gọi lại action.

Xem `docs/TV2_LINH_HANDOFF.md` tại gốc repo để tích hợp registry, schema và nút xác nhận.
