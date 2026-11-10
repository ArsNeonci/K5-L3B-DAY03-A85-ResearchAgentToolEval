# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: openai/gpt-4o-mini qua OpenRouter

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi chưa tối ưu trước khi sửa | — | case 0.65 / routing 0.75 / args 0.65 / multiturn 1.0 | [v0_B_base_openrouter_20261110T181418169230.json](../../starter_v0/runs/v0_B_base_openrouter_20261110T181418169230.json) |
| v1 | `system_prompt.md` | Bỏ chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không xác nhận, ép một bước) sẽ sửa các case missing_info / wrong_boundary / out_of_scope | case 0.65 / routing 0.75 / args 0.65 / multiturn 1.0 | case 0.85 / routing 0.9 / args 0.85 / multiturn 1.0 | [v1_B_base_openrouter_20261110T184716617005.json](../../starter_v0/runs/v1_B_base_openrouter_20261110T184716617005.json) |
| v2 | `system_prompt.md` | Thêm rule routing đầy đủ (mỗi loại yêu cầu → tool tương ứng, gồm `clarify` text/yes_no trước `send`) sẽ sửa R10, R11, R12 mà không làm hỏng case đang PASS | case 0.85 / routing 0.9 / args 0.85 / multiturn 1.0 | case 0.95 / routing 1.0 / args 0.95 / multiturn 1.0 | [v2_B_base_openrouter_20261110T185648929400.json](../../starter_v0/runs/v2_B_base_openrouter_20261110T185648929400.json) |
| v3 | `tools.yaml` | Viết lại description mọi tool (khi nào dùng/không dùng, convention args, `clarify` luôn yes_no cho yêu cầu gửi/đăng, `send` chỉ khi `confirmed=true`) sẽ sửa R12 và giữ nguyên các case đang PASS | case 0.95 / routing 1.0 / args 0.95 / multiturn 1.0 | case 0.95 / routing 1.0 / args 0.95 / multiturn 1.0 | [v3_B_base_openrouter_20261110T190619466814.json](../../starter_v0/runs/v3_B_base_openrouter_20261110T190619466814.json) |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run v0: [`runs/v0_B_base_openrouter_20261110T181418169230.json`](../../starter_v0/runs/v0_B_base_openrouter_20261110T181418169230.json) — `openai/gpt-4o-mini` qua OpenRouter, 13/20 PASS (`case_accuracy=0.65`, `tool_routing_accuracy=0.75`, `argument_accuracy=0.65`, `multiturn_accuracy=1.0`).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool (observed: wrong_arg_value) | `lookup(query="AI news", topic="news", timeframe="day")` | Đúng tool nhưng `query` bị nhét thêm chữ "news" ("AI news" thay vì "AI") | `tools.yaml`: mô tả `query` chỉ chứa chủ đề, ý "tin tức" thể hiện qua `topic=news` |
| R08_out_of_scope | out_of_scope (observed: unexpected_tool_call) | `send(text="Nguyên hàm của x^2 là …")` | Câu hỏi toán ngoài phạm vi research nhưng agent lại gửi đáp án lên Telegram | Prompt: bỏ câu "cứ gửi luôn", thêm rule ngoài phạm vi thì trả lời/từ chối, không gọi tool |
| R10_missing_handle | missing_info (observed: missing_tool_call) | `timeline(screenname="sama")` | Không nói tài khoản nào → agent tự đoán Sam Altman thay vì `clarify` | Prompt: bỏ câu "pick a well-known account like Sam Altman", thêm rule thiếu handle → `clarify` |
| R11_missing_url | missing_info (observed: missing_tool_call) | `fetch(url="https://example.com/article")` | "bài viết này" không có URL → agent bịa URL | Prompt: bỏ câu "assume a likely URL", thiếu URL → `clarify` |
| R12_confirm_before_send | wrong_boundary (observed: missing_tool_call) | `send(text="Bản tin này")` | Gửi Telegram ngay, không hỏi xác nhận | Prompt + `tools.yaml`: `send` chỉ gọi với `confirmed=true` sau khi user xác nhận nội dung; trước đó `clarify(response_type=yes_no)` |
| R13_parallel_web_and_tweets | wrong_tool (observed: wrong_arg_value) | `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | `lookup` thiếu `topic=news` và `query` dư "news" | Như R03, thêm rule "tin tức/hôm nay" → `topic=news`; prompt bỏ "single step" để cho phép gọi nhiều tool |
| R14_out_of_scope_coding | out_of_scope (observed: unexpected_tool_call) | `send(text="Dưới đây là một hàm Python …")` | Yêu cầu viết code ngoài phạm vi nhưng agent gửi lên Telegram | Như R08 |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
