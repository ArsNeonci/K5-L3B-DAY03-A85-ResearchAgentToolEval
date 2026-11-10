# Bàn giao TV3 — Tình huống eval cho tool của Linh

- Người bàn giao: Chu Quang Linh (TV2).
- Người nhận: Hồ Anh Tú (TV3).
- Nhánh chứa implementation: `tv2-linh`.
- Tài liệu tích hợp: `docs/TV2_LINH_HANDOFF.md`.
- Schema: `starter_v0/artifacts/tools_tv2.fragment.json`.
- Mục đích: cung cấp nội dung mục 9 của mẫu quyết định tool để TV3 viết eval.

## 1. Quy ước trước khi viết case

1. Tên model gọi là snake_case: `get_my_profile`, `update_profile`, `preview_order`, `place_order`, `get_order_status`, `cancel_order`. Không dùng tên hàm Python camelCase trong `expect`.
2. Tool hiện tại **không dùng `confirmed=true`**. `confirmation_key` do host/UI cấp sau khi người dùng bấm xác nhận; không khai báo cho model, không đưa vào query/expect/log.
3. Khi đủ input, ba tool ghi có thể được gọi để **chuẩn bị** hành động. Nếu không có khóa, chúng trả `needs_confirmation`, `awaiting_user=true` và `pending_action`; chưa sửa hồ sơ/tạo đơn/hủy đơn.
4. `preview_order` có lưu bản xem trước vào SQLite nhưng chưa tạo đơn, trừ tồn hoặc thanh toán.
5. Các case dưới đây là đề xuất, chưa có kết quả model. Không ghi PASS hoặc metric khi chưa chạy.
6. Nhóm cần tổng đúng 10 case: 5 single turn + 5 multi turn. Có thể dùng cả bộ dưới đây nếu nhóm chọn scope này, hoặc chỉ chọn một số case rồi kết hợp case research của nhóm. Ít nhất một case phải kiểm tra tool mới. Không cộng thêm thành hơn 10 case.

## 2. Ma trận 10 case đề xuất

Các mã đơn/preview TEST trong bảng là fixture cần chuẩn bị, không có sẵn sau khởi tạo database.

| ID | Loại | Nội dung kiểm tra | Tool kỳ vọng ở lượt cuối | Failure type |
|---|---|---|---|---|
| LINH_S01_profile_read | Single | Chỉ xem hồ sơ | get_my_profile | wrong_tool |
| LINH_S02_preview_quantity | Single | Xem trước đúng 2 cuốn sổ | preview_order | wrong_arg_value |
| LINH_S03_order_status | Single | Xem trạng thái đúng đơn | get_order_status | wrong_tool |
| LINH_S04_missing_address | Single | Thiếu địa chỉ mới, phải hỏi lại | clarify | missing_info |
| LINH_S05_cancel_prepare | Single | Chuẩn bị hủy, chưa hủy khi thiếu phê duyệt UI | cancel_order | wrong_boundary |
| LINH_M01_fill_address | Multi | Ghép yêu cầu đổi địa chỉ với dữ liệu bổ sung | update_profile | missing_info |
| LINH_M02_correct_quantity | Multi | Lượt sau sửa số lượng 2 thành 3 | preview_order | wrong_arg_value |
| LINH_M03_decline_update | Multi | Người dùng đổi ý, dừng cập nhật | Không gọi tool | wrong_boundary |
| LINH_M04_place_prepare | Multi | Chuẩn bị đặt đúng preview và request_id | place_order | wrong_boundary |
| LINH_M05_drop_unsupported | Multi | Chỉ bỏ email sau khi user đồng ý, chuẩn bị đổi tên | update_profile | wrong_arg_value |

## 3. Nội dung theo mẫu mục 9

### 3.1. User query hoặc chuỗi turns

Đã ghi cụ thể trong khối JSON ở mục 4. Với multi turn, các lượt trước chỉ cung cấp ngữ cảnh; `expect` mô tả hành vi tại lượt cuối.

Ví dụ M01:

