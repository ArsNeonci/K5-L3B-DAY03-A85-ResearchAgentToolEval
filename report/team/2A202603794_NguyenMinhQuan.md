# Báo cáo cá nhân — Nguyễn Minh Quân — 2A202603794

**Trạng thái cuối:** các khoảng trống mô tả ở mục 5 là ghi nhận trước đợt hoàn thiện. Chat đã được nối session/approval, UI đã lưu transcript, có live transcript v7 và test integration. Xem mục 6 và báo cáo nhóm cho kết quả cuối; không suy diễn thành Quân đã tự kiểm tra thủ công hoặc có link public.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Minh Quân.
- MSSV: 2A202603794.
- Vai trò: TV4 — UI Streamlit, demo và transcript.
- Email theo TEAM.md: 26ai.quannm10@vinuni.edu.vn.
- GitHub theo TEAM.md: nmqdhtb.
- Ngày cập nhật báo cáo: 11/11/2026 (giờ Việt Nam).

## 2. Phần việc phụ trách

Xây dựng UI để người dùng thử research agent, xem lịch sử hội thoại và các lần gọi tool; cung cấp khu vực thao tác trực tiếp với tool hồ sơ/đơn hàng của TV2. Chuẩn bị dependency UI và các transcript phục vụ demo, bàn giao bằng chứng cho báo cáo nhóm.

Phạm vi code UI khác với backend tool: TV2 triển khai SQLite và sáu tool; TV1 đăng ký tool và viết declaration/prompt; TV4 nối các thành phần vào giao diện. Các kết quả eval model do TV1/TV3 thực hiện không được tính thành kết quả kiểm thử UI của TV4.

## 3. Đóng góp cụ thể

### 3.1. Giao diện chat nghiên cứu

- Tạo [app.py](../../starter_v0/app.py) bằng Streamlit, có chat input, các ví dụ để thử và nút tạo phiên chat mới.
- Nạp prompt, tool declarations và provider từ cấu hình; dùng DAY03_PROVIDER, DAY03_MODEL nếu được thiết lập.
- Lưu lịch sử hội thoại trong session_state, giới hạn cửa sổ ngữ cảnh và số vòng gọi tool.
- Hiển thị tool name, arguments và result trong các mục mở rộng; phân biệt lỗi, chờ người dùng và câu trả lời.
- Hiển thị lỗi provider và thông báo khi đạt giới hạn vòng gọi, tránh để lỗi làm mất toàn bộ giao diện.
- Có hàm che các giá trị credential lấy từ biến môi trường khi hiển thị dữ liệu chat/tool.
- Chặn gửi Telegram đã confirmed trong UI demo bằng kết quả blocked_in_demo; không trình bày UI này là bằng chứng đã gửi thật.

### 3.2. Khu vực Hồ sơ & đơn hàng

- Thêm khu vực form để chạy trực tiếp sáu tool do TV2 bàn giao: đọc/sửa hồ sơ, xem trước/tạo/xem/hủy đơn.
- Khởi tạo SQLite giả riêng cho phiên trình duyệt và mở demoSession khi gọi tool từ form.
- Hiển thị pending_action trước khi người dùng chọn Đồng ý thực hiện hoặc Từ chối.
- Khi đồng ý, host cấp khóa xác nhận và thực thi action trong cùng context. Không truyền khóa cho model hoặc hiển thị khóa trong kết quả.
- Khi từ chối, dừng thao tác ghi; dùng mã preview/order trả về để hỗ trợ các form tiếp theo.

Đây là luồng form trực tiếp, chưa phải bằng chứng chat AI tự gọi tool commerce thành công. Luồng chat và form dùng các đường thực thi khác nhau; giới hạn này được ghi ở mục 5.

### 3.3. Dependency và transcript

- Thêm Streamlit vào [requirements.txt](../../starter_v0/requirements.txt).
- Commit UI có ba transcript, tổng bốn lượt chat, minh họa yêu cầu gửi Telegram, thiếu tài khoản X rồi bổ sung và tìm paper arXiv.
- Các transcript mang version/hash của starter v0. Chúng giữ nguyên bằng chứng thực tế, không được đổi nhãn thành bản tối ưu cuối.

Lệnh chạy từ `starter_v0/` sau khi cài dependency:

```powershell
python -m streamlit run app.py
```

Chưa có link deploy/public đã được xác nhận trong báo cáo nhóm tại thời điểm cập nhật; không tạo hoặc điền URL giả.

## 4. Bằng chứng, công cụ AI và cách kiểm tra

### 4.1. Code, commit và transcript

