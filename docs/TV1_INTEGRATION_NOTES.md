# Ghi chú tích hợp TV1 — 6 tool SQLite demo của TV2 (Linh)

Nhánh: `tv1-integrate-tools` (tạo từ `main`, đã merge `tv2-linh`). Tài liệu gốc của TV2: [TV2_LINH_HANDOFF.md](TV2_LINH_HANDOFF.md).

**Nguyên tắc:** không sửa code hay test của TV2 (`commerce_demo/`, `tools/<6 tool>/`, `tests/test_tv2_tools.py`). Mọi điều chỉnh nằm ở phía registry, tool declaration và prompt.

## 1. Đã thay đổi gì

| File | Thay đổi |
|---|---|
| `starter_v0/tools/__init__.py` | Import 6 hàm của TV2 và đăng ký vào `TOOL_FUNCTIONS`. Riêng `place_order` được đăng ký qua wrapper `place_order_auto_request_id` (xem mục 2) |
| `starter_v0/artifacts/tools.yaml` | Thêm 6 tool vào cuối file. Schema giữ theo `tools_tv2.fragment.json` (enum, minLength, maximum, `additionalProperties: false`), riêng `place_order` bỏ `request_id`. Description viết lại bằng tiếng Anh theo mẫu v3: làm gì / khi nào dùng / khi nào không dùng |
| `starter_v0/artifacts/system_prompt.md` | Thêm 4 dòng vào mục `## Routing` cho hồ sơ và đơn hàng |

Kiểm tra: `python -m pytest` → 122 passed, 17 skipped, 0 failed (gồm contract test cho 6 tool mới và toàn bộ test của TV2).

## 2. Ba quyết định đã chốt

### 2.1. Xác nhận thao tác ghi: theo handoff, bằng nút UI

- `update_profile`, `place_order`, `cancel_order`: model gọi tool → tool trả `status: needs_confirmation`, `awaiting_user: true`, `pending_action` → **người dùng bấm nút trên UI** → host cấp key bằng `issueConfirmation` và gọi lại hàm với `confirmation_key`.
- Model **không** thấy `confirmation_key` (không khai báo trong `tools.yaml`) nên không thể tự ghi.
- Khác với `send`: `send` vẫn dùng `clarify(response_type="yes_no")` → `send(confirmed=true)`. Prompt dặn model **không** dùng `clarify` yes_no cho 3 action của TV2.

### 2.2. `request_id`: registry tự tạo cho mỗi lần gọi

- Schema của TV2 bắt model truyền `request_id`, nhưng model không có nguồn nào để biết giá trị này, nên sẽ phải bịa.
- Giải pháp (không sửa code TV2): wrapper trong `tools/__init__.py`:

  ```python
  def place_order_auto_request_id(preview_id: str = "", **extra) -> dict:
      return placeOrder(preview_id=preview_id, request_id="REQ-" + secrets.token_hex(8), **extra)
  ```

- Model chỉ gửi `preview_id`. Mỗi lần model gọi là một `request_id` mới, và `request_id` đó nằm trong `pending_action.payload`.
- Trường lạ từ model vẫn được chuyển qua `**extra` và backend TV2 trả `unsupported_fields` như cũ.
- Đánh đổi: mất chống trùng khi model gọi lặp (mỗi lần ra một pending action khác). Không tạo đơn thừa vì chưa bấm đồng ý thì không ghi.

### 2.3. `demoSession`: giữ nguyên, phần host/UI tự mở

- Mọi tool TV2 cần `demoSession(database, user_id)` do host mở. Thiếu session → `error: session_required`.
- `run_eval.py` và `chat.py` **không** mở session. Vì vậy trong run JSON, tool TV2 luôn trả `session_required`. **Điều này không ảnh hưởng điểm eval** (eval chỉ chấm tool call của model), không phải bug.

## 3. Việc cho từng thành viên

### TV4 — UI

1. Khởi tạo DB một lần: `initializeDemoDatabase(Path("runtime/commerce.sqlite3"))` (đã có file thì báo `FileExistsError`; muốn làm lại thì xoá file trước).
2. Mỗi lần gọi tool TV2 phải nằm trong `with demoSession(database, user_id="demo-user-01"):`.
3. Khi tool trả `needs_confirmation`: hiển thị `pending_action.payload`, nút **Đồng ý / Từ chối**.
4. Khi bấm Đồng ý — **lấy action và payload từ `pending_action` backend trả về, không lấy từ tool call của model**:

   ```python
   from commerce_demo import demoSession, issueConfirmation
   from tools.place_order.tool import placeOrder          # gọi hàm GỐC, không qua TOOL_FUNCTIONS
   from tools.update_profile.tool import updateProfile
   from tools.cancel_order.tool import cancelOrder

   with demoSession(database, user_id="demo-user-01"):
       action, payload = pending["pending_action"]["action"], pending["pending_action"]["payload"]
       key = issueConfirmation(action, payload)
       if action == "place_order":
           result = placeOrder(preview_id=payload["preview_id"], request_id=payload["request_id"], confirmation_key=key)
       elif action == "update_profile":
           result = updateProfile(payload["field"], payload["new_value"], confirmation_key=key)
       elif action == "cancel_order":
           result = cancelOrder(payload["order_id"], confirmation_key=key)
   ```

   - **Không** gọi `TOOL_FUNCTIONS["place_order"]` ở bước này: wrapper sẽ sinh `request_id` mới, không khớp payload đã duyệt → `invalid_confirmation`.
   - Cấp key và thực thi trong **cùng một** `demoSession` (key gắn với session_id).
   - Không log key, không đưa key vào transcript hay tool call của model.
5. Transcript live (C6) chứng minh luồng xác nhận lấy từ UI; console `chat.py` không có nút bấm.

Đã kiểm thử luồng trên với SQLite tạm: `preview_order` → `place_order` qua wrapper (`needs_confirmation`, `request_id=REQ-...`) → `issueConfirmation` + `placeOrder` gốc → `status: created`.

### TV3 — eval nhóm (`data/eval_group.json`)

Kỳ vọng cho case route tới tool TV2:

| Yêu cầu | Kỳ vọng |
|---|---|
| Xem địa chỉ/hồ sơ của tôi | `get_my_profile`, không gọi `update_profile` |
| Đổi địa chỉ thành X | `update_profile(field="shipping_address", new_value="X")` — gọi tool ngay, **không** `clarify` yes_no |
| Đổi địa chỉ (không nói địa chỉ mới) | `clarify(response_type="text")` |
| Xem giá N sản phẩm DEMO-... | `preview_order(product_id=..., quantity=N)` |
| Đặt đơn từ preview | `place_order(preview_id=...)` — **không** có `request_id` trong `expect` |
| Trạng thái / hủy đơn DEMO-... | `get_order_status(order_id=...)` / `cancel_order(order_id=...)` |

Bonus "≥ 4 tool mới" yêu cầu **mỗi** tool có ít nhất 1 eval case route tới.

### TV2 — Linh

- Biết rằng `tools.yaml` khai báo `place_order` **không có** `request_id` (khác `tools_tv2.fragment.json`), do registry tự sinh qua wrapper.
- Nếu sửa signature/tên hàm trong `tools/<tool>/tool.py`, báo TV1 để cập nhật registry và chạy lại contract test.

### TV1 — tiếp theo

- Chạy base eval với nhãn `v4` trên trạng thái đã tích hợp (giả thuyết: thêm 6 tool không làm hỏng routing của 20 case base), ghi `version_log.csv` và bảng B1.
- Merge `tv1-integrate-tools` vào `main` qua PR sau khi review.