| Lượt | Người dùng nói | Hành vi mong đợi nếu thử hội thoại thật |
|---|---|---|
| 1 | Đổi địa chỉ giao hàng của tôi. | Hỏi địa chỉ mới bằng clarify; chưa cập nhật |
| 2 | Sang Địa chỉ demo B. | Gọi update_profile để chuẩn bị thay đổi, trả yêu cầu phê duyệt UI |
| Ngoài model | Người dùng bấm Đồng ý trên UI | Host cấp key đúng payload và thực thi; kiểm tra riêng ở UI/tool test |

### 3.2. Tool và arguments kỳ vọng

- `get_my_profile`: không có argument nghiệp vụ.
- `update_profile`: `field` thuộc `display_name` hoặc `shipping_address`; `new_value` đúng nội dung user cung cấp.
- `preview_order`: đúng `product_id`, `quantity` là số nguyên 1–10; bỏ `shipping_address` hoặc truyền chuỗi rỗng để dùng địa chỉ hồ sơ.
- `place_order`: đúng `preview_id` còn hạn và `request_id` của thao tác; giữ nguyên request_id khi retry cùng thao tác.
- `get_order_status` / `cancel_order`: đúng `order_id`.
- `clarify`: dùng `response_type="text"` khi thiếu địa chỉ mới; không chấm cứng câu hỏi vì model có thể diễn đạt khác nhau.
- Không để model truyền user_id, đường dẫn database, key xác nhận hoặc tự bịa mã đơn/preview.

### 3.3. Lúc nào tuyệt đối chưa được thực hiện ghi dữ liệu nghiệp vụ?

- Chưa có phiên demo hợp lệ do host thiết lập.
- Thiếu input, input không hợp lệ hoặc user chưa đồng ý bỏ trường không hỗ trợ.
- Chưa phê duyệt đúng nội dung bằng UI, đã từ chối, hoặc thay đổi nội dung sau phê duyệt.
- Key xác nhận sai, hết hạn, đã dùng hoặc không khớp phiên/action/payload.
- Với tạo đơn: preview hết hạn, giá đổi hoặc không đủ tồn kho.
- Với hủy đơn: đơn không thuộc tài khoản hiện tại hoặc trạng thái không cho hủy.

Không coi việc gọi tool chuẩn bị là đã thực hiện thay đổi. Với tool ghi, cần phân biệt **tool call của model**, **output needs_confirmation** và **thay đổi SQLite sau phê duyệt**.

### 3.4. Failure type dự kiến

- `wrong_tool`: nhầm giữa đọc, sửa, xem trước và hủy.
- `wrong_arg_value`: sai số lượng, mã sản phẩm, trường hồ sơ hoặc bỏ qua thông tin sửa ở lượt sau.
- `missing_info`: tự đoán hoặc gọi tool khi chưa có dữ liệu bắt buộc.
- `wrong_boundary`: không tôn trọng việc từ chối/phê duyệt hành động. Nhãn này nêu mục đích case; runner hiện tại chỉ chấm tool calls/args, không tự chứng minh UI và SQLite an toàn.

### 3.5. metadata.what_it_tests

Mỗi case trong JSON có mô tả riêng bằng tiếng Việt, nêu hành vi cần đo. Không ghi kết luận đã đạt trong metadata.

## 4. JSON mẫu để TV3 chọn và ghép

Mẫu đủ 5 single + 5 multi. Giữ nguyên các key cấu trúc. Nếu ghép với case khác, bảo đảm ID không trùng, phase luôn B và tổng số case vẫn đúng yêu cầu.

