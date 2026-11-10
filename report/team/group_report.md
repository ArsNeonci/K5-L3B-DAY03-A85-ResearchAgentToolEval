# Báo cáo nhóm — A85 — Research Agent Tool Eval

## 1. Thông tin nhóm

- Lớp: K5-L3B. Phân công và báo cáo cá nhân: [TEAM.md](../../TEAM.md).
- Provider/model: OpenRouter / openai/gpt-4o-mini. Bản cuối: v7-final.
- Cập nhật: 11/11/2026 (GMT+7). Không hồi tố thời gian hoàn thành: bản Phần A hoàn thiện này được bổ sung sau mốc showdown.

## 2. PHẦN A — Giới thiệu agent

### A1. Chức năng, lệnh chạy và link dùng thử

Agent tra cứu web/X/arXiv hoặc policy nội bộ, định dạng kết quả và có sáu tool hồ sơ/đơn hàng demo trên SQLite. Các thay đổi hồ sơ/tạo/hủy đơn phải qua nút phê duyệt; dữ liệu commerce là dữ liệu giả, không thanh toán thật.

```powershell
cd starter_v0
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1
```

**Link dùng thử trên máy chạy:** http://127.0.0.1:8502 — đã kiểm tra health HTTP 200. Người dùng đã chọn chỉ localhost, không mở public. Link này không mở từ máy khác; chưa có bằng chứng người ngoài nhóm dùng được link public.

Key provider có trong .env ở gốc repo hoặc starter_v0/.env; DAY03_ENV_FILE được ưu tiên nếu dùng file ngoài. Không commit .env. Hiện provider hoạt động; Tavily/Firecrawl/RapidAPI chưa được cấu hình nên lookup/fetch/X trả lỗi cấu hình rõ ràng thay vì giả dữ liệu. Policy, SQLite và API arXiv công khai vẫn dùng được. UI chặn Telegram thật.

### A2. Tool của agent

| Tool | Chức năng | Nhóm tự viết mới? |
|---|---|---|
| clarify | Hỏi lại và chờ người dùng | Không |
| timeline | Bài đăng theo tài khoản X (RapidAPI) | Không |
| social_search | Bài đăng theo chủ đề X (RapidAPI) | Không |
| lookup | Tìm web/tin tức (Tavily) | Không |
| fetch | Đọc URL (Firecrawl) | Không |
| format | Định dạng dữ liệu đã có | Không |
| send | Gửi Telegram sau xác nhận; bị chặn trong UI/eval mặc định | Không |
| policy | Tra cứu policy markdown nội bộ | Không |
| papers | Tìm paper arXiv qua API công khai | Không |
| paper_text | Đọc PDF arXiv | Không |
| get_my_profile | Đọc hồ sơ demo | Có |
| update_profile | Chuẩn bị/sửa tên hoặc địa chỉ | Có |
| preview_order | Xem trước giá và địa chỉ, chưa tạo đơn | Có |
| place_order | Tạo đơn demo sau phê duyệt | Có |
| get_order_status | Xem đơn demo | Có |
| cancel_order | Hủy đơn pending sau phê duyệt | Có |

### A3. Câu hỏi mẫu

1. Tìm quy định công ty về trích dẫn nguồn nghiên cứu và tóm tắt các điểm chính.
2. Đổi địa chỉ giao hàng của tôi. Sau khi được hỏi, trả lời: Địa chỉ demo B; kiểm tra nội dung rồi bấm Đồng ý hoặc Từ chối.
3. Xem trước 2 cuốn DEMO-NOTEBOOK, dùng địa chỉ hiện tại; chưa đặt đơn.
4. Xem tên hiển thị và địa chỉ giao hàng hiện tại của tôi.
5. Gửi lên Telegram đúng nội dung: Bản tin nghiên cứu demo A85. Quan sát hỏi xác nhận và thông báo chặn gửi trong demo.

## 3. Giải pháp

