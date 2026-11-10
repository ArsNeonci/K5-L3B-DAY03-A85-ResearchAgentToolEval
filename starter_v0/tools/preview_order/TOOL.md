---
name: preview_order
track: bonus
kind: action
provider: SQLite demo (Python standard library)
requires_env: []
inputs: ["product_id", "quantity", "shipping_address"]
outputs: [status]
side_effect: local_file_write
requires_confirmation: false
---
# preview_order

Tính và lưu bản xem trước đơn demo gồm sản phẩm, số lượng, địa chỉ, tổng VND và demo_cod; chưa tạo đơn/chưa thu tiền. Có thể bỏ shipping_address để dùng địa chỉ hồ sơ. Dùng trước place_order; không dùng để xem trạng thái đơn đã tạo.

- Implementation: `tools/preview_order/tool.py::previewOrder` (camelCase theo yêu cầu Linh).
- Ví dụ chuẩn bị/gọi trực tiếp: `previewOrder(product_id="DEMO-NOTEBOOK", quantity=2)`.
- Output: preview + preview_id/preview/expires_at; error + error/message.
- Cần `demoSession(database, user_id)` do host thiết lập; không có phiên thì trả `session_required`. Không phải cơ chế đăng nhập thật.
- Chỉ dữ liệu giả trong SQLite; không mạng, không API key, không dependency mới.
- Lưu preview có TTL 600 giây; không trừ tồn kho, không tạo order. Phí giao hàng demo cố định 10.000 VND.

Xem `docs/TV2_LINH_HANDOFF.md` tại gốc repo để tích hợp registry, schema và nút xác nhận.
