# Báo cáo cá nhân — Võ Hồng Lương

## 1. Thông tin thành viên

- Họ tên: Võ Hồng Lương
- MSSV: 2A202603839
- Email: 26ai.luongvh@vinuni.edu.vn
- GitHub: luongvh2510
- Vai trò: Prompt, phiên bản và tích hợp

## 2. Phần việc phụ trách

- **Setup & baseline (CP1):** cấu hình provider (`openai/gpt-4o-mini` qua OpenRouter) và key tool trong `.env`, chạy preflight, chạy baseline v0 trên prompt/tool declaration gốc của starter, phân loại các case FAIL.
- **Tối ưu prompt & tool declaration (CP2):** chịu trách nhiệm `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`. Mỗi version sửa một giả thuyết rút ra từ run JSON, chạy lại base eval, so metric trước/sau.
- **Quản lý phiên bản:** ghi `starter_v0/artifacts/version_log.csv` cho từng version, đối chiếu từng dòng với run JSON; điền bảng B1, B2 và mục B6 Reflection trong `report/team/group_report.md`.
- **Tích hợp (CP3):** đăng ký tool mới của TV2 vào registry `starter_v0/tools/__init__.py` và `tools.yaml`, giữ contract test xanh, chốt quy ước giữa tool – prompt – UI và viết tài liệu bàn giao.
- **Merge:** review và merge PR của thành viên vào `main`, kiểm tra không sửa chồng file và `pytest` 0 failed.

## 3. Đóng góp cụ thể

### 3.1. Baseline v0

- Run hợp lệ (`provider_error_cases = 0`, `measured_cases = total_cases = 20`): 13/20 PASS, `case_accuracy = 0.65`, `tool_routing_accuracy = 0.75`, `argument_accuracy = 0.65`, `multiturn_accuracy = 1.0`.
- Lần chạy đầu thiếu key tool trong `.env` (tool trả `Missing ..._API_KEY`); đã bổ sung key và chạy lại để có run v0 chính thức.
- Phân loại 7 case FAIL (bảng B2): 5 case do chỉ dẫn xấu cố ý trong prompt (R08, R14 gọi `send` cho câu hỏi ngoài phạm vi; R10, R11 đoán handle/URL; R12 gửi không xác nhận), 2 case do convention args của `lookup` (R03, R13 nhét "news" vào `query`, thiếu `topic=news`).

### 3.2. Vòng lặp v1 → v3

| Version | Artifact | Giả thuyết | case_accuracy | Kết quả |
|---|---|---|---:|---|
| v1 | `system_prompt.md` | Bỏ chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không xác nhận, ép một bước) | 0.65 → 0.85 | Sửa R08, R14, R03, R13. R10, R11 vẫn đoán vì eval ép `tool_choice="required"` (`run_eval.py:293`) mà prompt chưa nói hỏi lại bằng tool nào |
| v2 | `system_prompt.md` | Thêm rule routing đầy đủ, gồm `clarify` text/yes_no trước `send` | 0.85 → 0.95 | Sửa R10, R11. R12 vẫn `clarify(text)` thay vì `yes_no` |
| v3 | `tools.yaml` | Viết lại description mọi tool (khi nào dùng/không dùng, convention args, boundary `send` với `confirmed=true`) | 0.95 → 0.95 | Giả thuyết sửa R12 **không được xác nhận**; các case khác giữ nguyên |

- Cách làm: v1 giữ nguyên câu mở đầu và chỉ thay đúng 3 đoạn chỉ dẫn xấu, không nêu tên tool, để tách bạch với giả thuyết routing ở v2. v3 chỉ đổi `description` — tên tool, param, type, enum, default, required giữ nguyên (kiểm tra bằng script so sánh schema trước khi ghi).
- Nhận định về R12: yêu cầu "Đăng bản tin **này**" vừa thiếu nội dung vừa là yêu cầu gửi, nên model áp rule "thiếu thông tin → `text`" trong system prompt thay vì rule "gửi → `yes_no`" trong description. Boundary vẫn giữ: từ v1 đến v3 model không gọi `send` lần nào (v0 gọi 3 lần không xác nhận).

### 3.3. Tích hợp 6 tool SQLite demo của TV2 (Linh)

