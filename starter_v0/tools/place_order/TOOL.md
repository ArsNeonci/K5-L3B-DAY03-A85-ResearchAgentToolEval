---
name: place_order
track: bonus
kind: action
provider: SQLite demo (Python standard library)
requires_env: []
inputs: ["preview_id", "request_id", "confirmation_key"]
outputs: [status]
side_effect: local_file_write
requires_confirmation: true
---
# place_order

Đề nghị tạo đơn SQLite demo từ preview_id còn hạn. request_id giữ nguyên khi retry cùng thao tác, đổi khi người dùng thật sự đặt đơn mới. Yêu cầu phê duyệt nút UI cho đúng bản xem trước và request_id; không thanh toán thật, không tự đoán sản phẩm hoặc giá.

- Implementation: `tools/place_order/tool.py::placeOrder` (camelCase theo yêu cầu Linh).
- Ví dụ chuẩn bị/gọi trực tiếp: `placeOrder(preview_id="PREVIEW-...", request_id="req-01")`.
- Output: needs_confirmation + pending_action; created/already_exists + order; error + error/message.
- Cần `demoSession(database, user_id)` do host thiết lập; không có phiên thì trả `session_required`. Không phải cơ chế đăng nhập thật.
- Chỉ dữ liệu giả trong SQLite; không mạng, không API key, không dependency mới.
- `confirmation_key` chỉ code/UI truyền sau khi người dùng bấm đồng ý. Không khai báo key trong schema model, không log hoặc đưa key vào prompt. Không truyền key: trả `pending_action`, `awaiting_user=true`; dữ liệu nghiệp vụ không đổi.
- Khóa dùng một lần, hết hạn sau 300 giây, ràng buộc phiên/tài khoản/action/payload. Từ chối thì không cấp key và không gọi lại action.
- Transaction tạo order, trừ tồn kho và dùng key cùng lúc. request_id đã có với cùng preview trả đơn cũ, không ghi thêm và không cần key mới; khác preview trả request_conflict.
- Địa chỉ là snapshot từ preview; nếu muốn đổi phải tạo preview mới. Giá đổi, thiếu tồn kho hoặc preview hết hạn: xem trước và phê duyệt lại.

Xem `docs/TV2_LINH_HANDOFF.md` tại gốc repo để tích hợp registry, schema và nút xác nhận.