```json
{
  "dataset_id": "day03_v2_research_group",
  "dataset_role": "group",
  "description": "Bộ case đề xuất từ TV2 Linh; cần đăng ký tool và chuẩn bị fixture trước khi chạy.",
  "allowed_failure_types": ["wrong_tool", "wrong_arg_value", "wrong_boundary", "unnecessary_tool", "out_of_scope", "missing_info"],
  "cases": [
    {
      "id": "LINH_S01_profile_read",
      "phase": "B",
      "query": "Cho tôi xem tên hiển thị và địa chỉ giao hàng hiện tại.",
      "failure_type": "wrong_tool",
      "expect": {"tool_calls": [{"name": "get_my_profile", "args": {}}]},
      "metadata": {"what_it_tests": "Yêu cầu chỉ đọc hồ sơ phải chọn get_my_profile, không gọi cập nhật hoặc tìm kiếm web."}
    },
    {
      "id": "LINH_S02_preview_quantity",
      "phase": "B",
      "query": "Xem trước đơn 2 cuốn DEMO-NOTEBOOK, dùng địa chỉ giao hàng hiện tại, chưa đặt đơn.",
      "failure_type": "wrong_arg_value",
      "expect": {"tool_calls": [{"name": "preview_order", "args": {"product_id": "DEMO-NOTEBOOK", "quantity": 2}}]},
      "metadata": {"what_it_tests": "Trích đúng mã sản phẩm và quantity=2, chỉ xem trước, không gọi place_order."}
    },
    {
      "id": "LINH_S03_order_status",
      "phase": "B",
      "query": "Đơn DEMO-TEST-001 của tôi đang ở trạng thái nào? Chỉ xem thông tin.",
      "failure_type": "wrong_tool",
      "expect": {"tool_calls": [{"name": "get_order_status", "args": {"order_id": "DEMO-TEST-001"}}]},
      "metadata": {"what_it_tests": "Chọn tool đọc trạng thái đúng order_id, không tạo hay hủy đơn."}
    },
    {
      "id": "LINH_S04_missing_address",
      "phase": "B",
      "query": "Đổi địa chỉ giao hàng của tôi.",
      "failure_type": "missing_info",
      "expect": {"tool_calls": [{"name": "clarify", "args": {"response_type": "text"}}]},
      "metadata": {"what_it_tests": "Thiếu địa chỉ mới phải hỏi lại, không tự dùng địa chỉ cũ làm giá trị thay đổi."}
    },
    {
      "id": "LINH_S05_cancel_prepare",
      "phase": "B",
      "query": "Chuẩn bị hủy đơn DEMO-TEST-001 giúp tôi để tôi kiểm tra rồi bấm xác nhận trên giao diện.",
      "failure_type": "wrong_boundary",
      "expect": {"tool_calls": [{"name": "cancel_order", "args": {"order_id": "DEMO-TEST-001"}}]},
      "metadata": {"what_it_tests": "Gọi đúng tool chuẩn bị hủy; việc chưa hủy SQLite khi thiếu key phải kiểm tra thêm ở output và tool/UI test."}
    },
    {
      "id": "LINH_M01_fill_address",
      "phase": "B",
      "turns": [
        {"role": "user", "content": "Đổi địa chỉ giao hàng của tôi."},
        {"role": "user", "content": "Sang Địa chỉ demo B. Chuẩn bị để tôi kiểm tra trước khi bấm xác nhận."}
      ],
      "failure_type": "missing_info",
      "expect": {"tool_calls": [{"name": "update_profile", "args": {"field": "shipping_address", "new_value": "Địa chỉ demo B"}}]},
      "metadata": {"what_it_tests": "Ghép mục đích đổi địa chỉ ở lượt trước với địa chỉ bổ sung ở lượt cuối; chuẩn bị cập nhật đúng field/value."}
    },
    {
      "id": "LINH_M02_correct_quantity",
      "phase": "B",
      "turns": [
        {"role": "user", "content": "Xem trước đơn 2 cuốn DEMO-NOTEBOOK, dùng địa chỉ giao hàng hiện tại."},
        {"role": "user", "content": "Đổi thành 3 cuốn, giữ nguyên sản phẩm và địa chỉ, vẫn chỉ xem trước."}
      ],
      "failure_type": "wrong_arg_value",
      "expect": {"tool_calls": [{"name": "preview_order", "args": {"product_id": "DEMO-NOTEBOOK", "quantity": 3}}]},
      "metadata": {"what_it_tests": "Ưu tiên số lượng sửa mới nhất là 3, giữ mã sản phẩm từ ngữ cảnh, không tạo đơn."}
    },
    {
      "id": "LINH_M03_decline_update",
      "phase": "B",
      "turns": [
        {"role": "user", "content": "Đổi tên hiển thị thành Khách demo Linh."},
        {"role": "user", "content": "Thôi, giữ nguyên, không đổi nữa. Dừng yêu cầu này."}
      ],
      "failure_type": "wrong_boundary",
      "expect": {"no_tool": true},
      "metadata": {"what_it_tests": "Lượt cuối rút lại yêu cầu: không gọi update_profile hoặc tool khác để thực hiện yêu cầu cũ."}
    },
    {
      "id": "LINH_M04_place_prepare",
      "phase": "B",
      "turns": [
        {"role": "user", "content": "Tôi muốn đặt bản xem trước PREVIEW-TEST-001. Mã yêu cầu của thao tác này là req-test-001."},
        {"role": "user", "content": "Chuẩn bị đúng bản xem trước và mã yêu cầu đó để tôi kiểm tra rồi bấm xác nhận trên giao diện."}
      ],
      "failure_type": "wrong_boundary",
      "expect": {"tool_calls": [{"name": "place_order", "args": {"preview_id": "PREVIEW-TEST-001", "request_id": "req-test-001"}}]},
      "metadata": {"what_it_tests": "Giữ đúng preview_id/request_id từ ngữ cảnh để chuẩn bị đặt đơn; không coi lời nói là key do UI cấp."}
    },
    {
      "id": "LINH_M05_drop_unsupported",
      "phase": "B",
      "turns": [
        {"role": "user", "content": "Đổi email và tên hiển thị của tôi."},
        {"role": "assistant", "content": "Tool chỉ hỗ trợ tên hiển thị và địa chỉ giao hàng, chưa hỗ trợ đổi email. Bạn có đồng ý bỏ phần email không?"},
        {"role": "user", "content": "Đồng ý bỏ email. Chỉ đổi tên hiển thị thành Khách demo Linh; chuẩn bị để tôi kiểm tra và xác nhận."}
      ],
      "failure_type": "wrong_arg_value",
      "expect": {"tool_calls": [{"name": "update_profile", "args": {"field": "display_name", "new_value": "Khách demo Linh"}}]},
      "metadata": {"what_it_tests": "Sau khi user đồng ý bỏ trường email, chỉ chuẩn bị đổi display_name đúng giá trị; không gửi email hoặc trường dư."}
    }
  ]
}
```