- Tạo nhánh `tv1-integrate-tools` từ `main`, merge `tv2-linh` (TV2 chỉ thêm file mới, không sửa file chung).
- Đăng ký `get_my_profile`, `update_profile`, `preview_order`, `place_order`, `get_order_status`, `cancel_order` trong `tools/__init__.py`; khai báo 6 tool trong `tools.yaml` theo schema bàn giao, description theo mẫu v3; thêm 4 dòng routing hồ sơ/đơn hàng vào prompt.
- Chốt 3 quyết định với nhóm và **không sửa code/test của TV2**:
  1. Xác nhận thao tác ghi bằng nút UI theo handoff (model không có `confirmation_key` nên không thể tự ghi), khác với luồng `clarify(yes_no)` → `send(confirmed=true)`.
  2. `request_id` do registry tự sinh qua wrapper `place_order_auto_request_id`, model chỉ gửi `preview_id` → không phải bịa mã.
  3. `demoSession` để host/UI (TV4) mở; trong eval tool TV2 trả `session_required` nhưng không ảnh hưởng chấm điểm.
- Kiểm thử luồng trên SQLite tạm: `preview_order` → `place_order` qua wrapper (`needs_confirmation`, `request_id=REQ-...`) → `issueConfirmation` + `placeOrder` gốc → `status: created`; trường lạ vẫn trả `unsupported_fields`.
- Viết `docs/TV1_INTEGRATION_NOTES.md`: quyết định, lý do, việc cho TV2/TV3/TV4 (code mẫu nút xác nhận, kỳ vọng eval cho 6 tool).
- Kết quả: contract test 85 passed; toàn suite 122 passed, 17 skipped, 0 failed.

### 3.4. Merge

- PR #1 `tv1-integrate-tools` → `main` trên repo nhóm, merge commit để giữ nguyên commit của TV2.

### 3.5. Reflection (B6 trong group report)

- Tổng hợp từ run v0–v3: fix hành vi và routing `clarify` thuộc system prompt (v1, v2); convention args và phạm vi tool thuộc `tools.yaml` (v3, bỏ `request_id` khỏi schema `place_order`).
- Chỉ ra các failure cần review thủ công: R12 (`clarify(text)` hợp lý, boundary vẫn giữ), nội dung từ chối R08/R14 không được chấm, kết quả thật của tool không ảnh hưởng điểm, luồng nút UI của TV2 nằm ngoài eval, mỗi version chỉ chạy một lần.
- Đề xuất giả thuyết vòng sau: thứ tự ưu tiên rule cho R12, chạy lặp để đo dao động, bỏ ví dụ handle trùng eval, đo v3 bằng suite group/extension.

## 4. Bằng chứng

- **Run JSON:** `starter_v0/runs/v0_B_base_openrouter_20261110T181418169230.json`, `v1_B_base_openrouter_20261110T184716617005.json`, `v2_B_base_openrouter_20261110T185648929400.json`, `v3_B_base_openrouter_20261110T190619466814.json`
- **Version log:** `starter_v0/artifacts/version_log.csv` (v0–v3); bảng B1, B2 và mục 7 (B6 Reflection) trong `report/team/group_report.md`
- **Commit:**
  - `a11009a`, `5030c61`, `5b9176e` — baseline v0, CP1
  - `e8a8541` — v1
  - `6683a53` — v2 
  - `e05baad` — v3 
  - `7f012f1` — điền group report sau CP2
  - `14c2c0c`, `3f23e69` — merge TV2 và tích hợp tool
  - PR #1 / `c04f5da` — merge vào `main`
- **Tài liệu:** `docs/TV1_INTEGRATION_NOTES.md`
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng **Claude Code** (trợ lý AI trong VS Code) để: đọc toàn repo và lập checklist; đọc run JSON, tóm tắt case FAIL; soạn phần tích hợp (registry, wrapper, `tools.yaml`); viết tài liệu bàn giao.
  - Cách tự kiểm tra:
    - Mọi thay đổi do AI soạn đều được đề xuất trước, tôi đọc và duyệt rồi mới áp dụng.
    - Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases.
    - Chạy `pytest tests/test_tool_contract.py` sau mỗi lần sửa `tools.yaml`/registry và toàn suite `pytest` trước khi merge.
    - Kiểm tra diff trước khi commit/merge: không có `.env`, key, token, file SQLite.

## 5. Tự đánh giá

- Đã làm đúng quy tắc mỗi version chỉ sửa theo 1 giả thuyết, có thể giải thích được mỗi version tại sao lại sửa như vậy. Sau 2 bản sửa chất lượng đã tăng rõ rệt, tuy nhiên R12 vẫn chưa sửa được qua 3 version.
- Có một số lỗi nhỏ khi gõ powershell các lệnh git.
- Nếu được làm thêm nhiều vòng, tôi sẽ đo độ dao động của model tại mỗi version.