- Giữ nguyên testcase base/extension của starter, giữ run v0–v3 và snapshot prompt/tools lịch sử.
- Tối ưu prompt theo log: bỏ chỉ dẫn đoán/gửi luôn; thêm routing; sau tích hợp bổ sung thứ tự ưu tiên hỏi lại và xử lý xác nhận đúng nội dung. Không sửa scorer để làm đẹp điểm.
- Sáu tool SQLite có validation, error dict, transaction, khóa xác nhận dùng một lần. request_id được host sinh ổn định theo preview, không do model đoán; retry trả đơn cũ.
- Chat UI và console đều mở session cho tool commerce. UI hiển thị pending action trước nút đồng ý/từ chối và lưu transcript đầy đủ có hash/version, che khóa/credential.
- Eval dùng fixture SQLite riêng, mặc định không gửi Telegram; unit/UI tests dùng mock/fake provider, tách biệt với live model run.
- Hướng dẫn một lệnh: [FINAL_RUNBOOK.md](../../docs/FINAL_RUNBOOK.md).

## 4. PHẦN B — Kết quả và bằng chứng

### B1. Version Evidence

Chi tiết giả thuyết, metric trước/sau, prompt_hash, tools_hash và file run nằm trong [version_log.csv](../../starter_v0/artifacts/version_log.csv). Mỗi run dưới đây đo đủ case, provider_error_cases=0. Base v0–v3 lần lượt 65%, 85%, 95%, 95%; version không tăng vẫn được giữ và phân tích.

| Version | Suite | PASS | Routing | Arguments | Run JSON |
|---|---|---:|---:|---:|---|
| v0 | base | 13/20 | 75% | 65% | [v0_B_base_openrouter_20261110T181418169230.json](../../starter_v0/runs/v0_B_base_openrouter_20261110T181418169230.json) |
| v1 | base | 17/20 | 90% | 85% | [v1_B_base_openrouter_20261110T184716617005.json](../../starter_v0/runs/v1_B_base_openrouter_20261110T184716617005.json) |
| v2 | base | 19/20 | 100% | 95% | [v2_B_base_openrouter_20261110T185648929400.json](../../starter_v0/runs/v2_B_base_openrouter_20261110T185648929400.json) |
| v3 | base | 19/20 | 100% | 95% | [v3_B_base_openrouter_20261110T190619466814.json](../../starter_v0/runs/v3_B_base_openrouter_20261110T190619466814.json) |
| v3 | group | 8/10 | 100% | 80% | [v3_B_group_openrouter_20261111T000148799392.json](../../starter_v0/runs/v3_B_group_openrouter_20261111T000148799392.json) |
| v4-integrated | base | 18/20 | 95% | 90% | [v4-integrated_B_base_openrouter_20261111T014523807626.json](../../starter_v0/runs/v4-integrated_B_base_openrouter_20261111T014523807626.json) |
| v5-final | base | 20/20 | 100% | 100% | [v5-final_B_base_openrouter_20261111T014717860925.json](../../starter_v0/runs/v5-final_B_base_openrouter_20261111T014717860925.json) |
| v5-final | group | 8/10 | 90% | 80% | [v5-final_B_group_openrouter_20261111T014821748050.json](../../starter_v0/runs/v5-final_B_group_openrouter_20261111T014821748050.json) |
| v6-confirmation | group | 9/10 | 100% | 90% | [v6-confirmation_B_group_openrouter_20261111T015036404227.json](../../starter_v0/runs/v6-confirmation_B_group_openrouter_20261111T015036404227.json) |
| v7-final | base | 20/20 | 100% | 100% | [v7-final_B_base_openrouter_20261111T015243285356.json](../../starter_v0/runs/v7-final_B_base_openrouter_20261111T015243285356.json) |
| v7-final | base | 20/20 | 100% | 100% | [v7-final_B_base_openrouter_20261111T020314116121.json](../../starter_v0/runs/v7-final_B_base_openrouter_20261111T020314116121.json) |
| v7-final | group | 9/10 | 100% | 90% | [v7-final_B_group_openrouter_20261111T015225969730.json](../../starter_v0/runs/v7-final_B_group_openrouter_20261111T015225969730.json) |
| v7-final | group | 10/10 | 100% | 100% | [v7-final_B_group_openrouter_20261111T015412107306.json](../../starter_v0/runs/v7-final_B_group_openrouter_20261111T015412107306.json) |
| v7-final | group | 10/10 | 100% | 100% | [v7-final_B_group_openrouter_20261111T020330708243.json](../../starter_v0/runs/v7-final_B_group_openrouter_20261111T020330708243.json) |

