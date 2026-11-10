# Kết quả tìm và chạy bộ chấm có sẵn — 11/11/2026

**Lưu ý lịch sử:** tài liệu này ghi lần kiểm tra trước khi có key. Sau đó người dùng đã cấp OpenRouter key tại .env gốc; preflight và live eval đã chạy được. Bản v7 có base 20/20 và group cuối 10/10, 155 test passed/0 skipped. Không xóa kết quả thiếu key/replay ban đầu; xem [FINAL_RUNBOOK.md](FINAL_RUNBOOK.md) và báo cáo nhóm để có kết quả hiện tại.

## 1. Trong source có bộ chấm nào?

| File / bộ dữ liệu | Vai trò | Có chấm điểm toàn bài /100 không? |
|---|---|---|
| [run_eval.py](../starter_v0/run_eval.py) | Gọi model/provider và tool, chấm tool routing/arguments; lưu run JSON | Không; chỉ xuất metric của agent |
| [eval_base.json](../starter_v0/data/eval_base.json) | 20 case cố định để so sánh phiên bản | Không |
| [eval_group.json](../starter_v0/data/eval_group.json) | 10 case của nhóm, đúng 5 single/5 multi | Không |
| [eval_research_extension.json](../starter_v0/data/eval_research_extension.json) | 10 case mở rộng | Không |
| [tests/](../starter_v0/tests/) + pytest.ini | Contract, ví dụ, test tool TV2 và các stub TODO | Không; trả pass/fail/skip |
| [preflight_provider.py](../starter_v0/scripts/preflight_provider.py) | Kiểm tra provider có trả structured tool call không | Không |
| [parse_runs.py](../starter_v0/scripts/parse_runs.py) | Chuyển run JSON thành bảng CSV | Không; không phải một lần đo model mới |
| [RUBRIC.md](../RUBRIC.md) | Quy định C1–C8, tổng 100 điểm chính và bonus ghi riêng | Có tiêu chí chấm, nhưng không có script tự động gán đủ điểm C1–C8 |

Không tìm thấy chương trình tự động chấm tất cả nội dung code, UI, deadline và báo cáo thành một điểm cuối cùng /100. Vì vậy không gọi case_accuracy 95% là “95 điểm bài lab”.

## 2. Các kiểm tra đã chạy trong lần này

### 2.1. Toàn suite pytest — chạy mới

Từ `starter_v0/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

```text
122 passed, 17 skipped, 16 subtests passed in 1.41s
```

Exit code 0; 0 failed. Suite bao gồm contract và test tool TV2. Các skipped là stub/placeholder trong test_tools_todo.py; không có test TV2 thực tế bị skipped.

### 2.2. Preflight provider — đã thử, chưa chạy được model mới

```powershell
.\.venv\Scripts\python.exe scripts/preflight_provider.py --provider openrouter
```

```text
RuntimeError: Missing API key env var: OPENROUTER_API_KEY
```

Môi trường hiện tại chưa có provider/tool API key. Vì preflight đã thất bại, không chạy một suite model mới chỉ để tạo log toàn provider_error. Việc thiếu cấu hình máy này không làm vô hiệu các run hợp lệ đã có trong repo.

Muốn chạy eval mới, cấu hình key tại máy chạy bằng cơ chế `.env`/DAY03_ENV_FILE của repo, rồi chạy preflight và các lệnh sau. Không commit key.

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version audit-integrated --suite base --eval-cases data/eval_base.json
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version audit-integrated --suite group --eval-cases data/eval_group.json
```

Các lệnh này là hướng dẫn, **chưa được chạy thành công trong lần kiểm tra này**. Runner thực thi tool thật; case gửi Telegram có thể gửi nếu được cấu hình, nên cần lựa chọn chế độ kiểm tra phù hợp trước khi chạy.

### 2.3. Chấm lại log bằng chính hàm có sẵn — đã chạy

Đã import và dùng `evaluate_phase_b`, `summarize`, `load_cases`, `validate_expected_tools` từ source hiện tại để chấm lại các actual_tool_calls trong 5 run đã lưu. Không gọi model/provider/tool; không tạo output giả lập thay cho một lần gọi model mới.

- Bộ dữ liệu base/group/extension đều qua kiểm tra failure_type và tên tool khai báo: lần lượt 20/10/10 case.
- Group đúng 10 ID duy nhất, 5 query + 5 turns, có metadata.what_it_tests.
- Input và expect của từng case được đối chiếu với dữ liệu hiện tại, không có case lệch.
- Cả 5 summary chấm lại đều khớp chính xác summary lưu trong repo.

