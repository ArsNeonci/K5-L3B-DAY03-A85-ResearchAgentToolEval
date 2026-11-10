# Rà soát bài nộp và bằng chứng theo rubric — 11/11/2026

**Sau khi khắc phục:** audit này là snapshot trước sửa. Bản v7 hiện đã có session chat, UI approval/transcript, wrapper ổn định, send strict boolean, 155 test passed/0 skipped; live base 20/20 và group cuối 10/10. Group có sửa phạm vi expectation G09, giữ strict dataset/run cũ. Báo cáo đã hoàn thiện; chỉ localhost theo lựa chọn người dùng. Các giới hạn key Tavily/Firecrawl/RapidAPI, không Telegram thật và không local-model bonus vẫn được ghi rõ. Xem [runbook cuối](FINAL_RUNBOOK.md) và [báo cáo nhóm](../report/team/group_report.md) cho trạng thái mới.

**Cập nhật hồ sơ sau rà soát:** đã sửa tiêu đề báo cáo Hồ Anh Tú (2A202603811), tạo báo cáo Nguyễn Minh Quân (2A202603794, TV4; dùng Codex) từ code/commit và bằng chứng kiểm tra hiện có, đồng thời bổ sung đóng góp trong TEAM.md. Nhận xét thiếu báo cáo TV4 bên dưới phản ánh snapshot lúc audit; khoảng trống về code, deploy, live transcript và báo cáo nhóm vẫn còn. Báo cáo mới chưa tự động trở thành bằng chứng đã hoàn thành các chức năng còn thiếu.

## Kết luận

Bài có nền tảng code và unit test tốt, đủ run v0–v3 và bộ eval nhóm hợp lệ. Tuy nhiên, chưa đủ bằng chứng để kết luận đạt tối đa điểm chính: thiếu nội dung báo cáo nhóm, thiếu báo cáo TV4, transcript còn dùng artifact starter và nhánh nộp main chưa có UI/bản báo cáo TV2 cuối. Một số lỗi tích hợp không được suite hiện tại phát hiện.

RUBRIC.md quy định C1–C8, tổng 100 điểm chính và bonus tối đa 10 điểm ghi riêng; **không có định nghĩa band A/B/C hoặc bảng trừ điểm chi tiết**. Đánh giá dưới đây là mức sẵn sàng của bằng chứng theo từng tiêu chí, không phải điểm chính thức. Không lấy 95% base hay 80% group quy đổi thẳng thành điểm bài lab.

## 1. Phạm vi và phương pháp

- Snapshot kiểm tra: local `tv2-linh`, commit `04c3dc0`; local main ở `73e83be`.
- Nguồn yêu cầu: [README](../README.md), [Rubric](../RUBRIC.md), [Submission](../SUBMISSION.md), [Checkpoints](../CHECKPOINTS.md), [Rules](../RULES.md).
- Đã chạy toàn suite pytest offline và AppTest trên UI với SQLite giả; fake provider dùng để kiểm tra luồng code, không đo hành vi model thật. Đã mock HTTP cho kiểm tra âm của send.
- Đã đọc 5 run JSON, 3 transcript, version_log, eval_group, báo cáo nhóm và ba báo cáo cá nhân hiện có; đối chiếu artifact hash với lịch sử Git.
- Không chạy lại model/API có phí, không gửi Telegram thật, không tạo link public, không sửa source hoặc nội dung eval để thay đổi điểm. Chưa có bằng chứng người ngoài nhóm dùng được link UI vì A1 chưa có link.
- Không xác nhận được việc nộp LMS hoặc gia hạn deadline từ repo. Không suy diễn timestamp thành xác nhận nộp đúng hạn.

## 2. Kết quả kiểm tra thực tế

### 2.1. Toàn suite