v4/v5 giữ cả lần có regression; v6 xác nhận rõ nội dung giúp group từ 8/10 lên 9/10. v7 giữ base 20/20, group strict vẫn 9/10. Lần group cuối đạt 10/10 sau sửa thiết kế G09: chỉ chấm topic/timeframe, không exact-match query đồng nghĩa. Đây là **thay đổi thiết kế eval**, không nhận là model tự cải thiện. Bản strict ở data/history/eval_group_v4_strict_query.json và log 9/10 vẫn giữ nguyên. Bộ group v3 gốc lưu tại data/history/eval_group_v3.json.

Artifact cuối: `v7-final+p8f1ffce73931+tbbfd57e1b138`. Base cuối 20/20 và group cuối 10/10 đều là API run thật, không phải replay hay fake provider. Không quy đổi các tỷ lệ này thành điểm toàn bài /100.

### B2. Failure Analysis


Lấy từ `results[*].result.failures` trong run JSON.

Run v0: [`runs/v0_B_base_openrouter_20261110T181418169230.json`](../../starter_v0/runs/v0_B_base_openrouter_20261110T181418169230.json) — `openai/gpt-4o-mini` qua OpenRouter, 13/20 PASS (`case_accuracy=0.65`, `tool_routing_accuracy=0.75`, `argument_accuracy=0.65`, `multiturn_accuracy=1.0`).

| Case ID                     | Failure Type                                  | Actual Tool Calls                                                        | What Failed                                                                 | Fix                                                                                                                                 |
| --------------------------- | --------------------------------------------- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| R03_web_news_routing        | wrong_tool (observed: wrong_arg_value)        | `lookup(query="AI news", topic="news", timeframe="day")`                 | Đúng tool nhưng `query` bị nhét thêm chữ "news" ("AI news" thay vì "AI")    | `tools.yaml`: mô tả `query` chỉ chứa chủ đề, ý "tin tức" thể hiện qua `topic=news`                                                  |
| R08_out_of_scope            | out_of_scope (observed: unexpected_tool_call) | `send(text="Nguyên hàm của x^2 là …")`                                   | Câu hỏi toán ngoài phạm vi research nhưng agent lại gửi đáp án lên Telegram | Prompt: bỏ câu "cứ gửi luôn", thêm rule ngoài phạm vi thì trả lời/từ chối, không gọi tool                                           |
| R10_missing_handle          | missing_info (observed: missing_tool_call)    | `timeline(screenname="sama")`                                            | Không nói tài khoản nào → agent tự đoán Sam Altman thay vì `clarify`        | Prompt: bỏ câu "pick a well-known account like Sam Altman", thêm rule thiếu handle → `clarify`                                      |
| R11_missing_url             | missing_info (observed: missing_tool_call)    | `fetch(url="https://example.com/article")`                               | "bài viết này" không có URL → agent bịa URL                                 | Prompt: bỏ câu "assume a likely URL", thiếu URL → `clarify`                                                                         |
| R12_confirm_before_send     | wrong_boundary (observed: missing_tool_call)  | `send(text="Bản tin này")`                                               | Gửi Telegram ngay, không hỏi xác nhận                                       | Prompt + `tools.yaml`: `send` chỉ gọi với `confirmed=true` sau khi user xác nhận nội dung; trước đó `clarify(response_type=yes_no)` |
| R13_parallel_web_and_tweets | wrong_tool (observed: wrong_arg_value)        | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | `lookup` thiếu `topic=news` và `query` dư "news"                            | Như R03, thêm rule "tin tức/hôm nay" → `topic=news`; prompt bỏ "single step" để cho phép gọi nhiều tool                             |
| R14_out_of_scope_coding     | out_of_scope (observed: unexpected_tool_call) | `send(text="Dưới đây là một hàm Python …")`                              | Yêu cầu viết code ngoài phạm vi nhưng agent gửi lên Telegram                | Như R08                                                                                                                             |



**Bổ sung sau tích hợp:** G02 của group v3 có gọi clarify(text), không phải trả lời thẳng. G09 dùng đúng timeframe=year, chỉ khác query “Tesla electric vehicles” so với “Tesla”; mô tả cũ về timeframe đã được sửa tại đây. PASS routing của hai case TV2 trong group v3 vẫn đi kèm session_required; G06 send PASS routing nhưng thiếu cấu hình Telegram. Không coi các PASS đó là bằng chứng CRUD/gửi thành công.