| Đầu ra | Bằng chứng |
|---|---|
| UI nghiên cứu và form commerce | [app.py](../../starter_v0/app.py) |
| Dependency | [requirements.txt](../../starter_v0/requirements.txt) |
| Commit kỹ thuật TV4 | [dbd5b70 — commit ui](https://github.com/ArsNeonci/K5-L3B-DAY03-A85-ResearchAgentToolEval/commit/dbd5b70) |
| Tình huống yêu cầu gửi | [v0_openrouter_20261110T194218519857.transcript.json](../../starter_v0/transcripts/v0_openrouter_20261110T194218519857.transcript.json) |
| Tình huống thiếu tài khoản X rồi bổ sung | [v0_openrouter_20261110T194218520239.transcript.json](../../starter_v0/transcripts/v0_openrouter_20261110T194218520239.transcript.json) |
| Tìm paper và định dạng kết quả | [v0_openrouter_20261110T194218520399.transcript.json](../../starter_v0/transcripts/v0_openrouter_20261110T194218520399.transcript.json) |
| Rà soát kỹ thuật sau tích hợp | [REVIEW_RUBRIC_20261111.md](../../docs/REVIEW_RUBRIC_20261111.md) |

### 4.2. Công cụ AI đã sử dụng

Sử dụng **Codex** để hỗ trợ thực hiện phần UI. Tên công cụ được xác nhận khi bổ sung thông tin báo cáo. Không mô tả toàn bộ code là tự viết thủ công hoặc nhận mọi kết quả do AI đề xuất mà không kiểm tra.

Cách kiểm chứng đã có bằng chứng trong lần rà soát kỹ thuật của dự án ngày 11/11/2026:

- Chạy toàn suite offline: 122 passed, 17 skipped, 0 failed. Đây là kết quả suite của dự án; không coi toàn bộ test là do TV4 viết.
- Chạy Streamlit AppTest trên dữ liệu SQLite giả: giao diện khởi động, đọc hồ sơ, chuẩn bị thay đổi, từ chối không ghi, đồng ý mới ghi, preview đúng tổng 60.000 VND, tạo đơn pending, đọc trạng thái, hủy và đọc lại cancelled.
- Dùng fake provider và chặn mạng ngoài loopback để kiểm tra luồng chat; phát hiện lỗi session_required khi chat gọi tool TV2 và việc UI chưa lưu transcript xuống đĩa.
- Đọc output thực tế thay vì chỉ quan sát giao diện hoặc coi không có exception là đã hoàn thiện cả luồng.

Những kiểm tra trên được thực hiện qua công cụ trong đợt rà soát, không phải lời xác nhận Quân đã tự thao tác thủ công toàn bộ kịch bản. Chưa có thông tin để khẳng định người ngoài nhóm đã mở và dùng thành công link deploy.

## 5. Đánh giá mức hoàn thành và giới hạn

Phần UI đã có code và commit kỹ thuật, chạy được khu vực form commerce với cơ chế phê duyệt. UI chat hiển thị công cụ và lỗi, hỗ trợ lịch sử trong phiên, có dependency và transcript demo trong repo.

Các điểm chưa đủ bằng chứng để ghi nhận hoàn thành toàn bộ TV4/C6:

1. Chat AI gọi tool TV2 qua execute_tool_call nhưng chưa mở demoSession; form trực tiếp có mở session. Cần nối luồng chat với session và pending action/nút phê duyệt.
2. UI lưu lịch sử trong session_state, chưa ghi transcript JSON mới xuống đĩa; cần bổ sung cơ chế lưu kèm hash/version.
3. Transcript hiện tại dùng starter: tình huống X tự đoán sama rồi lỗi thiếu RAPIDAPI_KEY; chưa chứng minh agent hỏi lại đúng trên bản cuối. Cần chạy live chat mới với đủ ba tình huống của lab.
4. UI cố ý chặn gửi Telegram thật. Chưa có bằng chứng cho bonus Telegram; không coi HTTP mock hoặc blocked_in_demo là gửi thành công.
5. Phần A và B4/B5a của báo cáo nhóm còn cần cập nhật lệnh chạy, link thật, câu hỏi mẫu và dẫn chứng tương ứng.

Ưu tiên tiếp theo là hoàn thiện kết nối chat với backend, lưu transcript và kiểm thử trên artifact cuối trước khi công bố UI đã hoàn thành. Không tự gán mức hoàn thành 100% hoặc mô tả trải nghiệm cá nhân chưa được xác nhận.

## 6. Kết quả bổ sung bằng Codex trong đợt hoàn thiện

- `run_turn` mở demoSession; pending action từ chat được hiển thị qua nút Đồng ý/Từ chối, gọi hàm gốc trong cùng session khi cấp key.
- UI ghi transcript JSON có prompt_hash/tools_hash, status, rounds, tool_events; che credential và không ghi confirmation_key.
- Form và chat dùng cùng quy ước request_id ổn định theo preview. Test thật qua AppTest chứng minh từ chối không sửa, đồng ý mới sửa, tạo/xem/hủy đơn đúng.
- Transcript UI mới dùng OpenRouter thật và bản v7. Input/nhấn nút được script hóa để tái lập, không gán thành thao tác thủ công của Quân. [Manifest bằng chứng](../../starter_v0/analysis/submission_evidence.json) và [B4 báo cáo nhóm](group_report.md) dẫn từng file.
- UI localhost: http://127.0.0.1:8502. Người dùng đã chọn không mở public; không có claim triển khai public hoặc bonus Telegram thật.
- Toàn suite sau bổ sung: 155 passed +16 subtests, 0 failed, 0 skipped. Code/backend gốc của TV2 và phần tích hợp ban đầu của TV1 được ghi riêng theo lịch sử; các sửa bổ sung được hỗ trợ bằng Codex.