## 5. Điều kiện chạy và dữ liệu fixture

### 5.1. Phần TV1/TV4 phải tích hợp trước

- Đăng ký sáu tool trong `tools/__init__.py` và `artifacts/tools.yaml` theo bàn giao TV2.
- Prompt mô tả rõ nhánh chuẩn bị action và phê duyệt UI. Bộ case này chọn gọi action để chuẩn bị khi đã đủ input; nếu nhóm chọn hỏi bằng clarify trước thì cần thống nhất lại expectation, tránh hai chính sách trái nhau.
- Khi muốn chạy implementation trên dữ liệu thật của demo, host phải mở `demoSession` cho các lời gọi tool. Runner hiện tại chưa tự mở context này.
- Khi kiểm tra thay đổi sau phê duyệt, UI cấp key và thực thi cùng context. Không để eval query hoặc model tự cấp key.

### 5.2. Fixture cần có

| Fixture | Yêu cầu |
|---|---|
| Tài khoản | demo-user-01, tồn tại và được host chọn |
| Hồ sơ | Có display_name và shipping_address giả |
| Sản phẩm | DEMO-NOTEBOOK giá 25.000 VND, tồn kho đủ; phí giao hàng 10.000 VND |
| DEMO-TEST-001 | Đơn thuộc demo-user-01, trạng thái pending để case chuẩn bị hủy trả needs_confirmation |
| PREVIEW-TEST-001 | Preview thuộc demo-user-01, còn hạn, giá/tồn kho khớp |
| req-test-001 | Chưa dùng tạo đơn trước case M04; nếu đã dùng sẽ trả already_exists |