v4 từng gọi social_search với query rỗng khi thiếu account/topic; sửa bằng thứ tự quyết định trong v5. v5/v6 còn hỏi xác nhận lặp khi user đã xác nhận nguyên văn; v6 giải thích rõ ngữ cảnh user. Lỗi send nhận chuỗi false và wrapper request_id trùng được tái hiện rồi sửa, có regression test.

### B3. Team Eval Cases

Dataset hiện tại: [eval_group.json](../../starter_v0/data/eval_group.json), đúng 10 case, 5 single + 5 multi; route đủ 6 tool mới. Run tương ứng: [v7-final_B_group_openrouter_20261111T020330708243.json](../../starter_v0/runs/v7-final_B_group_openrouter_20261111T020330708243.json). Fixtures PREVIEW-EVAL-001 và DEMO-EVAL-ORDER thuộc tài khoản demo, do host tạo; không phải mã model tự bịa.

| Case | Loại | Tool kỳ vọng | Kết quả | Mục tiêu |
|---|---|---|---|---|
| G01_policy_internal_routing | Single | policy | PASS | Nhận diện câu hỏi về quy định nội bộ công ty -> Route vào tool policy thay vì tìm trên web. |
| LINH_S01_profile_read | Single | get_my_profile | PASS | Yêu cầu chỉ đọc hồ sơ phải chọn get_my_profile, không gọi cập nhật hoặc tìm kiếm web. |
| LINH_S02_preview_quantity | Single | preview_order | PASS | Xem trước 2 cuốn DEMO-NOTEBOOK, dùng địa chỉ hiện tại. Chưa đặt đơn. |
| LINH_S03_order_status | Single | get_order_status | PASS | Xem trạng thái đơn DEMO-EVAL-ORDER của tôi, không hủy. |
| LINH_S04_cancel_prepare | Single | cancel_order | PASS | Chuẩn bị hủy đơn DEMO-EVAL-ORDER để tôi kiểm tra rồi bấm xác nhận. |
| LINH_M01_fill_address | Multi | update_profile | PASS | Ghép yêu cầu đổi địa chỉ ở lượt trước với dữ liệu bổ sung ở lượt cuối; chuẩn bị cập nhật đúng field/value. |
| LINH_M02_place_prepare | Multi | place_order | PASS | Giữ preview_id từ ngữ cảnh; wrapper cấp request_id; chỉ chuẩn bị, chưa tạo đơn khi thiếu phê duyệt. |
| G07_multiturn_clarify_missing_paper_query | Multi | papers | PASS | Turn 1 nói chung chung về arXiv, Turn 2 bổ sung từ khóa -> Gọi đúng tool papers với query tương ứng. |
| G09_multiturn_timeframe_correction | Multi | lookup | PASS | Sửa timeframe week thành year và giữ topic=news. Không chấm exact query vì Tesla electric vehicles vẫn đúng chủ đề; kiểm tra chủ đề bằng actual_tool_calls. Bản strict query và run 9/10 được giữ nguyên để đối chiếu. |
| G10_multiturn_send_exact_content | Multi | send | PASS | Xác nhận gắn với nội dung cụ thể. Eval đo routing và chặn gửi thật mặc định; không tính là bonus Telegram. |

Scorer chỉ đo tool calls/args; multi-turn đưa lượt trước vào ngữ cảnh rồi chấm lượt cuối. G09 kiểm tra time range; chủ đề query vẫn được đọc từ actual_tool_calls. Tool lookup còn lỗi thiếu Tavily key; hành vi API bên ngoài chưa được chứng minh chỉ bởi PASS routing. Send bị chặn theo execution_policy, không tính là Telegram thật.

### B4. Live Chat Evidence

Các transcript sau dùng model thật qua OpenRouter và tool thật/local. Input và thao tác widget được script hóa bằng AppTest để tái lập; không trình bày là kiểm thử thủ công bởi người ngoài nhóm. Header evidence_kind=live; test fake-provider được lưu vào thư mục tạm riêng, không trộn vào bằng chứng live.

