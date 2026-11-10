# Bàn giao TV2 — Chu Quang Linh

Nhánh: `tv2-linh`. Căn cứ: phần trả lời mục 1–8 trong `docs/TV2_MAU_QUYET_DINH_TOOL.md`.

## Phạm vi đã làm

Sáu tool chạy trực tiếp với SQLite cục bộ: đọc/sửa hồ sơ, xem trước/tạo/xem/hủy đơn demo. Các hàm Python dùng camelCase; tên tool model nhìn thấy dùng snake_case. Không gọi AI, không HTTP, không API key, không thêm thư viện.

Theo quyết định cụ thể tại mục 7, SQLite được chọn thay cho JSON trong ví dụ mục 3. Dữ liệu khởi tạo gồm 2 hồ sơ giả và 2 sản phẩm giả. Không xây nghiệp vụ thanh toán, hệ thống đăng nhập thật hoặc phân quyền chi tiết.

| Tên tool | Hàm Python | Hành vi |
|---|---|---|
| get_my_profile | getMyProfile | Đọc tên hiển thị, địa chỉ của tài khoản demo hiện tại |
| update_profile | updateProfile | Sửa display_name hoặc shipping_address sau phê duyệt UI |
| preview_order | previewOrder | Lưu báo giá demo, chưa tạo đơn; hết hạn sau 600 giây |
| place_order | placeOrder | Tạo đơn pending và trừ tồn kho; chống trùng theo request_id |
| get_order_status | getOrderStatus | Đọc thông tin đơn của tài khoản hiện tại |
| cancel_order | cancelOrder | Hủy đơn pending sau phê duyệt UI và hoàn tồn kho một lần |

`preview_order` có ghi bản xem trước vào SQLite nên TOOL.md khai báo `side_effect: local_file_write`, nhưng không yêu cầu xác nhận vì chưa tạo đơn. Ba action sửa hồ sơ/tạo đơn/hủy đơn bắt buộc có khóa xác nhận.

## Kiểm tra tool riêng, không dùng model

Chạy từ `starter_v0/`:

```powershell
python -m unittest discover -s tests -p test_tv2_tools.py -v
python scripts/demo_tv2_tools.py
```

- Auto test tạo SQLite tạm riêng cho từng test; không gọi registry hoặc dependency API của các tool cũ. Có thành công, input xấu, lỗi storage cho từng tool; có kiểm tra xác nhận, session, chống trùng và rollback.
- Console demo đi qua cả 6 tool; nhập `YES` tại từng lần hỏi để tự kiểm tra hành vi ghi. Nhập khác thì dừng. Không có đơn hàng hay thanh toán ngoài đời.
- File test dùng `unittest` của Python chuẩn, cũng có thể được pytest thu thập khi nhóm chạy suite sau này. Tách riêng `tests/test_tv2_tools.py` để không sửa stub test chung của thành viên khác.
- SQLite demo tạm nằm trong `starter_v0/runtime/`, bị Git ignore và được dọn khi kết thúc. Không commit database hoặc khóa xác nhận.
- Kết quả kiểm tra ghi trong `report/team/TV2_LINH_TOOL_TESTS.md`. Đã bổ sung kiểm tra TV2-12 trên bản tích hợp `c04f5da`: contract 85 passed; full pytest 122 passed, 17 skipped, 0 failed. Chưa chạy eval nhóm/base, model hoặc UI chung trong đợt kiểm tra này.

## TV1 cần tích hợp registry và tool declaration

Import và thêm các cặp sau vào `TOOL_FUNCTIONS` trong `starter_v0/tools/__init__.py`:

```python
from .get_my_profile.tool import getMyProfile
from .update_profile.tool import updateProfile
from .preview_order.tool import previewOrder
from .place_order.tool import placeOrder
from .get_order_status.tool import getOrderStatus
from .cancel_order.tool import cancelOrder

# Bổ sung vào dict hiện tại, không xóa tool có sẵn:
TV2_TOOL_FUNCTIONS = {
    "get_my_profile": getMyProfile,
    "update_profile": updateProfile,
    "preview_order": previewOrder,
    "place_order": placeOrder,
    "get_order_status": getOrderStatus,
    "cancel_order": cancelOrder,
}
TOOL_FUNCTIONS.update(TV2_TOOL_FUNCTIONS)
```

Schema bàn giao: `starter_v0/artifacts/tools_tv2.fragment.json`, có cấu trúc `{"tools": [...]}`. TV1 ghép 6 phần tử vào danh sách `tools` của `artifacts/tools.yaml` và review descriptions cùng master prompt. Đây là fragment, không thay toàn bộ YAML. Không khai báo `issueConfirmation`, `demoSession`, đường dẫn database, user_id hoặc confirmation_key cho model.

Chưa sửa registry/YAML/prompt/eval chung trong nhánh này. Sau tích hợp, TV1 chạy contract test, suite phù hợp và eval khi tới checkpoint của nhóm.

## TV1/TV4 cần gắn context và nút xác nhận

### Khởi tạo SQLite demo một lần

Chạy từ `starter_v0/`:

```python
from pathlib import Path
from commerce_demo import initializeDemoDatabase

database = Path("runtime/commerce.sqlite3")
initializeDemoDatabase(database)  # Chỉ chạy khi chưa có file; có rồi sẽ báo FileExistsError.
```

Muốn reset: dừng phiên đang dùng database, chọn file database mới và gọi khởi tạo lại. Không tự ghi đè file đang có.

### Chuẩn bị, phê duyệt, thực thi

Ví dụ dưới đây dành cho host/UI sau khi TV1 đã đăng ký imports. `user_clicked_confirm` là giá trị của nút hoặc lựa chọn người dùng từ UI, không do model quyết định:

```python
from commerce_demo import demoSession, issueConfirmation
from tools.update_profile.tool import updateProfile

with demoSession(database, user_id="demo-user-01"):
    pending = updateProfile("shipping_address", "Địa chỉ demo B")
    # Hiển thị pending_action.payload cho người dùng; chờ nút Đồng ý / Từ chối.
    if pending["status"] == "needs_confirmation" and user_clicked_confirm:
        approved = pending["pending_action"]
        key = issueConfirmation(approved["action"], approved["payload"])
        result = updateProfile("shipping_address", "Địa chỉ demo B", confirmation_key=key)
        # Chỉ lưu result vào transcript; KHÔNG lưu key hoặc arguments có key.
```

- Mỗi lần gọi tool phải có `demoSession` do host mở; thiếu context/tài khoản demo không tồn tại thì từ chối cả đọc và ghi. Context dùng `ContextVar`, không có global user_id dùng chung giữa các phiên.
- Đây là **chọn tài khoản giả từ host**, không phải đăng nhập thật. Không cung cấp qua model. Nếu cần dữ liệu/người dùng thật phải triển khai xác thực riêng trước khi dùng.
- Khóa xác nhận ràng buộc đúng phiên, tài khoản, action, toàn bộ payload; TTL 300 giây; chỉ dùng một lần. Nếu UI rerun, có thể lưu pending action trong session state, rồi mở một `demoSession` mới để cấp key và thực thi ngay trong cùng context. Không cấp key ở một context rồi thực thi ở context khác.
- Khi thay đổi nội dung, hiển thị lại và yêu cầu phê duyệt mới. Từ chối thì xóa pending action, không cấp key/không ghi.
- Chỉ gọi `issueConfirmation` sau nút đồng ý thật. Đây là helper host, không phải tool AI; không cấp sẵn key cho prompt hay để model tự điền boolean.
- Tool action trả `awaiting_user=true` khi chờ xác nhận; tương thích cơ chế dừng sẵn trong chat loop. Loop hiện tại chưa tự thực thi lần hai với key: TV1/TV4 cần thêm nhánh UI này. Với console chat cần adapter xác nhận tương tự.
- Cần lấy pending action và arguments đã chuẩn hóa từ backend, không tin một payload khác do model gửi lúc bấm nút. Không log key, và không truyền key vào tool call do model phát sinh.

## Dữ liệu và các quyết định cụ thể

- Hồ sơ `demo-user-01`: Khách demo An / Địa chỉ demo A. Hồ sơ thứ hai: `demo-user-02`.
- Danh mục: `DEMO-NOTEBOOK` giá 25.000 VND, tồn 20; `DEMO-PEN` giá 10.000 VND, tồn 30.
- Số lượng là int 1–10; không nhận boolean, float, chuỗi số. Phí giao hàng cố định 10.000 VND; chỉ `demo_cod`.
- Preview tự dùng địa chỉ hồ sơ nếu không truyền địa chỉ. Địa chỉ là snapshot: đổi hồ sơ sau đó không sửa preview cũ; nếu muốn giao chỗ khác phải tạo preview mới.
- Preview hết hạn, giá thay đổi hoặc thiếu tồn kho: tạo preview và phê duyệt lại. Giá, tổng tiền lấy từ SQLite, không nhận do model nhập.
- `request_id` là mã của một ý định đặt đơn. UI nên tạo một lần cho thao tác đó và giữ nguyên khi retry; không tạo mã mới mỗi lần mất kết nối. Retry cùng request_id/preview trả đơn cũ, không yêu cầu khóa mới vì không ghi dữ liệu; request_id cũ với preview khác trả `request_conflict`.
- Ghi đơn, trừ tồn kho, sử dụng key nằm trong cùng transaction; lỗi sẽ rollback. Hủy đơn đã cancelled không hoàn tồn thêm. Demo chỉ hủy pending, từ chối shipped/trạng thái khác.
- Trường dư trả `unsupported_fields`, liệt kê trường dư và dừng. Prompt/UI cần hỏi người dùng xác nhận bỏ trường đó trước khi gọi lại; backend không tự bỏ. Trường thiếu trả `missing_fields` để hỏi đủ trong một lượt.
- Không thêm API/dependency/env mới. Chưa có màn hình bảng đơn; output `order` là dict để TV4 hiển thị.

## TV3 có thể dùng để viết eval sau tích hợp

Các ví dụ sau là đầu vào đề xuất, không phải kết quả model đã đo:

1. “Xem địa chỉ giao hàng hiện tại của tôi” → `get_my_profile`, không gọi update.
2. “Đổi địa chỉ của tôi” → hỏi địa chỉ mới; chưa ghi. Khi có địa chỉ thì hỏi xác nhận UI.
3. “Đổi email và tên hiển thị” → email ngoài phạm vi; báo rõ, hỏi có bỏ email không; chưa tự sửa tên.
4. “Xem giá 2 cuốn DEMO-NOTEBOOK” → `preview_order(product_id="DEMO-NOTEBOOK", quantity=2)`, tổng 60.000 VND; chưa place_order.
5. “Đặt đơn này” → cần preview_id/request_id và phê duyệt UI; model không có key để tự tạo đơn.
6. “Xem trạng thái đơn DEMO-...” → `get_order_status`; “hủy đơn” → chuẩn bị cancel, chờ nút đồng ý.

Phân loại gợi ý: wrong_tool, missing_info, wrong_arg_value, wrong_boundary. TV3 chọn các case vào tổng 10 case của nhóm và quyết định kỳ vọng phù hợp với runner. Chưa có bằng chứng routing của model trong bàn giao này.