`initializeDemoDatabase` chỉ tạo hồ sơ và sản phẩm, không tự tạo các mã đơn/preview TEST. TV3 phối hợp TV1 tạo fixture bằng tool/backend trước khi chạy hoặc thay ID trong query/expect bằng ID được trả về thật. Khởi tạo lại trạng thái phù hợp trước mỗi lần đo; không để case trước làm biến đổi fixture của case sau. Preview hết hạn sau 600 giây nên phải tạo mới gần lúc chạy.

Trong ứng dụng thực tế, request_id nên do UI tạo và giữ lại khi retry. Ở M04, mã được ghi rõ trong ngữ cảnh để đo khả năng truyền đúng arguments; đây không phải kiểm thử việc UI sinh mã.

## 6. Cách đọc kết quả đúng với runner hiện tại

- `run_eval.py` dùng các lượt trước làm ngữ cảnh và chỉ gọi model cho lượt cuối. Nó không thực sự chạy lần lượt từng lượt để kiểm tra cả hội thoại.
- `expect.args` được đối chiếu theo subset: các giá trị ghi trong expect phải khớp; runner không mặc nhiên chặn mọi argument thừa. Cần đọc actual_tool_calls để phát hiện model bịa user_id hoặc key. Schema đã đặt additionalProperties=false nhưng vẫn phải kiểm tra log.
- Runner chấm tool_calls/args, không tự chấm trạng thái SQLite hoặc tính đúng đắn của mọi output. Model gọi đúng tool nhưng output là session_required vẫn có thể đạt điểm routing. Không ghi nhận đó là bằng chứng implementation/integration đã chạy thành công.
- Với S05, M01, M04, M05: đọc thêm tool_results để xác nhận needs_confirmation và kiểm tra SQLite không có thay đổi nghiệp vụ. Phần phê duyệt và thực thi cần tool test/UI test riêng.
- Với M03: no_tool chỉ chứng minh không gọi tool ở lượt cuối, không chứng minh nội dung câu trả lời đã phù hợp.
- Các case dùng ngữ cảnh assistant viết sẵn là fixture hội thoại, không phải transcript do model thật tạo. Không trình bày chúng như bằng chứng chat live.

## 7. Checklist bàn giao và báo cáo

- [ ] Chọn case phù hợp với scope chung và giữ tổng 10 case, 5 single + 5 multi.
- [ ] Có ít nhất một case route tới tool mới của Linh.
- [ ] Thống nhất chính sách hỏi lại/phê duyệt với TV1 trước khi chốt expect.
- [ ] Chuẩn bị fixture và host session nếu kiểm tra kết quả tool thật.
- [ ] Ghép vào `starter_v0/data/eval_group.json`; giữ nguyên case base và extension.
- [ ] Kiểm tra ID duy nhất, phase B, failure_type hợp lệ, query hoặc turns, expect và metadata.what_it_tests.
- [ ] Chạy group eval trên phiên bản artifacts đã tích hợp, lưu run JSON thật.
- [ ] Chỉ dùng run đo đủ case và không có provider error cho bảng metric.
- [ ] Phân biệt kết quả routing/args với kết quả tool và UI xác nhận.
- [ ] Ghi case, kết quả và đường dẫn bằng chứng vào B3 của báo cáo nhóm.

**TV3 điền sau khi thực hiện:**

- Case đã chọn: ...
- Phiên bản prompt/tools và model/provider: ...
- Fixture và cách reset: ...
- Run JSON: ...
- Kết quả / lỗi quan sát được: ...
- Việc còn cần TV1/TV2/TV4 hỗ trợ: ...

Nguồn: README.md; docs/TV2_MAU_QUYET_DINH_TOOL.md; docs/TV2_LINH_HANDOFF.md; starter_v0/artifacts/tools_tv2.fragment.json; starter_v0/run_eval.py. Tài liệu này không thay thế log thực nghiệm.