| Kịch bản / lượt | User input | Tool | Kết quả | Transcript |
|---|---|---|---|---|
| research_policy / 1 | Tìm quy định công ty về trích dẫn nguồn nghiên cứu và tóm tắt các điểm chính, dẫn nguồn nội bộ. | policy | answered | [v7-final_ui_79f56c6fb09d429db680bc7b536ba596.transcript.json](../../starter_v0/transcripts/v7-final_ui_79f56c6fb09d429db680bc7b536ba596.transcript.json) |
| clarify_then_profile / 1 | Đổi địa chỉ giao hàng của tôi. | Không gọi tool | answered | [v7-final_ui_5a5af311500440d8bc5bf5bcd62bf088.transcript.json](../../starter_v0/transcripts/v7-final_ui_5a5af311500440d8bc5bf5bcd62bf088.transcript.json) |
| clarify_then_profile / 2 | Đổi sang Địa chỉ demo B. | update_profile | waiting_for_user | [v7-final_ui_5a5af311500440d8bc5bf5bcd62bf088.transcript.json](../../starter_v0/transcripts/v7-final_ui_5a5af311500440d8bc5bf5bcd62bf088.transcript.json) |
| clarify_then_profile / 3 | [UI] Đồng ý thực hiện | update_profile | host_action | [v7-final_ui_5a5af311500440d8bc5bf5bcd62bf088.transcript.json](../../starter_v0/transcripts/v7-final_ui_5a5af311500440d8bc5bf5bcd62bf088.transcript.json) |
| send_confirmation / 1 | Gửi lên Telegram đúng nội dung: Bản tin nghiên cứu demo A85. | clarify | waiting_for_user | [v7-final_ui_40ef006d5fc7466d9a09911a601b82e2.transcript.json](../../starter_v0/transcripts/v7-final_ui_40ef006d5fc7466d9a09911a601b82e2.transcript.json) |
| send_confirmation / 2 | Tôi xác nhận gửi nguyên văn: Bản tin nghiên cứu demo A85. | send | answered; Telegram bị chặn, chưa gửi | [v7-final_ui_40ef006d5fc7466d9a09911a601b82e2.transcript.json](../../starter_v0/transcripts/v7-final_ui_40ef006d5fc7466d9a09911a601b82e2.transcript.json) |

Script tái lập: [record_live_demo.py](../../starter_v0/scripts/record_live_demo.py). Transcript v0 cũ được giữ để đối chiếu, không đổi nhãn thành bản cuối. Kịch bản sửa hồ sơ ghi cả bước host approval và kết quả updated; kịch bản Telegram chưa gửi ra ngoài.

### B5a. Tool, unit test và UI

| Thành phần | Bằng chứng | Kết quả / giới hạn |
|---|---|---|
| 6 tool mới | tools/get_my_profile, update_profile, preview_order, place_order, get_order_status, cancel_order; mỗi folder có TOOL.md | Đọc/ghi SQLite giả; khóa xác nhận gắn session/action/payload |
| Unit test | [test_tv2_tools.py](../../starter_v0/tests/test_tv2_tools.py), [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) | ≥3 test/tool mới; test TODO đã được thay bằng assertion thực |
| UI/CLI integration | [test_ui_integration.py](../../starter_v0/tests/test_ui_integration.py), [test_runtime_host.py](../../starter_v0/tests/test_runtime_host.py) | Session chat, đồng ý/từ chối, transaction, transcript và console approval |
| Kết quả toàn suite | [JUnit](../../starter_v0/analysis/pytest_final.xml), [final_check.json](../../starter_v0/analysis/final_check.json) | 155 passed + 16 subtests; 0 failed, 0 skipped; JUnit đếm 171 gồm subtests |
| UI | [app.py](../../starter_v0/app.py), Streamlit trong requirements | Localhost hoạt động; public link không mở theo lựa chọn người dùng |

Ví dụ lỗi eval không bắt nhưng unit test bắt: model có thể gửi confirmed dưới dạng chuỗi “false”; Python truthiness trước đây vẫn gửi. Regression test khẳng định mọi giá trị khác boolean True đều không gọi mạng. Wrapper nhận request_id thừa cũng phải trả error dict, không raise TypeError.

### B5. Bonus Evidence

- Đề nghị xét bonus ≥4 tool mới: có 6 tool, registration, TOOL.md, ≥3 test/tool và eval route cả 6, đều PASS trong run cuối. Không tự cộng 3 điểm vào điểm chính.
- Đề nghị xét Test challenge: toàn suite 0 skipped và có regression cho bug send của tool có sẵn. Không tự cộng 1 điểm vào điểm chính.
- Telegram thật: không thực hiện; không có status sent thật để nhận bonus.