Từ `starter_v0/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

```text
122 passed, 17 skipped, 16 subtests passed in 1.61s
```

Exit code 0; 0 failed. Suite có 85 contract test và 30 test tool TV2. Các số này là thành phần trong 122 passed, không cộng lại thành một tổng mới.

17 skipped gồm 14 stub cho tool có sẵn và 3 placeholder chung cho tool mới trong `test_tools_todo.py`; 30 test TV2 thật nằm ở `test_tv2_tools.py` và đều chạy. Phần bắt buộc về test tool mới có bằng chứng đạt; chưa đạt bonus toàn suite 0 skipped.

### 2.2. UI offline và các lỗi tái hiện

Khu vực form **Hồ sơ & đơn hàng** khởi động và chạy được cả sáu tool. Đã kiểm tra: đọc hồ sơ, chuẩn bị sửa, từ chối không sửa, đồng ý mới sửa, preview tổng 60.000 VND, tạo đơn pending, xem trạng thái, hủy và đọc lại cancelled. Không có exception UI trong kịch bản này.

Các probe bổ sung xác nhận:

| Kiểm tra | Kết quả quan sát | Kết luận |
|---|---|---|
| Fake provider gọi get_my_profile từ chat AI | Tool trả session_required | Chat không mở demoSession, khác với form trực tiếp |
| Chat UI hoàn tất một lượt fake-provider | Không có file transcript mới | App chỉ lưu session_state; chưa đáp ứng ghi bằng chứng chat từ UI |
| Model-facing place_order nhận thêm request_id | TypeError vì truyền trùng keyword request_id | Wrapper chưa trả error dict cho trường thừa, trái mô tả bàn giao |
| send với confirmed=False (boolean) | needs_confirmation; 0 HTTP mock call | Nhánh boolean false đúng |
| send với confirmed="false" (chuỗi) | sent; 1 HTTP mock call | Guardrail chưa kiểm tra kiểu boolean chặt chẽ |
| send với confirmed=True, HTTP mock | sent; 1 HTTP mock call | Chỉ chứng minh logic với mock, không phải Telegram thật |
| Chat UI gọi send đã confirmed | blocked_in_demo | Không thể dùng UI này làm bằng chứng bonus Telegram thật |

Đã thực hiện 29 quan sát/assertion trong probe UI, bao gồm các điều kiện xác nhận lỗi đã tái hiện; không trình bày thành “29 tính năng sản phẩm đều đạt”. Các script và JSON kết quả probe nằm ở `outputs/audit_20261111/` trên máy; chưa commit. Lệnh tái chạy probe được ghi ở mục 10.

## 3. Đối chiếu từng tiêu chí C1–C8

| Tiêu chí | Điểm tối đa | Bằng chứng đã có | Chưa đủ để khẳng định tối đa / việc cần làm |
|---|---:|---|---|
| C1 Baseline và phân tích lỗi | 10 | v0 hợp lệ, 13/20; version_log khớp run; B2 có đủ 7 case FAIL | Mức sẵn sàng cao. Bổ sung phân biệt model định gọi send với việc gửi thành công; guardrail backend đã chặn các call thiếu xác nhận |
| C2 Prompt và declaration | 15 | 16 tool; 85 contract test xanh; routing, convention args, send boundary đã có | Rule “Only use tools when request needs research” mâu thuẫn với routing commerce. send chưa chặn chuỗi false. Chat commerce không có session. Rà soát ưu tiên missing_info/xác nhận để tránh diễn giải lệch |
| C3 Vòng lặp v1–v3 | 20 | Đủ run thật, hash thay đổi, giả thuyết và metric; 0.65 → 0.85 → 0.95 → 0.95 | v3 không tăng điểm vẫn hợp lệ theo rubric. Sau thêm 6 tool, artifact đã khác nhưng vẫn gắn nhãn v3 ở run group; cần ghi rõ phiên bản tích hợp và đo lại base trên trạng thái cuối để kết luận không regression |
| C4 Tool mới và unit test | 15 | 6 tool + TOOL.md + registry/YAML + ≥3 test/tool; pytest 0 failed; form UI chạy được | Wrapper place_order có nhánh TypeError cho request_id thừa; cần regression test và trả error dict. Phân biệt backend chạy được với chat AI chưa tích hợp session. B5a chưa điền bằng chứng này |
| C5 Eval nhóm | 10 | Đúng 10 case, 5 single/5 multi, ID duy nhất, schema đủ; 2 case route tới tool mới; run hợp lệ 8/10 | Hai FAIL không tự động làm mất 20% điểm C5. Cần sửa phân tích G02/G09 theo log; cải thiện case thiếu nội dung gửi. Chưa phủ 4/6 tool mới để lấy bonus tool |
| C6 UI và live chat | 10 | app.py, streamlit trong requirements; form commerce hoạt động; 3 file transcript, tổng 4 lượt | Không có lệnh chạy/link UI thật trong A1; transcript dùng starter, luồng thiếu dữ liệu đã đoán account và thiếu RAPIDAPI_KEY; chưa có UI transcript writer. Cần ghi live chat mới trên artifact cuối và nối chat → confirmation UI |
| C7 Báo cáo nhóm | 10 | B1, B2, B3, B6 có nội dung và log | Phần A, mục 3, B4, B5a, khó khăn và tài liệu tham khảo chưa hoàn thiện. B3 có hai giải thích sai. Chưa có bằng chứng Phần A hoàn thành trước showdown; không bịa thời điểm để bù |
| C8 Cá nhân | 10 | TV1, TV2, TV3 có báo cáo; cả 4 người có commit kỹ thuật | Thiếu báo cáo Nguyễn Minh Quân; TEAM thiếu tên nhóm/lớp chốt/commit nộp và email/GitHub Linh. TV3 còn placeholder và mô tả vượt coverage thật. Nhánh main chưa có UI và báo cáo TV2 hoàn thiện |

Ưu tiên đạt mức cao nhất là hoàn thiện C6/C7/C8 và lỗi guardrail, không phải cố nâng metric bằng cách nới expect. Rubric không yêu cầu mọi case phải PASS hoặc mọi version phải tăng metric; yêu cầu giả thuyết và phân tích trung thực, có bằng chứng.

## 4. Kiểm tra log và tính nhất quán số liệu

### 4.1. Run v0–v3 và group

| Run | Case accuracy | Routing | Arguments | Multi turn | measured / total | Provider errors |
|---|---:|---:|---:|---:|---:|---:|
| v0 base | 0.65 | 0.75 | 0.65 | 1.00 | 20/20 | 0 |
| v1 base | 0.85 | 0.90 | 0.85 | 1.00 | 20/20 | 0 |
| v2 base | 0.95 | 1.00 | 0.95 | 1.00 | 20/20 | 0 |
| v3 base trước tích hợp commerce | 0.95 | 1.00 | 0.95 | 1.00 | 20/20 | 0 |
| v3 group sau tích hợp commerce | 0.80 | 1.00 | 0.80 | 0.80 | 10/10 | 0 |

Cả năm run thỏa quy tắc hợp lệ của rubric. Hash v0–v3 trong CSV khớp run và truy được về Git khi tính đúng CRLF; không coi khác line ending là bằng chứng sai version. Base và extension không bị sửa nội dung so với commit starter `c68da4c`.

Artifact của v3 base là `v3+p42c5404836b3+t713d6c7f21e0`; group là `v3+pac89e3c12b62+tbbfd57e1b138`. Run group khớp hash artifacts hiện tại. Do khác cả prompt và tools, không dùng kết quả v3 base cũ như bằng chứng base regression của bản commerce hiện tại. Có thể bổ sung nhãn v4-integrated và một dòng version_log/run base mới; không sửa hash hoặc metric của run cũ.

### 4.2. Hai phân tích sai trong B3 cần sửa

| Case | Báo cáo đang ghi | Log thực tế | Cách diễn giải đúng |
|---|---|---|---|
| G02_boundary_send_guardrail | Model trả lời thẳng, không kích hoạt clarify | Model gọi clarify, response_type=text, hỏi nội dung cụ thể | Routing đúng; lỗi args so với expect yes_no. Có mơ hồ vì user chưa cung cấp nội dung bản tin |
| G09_multiturn_timeframe_correction | Model giữ timeframe cũ | timeframe=year đúng; query="Tesla electric vehicles" khác expect="Tesla" | Lỗi chuỗi query; không phải lỗi carry-over timeframe |

Với G09, TV3 cần quyết định convention query có thật sự bắt buộc đúng chuỗi Tesla hay chỉ cần đúng chủ đề. Nếu điều chỉnh eval của nhóm vì thiết kế quá cứng, phải nêu lý do, giữ run cũ và chạy run mới, không sửa log để biến FAIL thành PASS.

G06 đang cho user “xác nhận bản tóm tắt này” nhưng không đưa nội dung tóm tắt vào context. Expect send(confirmed=true) chưa chứng minh được xác nhận đúng nội dung. Nên cung cấp nội dung cụ thể trong các lượt và chấm text/confirmed phù hợp. Đây là thay đổi thiết kế eval, không phải yêu cầu sửa case base.

### 4.3. PASS routing không đồng nghĩa tool chạy thành công

Trong group run:

- LINH_S01_profile_read và LINH_M01_fill_address PASS routing nhưng tool output là session_required.
- G06_multiturn_send_confirmed PASS routing nhưng tool output là RuntimeError do thiếu cấu hình Telegram.

Các run này vẫn hợp lệ theo định nghĩa provider_error của rubric. Báo cáo phải ghi rõ chúng đo model chọn tool/args, không dùng chúng chứng minh CRUD thành công hoặc Telegram đã gửi thật. Runner multi-turn chỉ đưa lịch sử làm ngữ cảnh cho lượt cuối, không thực thi cả hội thoại theo từng lượt.

## 5. Transcript và C6

Ba transcript hiện có đều ghi version v0, prompt hash `f0c107a9d7a1...`, tools hash `41a2894f8ad1...`. Hai hash này khớp nội dung starter tại `c68da4c` dạng LF, không phải prompt/tool tối ưu hiện tại.

| Transcript | Nội dung | Chất lượng bằng chứng |
|---|---|---|
| `v0_openrouter_20261110T194218519857.transcript.json` | Yêu cầu gửi Telegram | Model gọi send khi chưa confirmed; backend trả needs_confirmation, sau đó assistant hỏi bằng text. Chưa có lượt user xác nhận rồi gửi thành công |
| `v0_openrouter_20261110T194218520239.transcript.json` | Yêu cầu bài mới trên X; sau đó bổ sung @OpenAI, limit=2 | Có 2 lượt, nhưng lượt đầu tự đoán sama; cả hai call timeline lỗi thiếu RAPIDAPI_KEY. Không phải ví dụ tốt cho “agent hỏi rồi user bổ sung” |
| `v0_openrouter_20261110T194218520399.transcript.json` | Tìm 2 paper arXiv rồi format | Tool có dữ liệu thật và trả lời có nguồn; dùng được làm bằng chứng research, nhưng phải ghi đúng artifact starter |

Không có đủ bằng chứng luồng hỏi lại đúng trên bản cuối hoặc nút UI confirmation. Cần chạy lại theo kịch bản thật sau tích hợp: research thành công; thiếu dữ liệu → clarify → bổ sung; yêu cầu gửi/đăng → hỏi xác nhận → user trả lời. Gửi Telegram thật chỉ cần nếu nhóm theo bonus; phần bắt buộc cần chứng minh boundary và ghi trung thực nếu demo chặn gửi.

Không sửa hoặc đổi nhãn các transcript starter thành v3; tạo transcript mới, có hash đúng và thông tin model/provider.

## 6. Đánh giá báo cáo nhóm và cá nhân

### Báo cáo nhóm

[group_report.md](../report/team/group_report.md) **chưa đầy đủ**:

- A1 vẫn là lời hướng dẫn và ví dụ, chưa có mô tả sản phẩm chính thức, lệnh chạy cụ thể và link dùng thử.
- A2 chỉ có clarify và hai dòng trống, chưa liệt kê 16 tool.
- A3 chưa có 3–5 câu hỏi mẫu.
- Mục 3 Giải pháp trống.
- B1/B2 có bằng chứng khá đầy đủ; B3 có log nhưng sai diễn giải G02/G09 và chưa phân biệt tool error với model PASS.
- B4 trống dù có transcript trong repo.
- B5a trống dù code/tool/test đã có. Nên dẫn tới báo cáo test của TV2, output pytest và UI code; mô tả rõ giới hạn chat AI so với form trực tiếp.
- Mục 5 Khó khăn và mục 8 Nguồn trống. Có vấn đề thực tế để ghi: thiếu key, session_required, query convention, R12 và Windows sandbox.
- B6 có phân tích trung thực, nên giữ; cập nhật nhận xét về group sau khi đã có kết quả.
- B5/B7 là bonus: không làm thì ghi rõ Không thực hiện thay vì để bảng template dễ nhầm với thiếu phần bắt buộc.

### Cá nhân

| Thành viên | Mức đầy đủ hiện tại | Bổ sung / chỉnh sửa |
|---|---|---|
| Võ Hồng Lương — TV1 | Khá đầy đủ: scope, version/hypothesis, log, commit, AI và verification | Sửa dòng Markdown thiếu backtick; cập nhật kết quả tích hợp cuối và giới hạn wrapper. Tránh khẳng định mọi trường lạ đều trả unsupported_fields vì request_id hiện gây TypeError |
| Chu Quang Linh — TV2 | Đầy đủ hơn về phạm vi, checklist, bằng chứng, AI, test và hạn chế | Chốt email/GitHub trong TEAM; giữ kết quả test gắn đúng commit/ngày. Không tính thay đổi TV1/UI thành đóng góp TV2. Báo cáo mới chưa nằm trên main |
| Hồ Anh Tú — TV3 | Có nội dung chính và run group nhưng cần sửa tính chính xác | Tiêu đề còn HoAnhTu-[MSSV]; claim phủ paper_text, thiếu URL/từ khóa chưa khớp 10 case hiện tại; nêu rõ tên công cụ AI; thay “commit cá nhân liên quan” bằng hash thực. Sửa B3, ghi session_required/Telegram error, cân nhắc lại claim hoàn thành 100% |
| Nguyễn Minh Quân — TV4 | Có commit kỹ thuật dbd5b70 nhưng chưa có báo cáo cá nhân | Tạo `report/team/2A202603794_NguyenMinhQuan.md`, nêu app, dependency, transcript, cách dùng AI/verification, giới hạn AI chat/CRUD form và demo chặn send; dẫn code và commit thật |

Không viết thay trải nghiệm cá nhân chưa được xác nhận hoặc tạo commit/transcript giả để hoàn thiện C8.

## 7. Bonus: chưa đủ điều kiện ghi nhận mục nào

| Bonus | Điểm tối đa | Hiện trạng | Cần thêm |
|---|---:|---|---|
| ≥4 tool mới | 3 | Có 6 tool và test; eval mới route 2 tool: get_my_profile, update_profile | Đưa ít nhất 4 tool mới vào eval có route và run bằng chứng; nếu nhận cho cả 6 thì phủ cả 6. Vẫn giữ tổng 10 case, 5 single + 5 multi |
| Telegram thật | 2 | Không có status sent trên Telegram thật; UI chủ động block | Thực hiện luồng xác nhận thật trên private channel và có transcript, chỉ khi nhóm chọn bonus |
| Test challenge | 1 | 17 skipped, chưa có regression test bug tool cũ được ghi B5 | Có thể sửa bug send nhận chuỗi false, giữ regression test bắt lỗi và ghi B5; không bắt buộc hoàn thiện mọi stub nếu đi theo nhánh regression |
| Local model | 4 | Chưa có hai model local, hai vòng tối ưu hoặc bảng so sánh | Làm đủ yêu cầu Step 7 nếu có thời gian; ưu tiên phần bắt buộc trước |

Không cộng bonus vào điểm chính và không ghi đã đạt bonus chỉ vì đủ số lượng tool.

## 8. Rủi ro nhánh nộp

TEAM.md khai báo nhánh nộp `main`, nhưng main `73e83be` chưa có:

- `starter_v0/app.py` và dependency Streamlit;
- ba transcript từ commit UI;
- bản báo cáo cá nhân TV2 hoàn thiện, cập nhật TEAM và bằng chứng TV2-12 mới.

Các file này đang có trên tv2-linh. Commit local `04c3dc0` ghép main vào tv2-linh, **không có nghĩa main đã nhận code từ tv2-linh**. Trước chốt bài cần PR/merge chiều ngược lại vào nhánh nộp rồi ghi commit chốt trong TEAM. Không force-push hoặc sửa lịch sử.

TEAM còn để trống tên nhóm dù group report ghi A85, lớp còn L3A / L3B, email/GitHub Linh chưa chốt và commit nộp trống. Bổ sung thông tin thật, không suy đoán.

## 9. Thứ tự hoàn thiện để hướng tới mức tối đa

| Ưu tiên | Việc cụ thể | Người chính | Bằng chứng đóng việc |
|---|---|---|---|
| P0 | Chốt nhánh nộp, merge UI/báo cáo TV2 vào main | TV1 | app.py và đủ báo cáo trong commit chốt trên main |
| P0 | Hoàn thiện Phần A, mục 3, B4, B5a, khó khăn và nguồn của group report | TV4 + TV3, TV1/TV2 cung cấp dữ liệu | Mọi mục bắt buộc có nội dung và đường dẫn thật; link UI dùng được |
| P0 | Bổ sung báo cáo TV4 và hoàn tất TEAM | TV4 + TV1; Linh chốt liên hệ | Đủ 4 báo cáo đúng MSSV, đủ đóng góp/commit/AI verification |
| P0 | Nối chat AI với demoSession và pending action/nút UI; thêm lưu transcript UI | TV4 + TV1 | Test offline + live chat mới chứng minh chat gọi commerce chạy được và không ghi trước phê duyệt |
| P0 | Sửa send chỉ chấp nhận boolean True; từ chối chuỗi false/true và input sai | Chủ sở hữu tool / TV1, TV2 hỗ trợ test | Regression test mocked HTTP: sai kiểu → không HTTP, đúng True → gửi theo điều kiện |
| P1 | Sửa wrapper place_order không raise khi có request_id thừa | TV1 | Test extra field trả error dict, không tạo đơn; giữ request_id của pending khi phê duyệt |
| P1 | Sửa phân tích G02/G09; làm rõ G06 và các output session_required | TV3 | B3 khớp failures/actual_tool_calls/tool_results, không sửa run cũ |
| P1 | Ghi live transcript mới trên artifact cuối với đủ ba tình huống | TV4 | Có hỏi lại thật, có user bổ sung, có boundary gửi; B4 dẫn đúng file |
| P1 | Ghi phiên bản tích hợp mới và base regression sau thêm 6 tool | TV1 | Run hợp lệ, version_log/README report khớp hash |
| P2 | Phủ ≥4 tool mới trong eval; ghi bonus đúng bằng chứng | TV3 + TV2 | Bộ 10 case vẫn 5/5; route ≥4 tool mới và có run |
| P2 | Local model / Telegram thật / mở rộng test challenge | Theo thời gian và lựa chọn nhóm | Chỉ nhận bonus khi đủ evidence tương ứng |

Không cần làm poster hoặc local model để đáp ứng 100 điểm chính. Không cần đạt 100% eval để chứng minh đã làm đủ phương pháp. Không được hồi tố thời gian hoàn thành Phần A nếu đã lỡ mốc showdown.

## 10. Tái chạy kiểm tra audit trên máy hiện tại

Từ `starter_v0/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe ..\outputs\audit_20261111\ui_probe.py
.\.venv\Scripts\python.exe ..\outputs\audit_20261111\negative_probe.py
```

UI probe cần Streamlit; đã cài Streamlit/OpenAI SDK vào .venv để kiểm tra, không thêm dependency mới vào requirements vì repo đã khai báo chúng. Probe chặn kết nối ngoài loopback và dùng fake provider/HTTP mock. Các file outputs là công cụ audit cục bộ, chưa là deliverable nộp bài. Report này là kết quả rà soát, không thay thế việc coach chấm điểm.