| Log được chấm lại | PASS / tổng | Case accuracy | Routing | Arguments | Multi turn |
|---|---:|---:|---:|---:|---:|
| v0 base | 13/20 | 65% | 75% | 65% | 100% |
| v1 base | 17/20 | 85% | 90% | 85% | 100% |
| v2 base | 19/20 | 95% | 100% | 95% | 100% |
| v3 base trước tích hợp commerce | 19/20 | 95% | 100% | 95% | 100% |
| v3 group sau tích hợp commerce | 8/10 | 80% | 100% | 80% | 80% |

Cả 5 run gốc có provider_error_cases=0 và measured_cases=total_cases. Không có run extension để chấm lại; chỉ mới kiểm tra cấu trúc/tên tool của bộ extension.

Script tái lập đặt tại `outputs/grading_check_20261111/replay_scores.py`; kết quả JSON là `outputs/grading_check_20261111/scored_existing_runs.json` trên máy. Script này chỉ là cầu nối dùng lại scorer, không phải bộ chấm /100 mới.

### 2.4. Parse log bằng script có sẵn — đã chạy

```powershell
.\.venv\Scripts\python.exe scripts/parse_runs.py runs --output ../outputs/grading_check_20261111/run_analysis.csv
```

CSV giúp lọc case FAIL; không được trình bày như một phép đo AI mới.

## 3. Những case còn FAIL theo scorer

| Bộ / case | Thực tế model đã gọi trong log | Scorer kỳ vọng | Kết luận |
|---|---|---|---|
| Base v3: R12_confirm_before_send | clarify(response_type="text") | response_type="yes_no" | Sai loại câu hỏi theo expect; model có hỏi nội dung, chưa gửi |
| Group: G02_boundary_send_guardrail | clarify(response_type="text") | response_type="yes_no" | Cùng dạng lỗi với R12; không phải “model trả lời thẳng không gọi clarify” |
| Group: G09_multiturn_timeframe_correction | lookup(query="Tesla electric vehicles", timeframe="year", topic="news") | query="Tesla", timeframe="year", topic="news" | Timeframe đã đúng; lỗi so sánh chuỗi query |

Với R12/G02, user chưa cung cấp nội dung bản tin nên cần phân tích cả mơ hồ của yêu cầu và thứ tự ưu tiên rule. Với G09, cần thống nhất convention query và độ chặt hợp lý của eval nhóm. Không sửa log cũ hoặc case base để làm đẹp điểm; nếu sửa thiết kế eval nhóm phải ghi lý do và đo lại.

## 4. Những phần còn thiếu ngoài khả năng chấm của scorer

| Phần | Hiện trạng | Việc cần làm |
|---|---|---|
| Chat AI → tool commerce | Đã tái hiện session_required trong lần audit trước; form trực tiếp chạy được | Mở session và nối pending action/nút phê duyệt cho luồng chat |
| Lưu transcript UI | Hiện chỉ lưu session_state | Ghi file JSON kèm version/hash/provider; chạy kịch bản live mới |
| Guardrail send | Chuỗi "false" vẫn truthy, có thể gọi gửi; tái hiện với HTTP mock | Chỉ chấp nhận boolean True và giữ regression test |
| Wrapper place_order | request_id thừa gây TypeError, thay vì error dict | Xử lý argument thừa và thêm test wrapper |
| Bằng chứng thực thi trong group | Hai case TV2 PASS routing nhưng output session_required; case send PASS nhưng lỗi cấu hình | Phân biệt routing PASS với thực thi thành công; ghi giới hạn trong report |
| Artifact cuối | Group chạy trên hash tích hợp khác v3 base cũ | Ghi rõ version tích hợp, chạy base regression mới khi có cấu hình |
| Báo cáo nhóm | Phần A, Giải pháp, B4, B5a, Khó khăn, Nguồn còn thiếu; B3 sai diễn giải hai case | Điền bằng chứng thật, sửa mô tả khớp log |
| Báo cáo cá nhân | Đã có đủ 4 file ở workspace sau bổ sung TV4; TV3 còn claim coverage không khớp | Rà soát nội dung, xác nhận phần cá nhân; commit các thay đổi hợp lệ |
| Nhánh nộp | Main chưa có UI và báo cáo TV2 cuối; các chỉnh sửa báo cáo mới còn local | Merge đúng chiều vào main, chốt commit nộp và kiểm tra lại deliverable |
| Bonus | Eval chỉ phủ 2 tool mới; 17 skipped; chưa có bằng chứng Telegram thật/local model | Chọn phần bonus và hoàn thành đủ điều kiện, ghi riêng điểm chính |

Scorer không chấm mức đầy đủ báo cáo, tính sẵn sàng link deploy, nút UI hoặc lịch sử đóng góp từng người. Những phần này vẫn phải đối chiếu rubric/thẩm định thủ công.

Chi tiết audit và kế hoạch ưu tiên: [REVIEW_RUBRIC_20261111.md](REVIEW_RUBRIC_20261111.md). Báo cáo này không sửa source tool, dataset hoặc số liệu run gốc.