### B7. Small Local Model

Không thực hiện bonus này; không có hai model local hoặc hai vòng tối ưu local. Không dùng fake provider để giả bằng chứng model local.

## 5. Khó khăn và cách xử lý

1. Key đặt ở .env gốc repo thay vì starter_v0: env_loader đã hỗ trợ cả hai, file starter override root, DAY03_ENV_FILE có ưu tiên cao nhất. Không log giá trị key.
2. Tavily/Firecrawl/RapidAPI chưa có key: giữ error dict rõ ràng và ghi giới hạn; không giả kết quả tìm kiếm. Provider OpenRouter hoạt động và các run model đều có log thật.
3. Windows sandbox chặn tempfile: chạy kiểm tra với quyền thực thi phù hợp, SQLite tạm nằm trong runtime và được dọn; không bỏ validation để test xanh.
4. Prompt mơ hồ và eval query quá cứng: giữ cả log FAIL, sửa thứ tự rule bằng giả thuyết, rồi sửa đúng phạm vi expectation G09 có giải thích và archive.
5. Bật tunnel public đã bị auto-review chặn; sau đó người dùng chọn chỉ localhost. Không thử đường vòng và không ghi URL public giả.
6. Không xác nhận được deadline/gia hạn hoặc mốc Phần A trước showdown từ repo; báo cáo ghi ngày bổ sung thật, không sửa ngày commit.

## 6. Tổng hợp đóng góp

- TV1 Võ Hồng Lương: baseline, v1–v3, declaration/prompt và tích hợp registry.
- TV2 Chu Quang Linh: 6 tool/SQLite/test và bàn giao; đợt hoàn thiện dùng Codex sửa runtime, test, báo cáo và đo lại trên yêu cầu của người dùng.
- TV3 Hồ Anh Tú: bộ group v3, run group và phân tích B2/B3; bộ group bổ sung phủ 6 tool được điều chỉnh trong đợt hoàn thiện có lưu lịch sử.
- TV4 Nguyễn Minh Quân: UI/requirements/transcript ban đầu; dùng Codex. Đợt hoàn thiện bổ sung session chat, host approval và ghi transcript.
- Chi tiết/bằng chứng: [TEAM.md](../../TEAM.md) và 4 báo cáo cá nhân. Không tạo trải nghiệm tự đánh giá, commit hay kết quả giả cho cá nhân khác.

## 7. B6 — Reflection và giới hạn

Prompt/declaration điều khiển model lựa chọn hành động; backend phải tự chặn input sai và thao tác chưa được phê duyệt. Test fake-provider chứng minh code nhưng không thay thế eval thật. Eval routing 100% không chứng minh Tavily/Firecrawl/X đang hoạt động, không chứng minh Telegram đã gửi và không tự quy thành 100 điểm lab.

Chỉ một lần đo mỗi trạng thái không chứng minh tính ổn định thống kê; OpenRouter/model có thể dao động ở lần chạy khác. G09 cuối đạt nhờ expectation được sửa đúng mục tiêu đo, không được mô tả thành cải thiện model. Base gốc và scorer không bị sửa để tăng điểm.

SQLite chỉ dùng dữ liệu giả và host chọn tài khoản demo; chưa có authentication production, thanh toán, kiểm chứng tải hoặc concurrency nhiều người dùng thật. Localhost không dùng được từ máy khác. Những giới hạn này được nêu công khai thay vì đánh dấu hoàn thành giả.

## 8. Tài liệu tham khảo

- [README lab](../../README.md), [Rubric](../../RUBRIC.md), [Rules](../../RULES.md), [Submission](../../SUBMISSION.md).
- [Tool folder contract](../../starter_v0/tools/README.md), mẫu fixture/test có sẵn trong starter.
- [Bàn giao TV2](../../docs/TV2_LINH_HANDOFF.md), [ghi chú tích hợp TV1](../../docs/TV1_INTEGRATION_NOTES.md), [runbook cuối](../../docs/FINAL_RUNBOOK.md).
- Các số liệu và kết luận lấy từ run/transcript/JUnit trong repo; không dùng ảnh hoặc cảm nhận thay cho log.
