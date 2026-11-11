# Báo cáo cá nhân — NguyenMinhQuan-2A202603794

## 1. Thông tin thành viên

- Họ tên: Nguyễn Minh Quân
- MSSV: 2A202603794
- Email: 26ai.quannm10@vinuni.edu.vn

## 2. Phần việc phụ trách

Xây dựng giao diện Streamlit để nhóm khác dùng thử Research Agent, chuẩn bị kịch bản demo và thu bằng chứng chat trực tiếp. Cập nhật phần giới thiệu agent, hướng dẫn chạy, danh sách tool và câu hỏi mẫu trong Phần A của báo cáo nhóm.

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

- Thêm khu vực form để chạy trực tiếp sáu tool do thành viên 2 bàn giao: đọc/sửa hồ sơ, xem trước/tạo/xem/hủy đơn.
- Khởi tạo SQLite giả riêng cho phiên trình duyệt và mở demoSession khi gọi tool từ form.
- Hiển thị pending_action trước khi người dùng chọn Đồng ý thực hiện hoặc Từ chối.
- Khi đồng ý, host cấp khóa xác nhận và thực thi action trong cùng context. Không truyền khóa cho model hoặc hiển thị khóa trong kết quả.
- Khi từ chối, dừng thao tác ghi; dùng mã preview/order trả về để hỗ trợ các form tiếp theo.

Đây là luồng form trực tiếp, chưa phải bằng chứng chat AI tự gọi tool commerce thành công. Luồng chat và form dùng các đường thực thi khác nhau; giới hạn này được ghi ở mục 5.

### 3.3. Dependency và transcript

- Thêm Streamlit vào [requirements.txt](../../starter_v0/requirements.txt).
- Commit UI có ba transcript, tổng bốn lượt chat, minh họa yêu cầu gửi Telegram, thiếu tài khoản X rồi bổ sung và tìm paper arXiv.
- Các transcript mang version/hash của starter v0. Chúng giữ nguyên bằng chứng thực tế, không được đổi nhãn thành bản tối ưu cuối.

## 4. Bằng chứng

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

Codex hỗ trợ đọc tài liệu, triển khai và rà soát UI. Kết quả được đối chiếu bằng Streamlit AppTest, pytest và các lần gọi OpenRouter thật. Khi tự kiểm tra, có thể mở từng mục nhật ký tool trong UI và đối chiếu với trường `tool_events` trong transcript tương ứng.

## 5. Tự đánh giá

Em đã hoàn thành phần giao diện và chuẩn bị bằng chứng cho ba tình huống CP5 trên bản starter. Phần đã làm tốt là hiển thị tên tool, tham số và kết quả ngay dưới từng lượt chat. Nhờ đó, khi thử câu hỏi thiếu tên tài khoản X, em có thể tách hai vấn đề: agent tự đoán tài khoản ở lượt đầu, còn tool `timeline` báo lỗi vì thiếu `RAPIDAPI_KEY`. Nếu chỉ đọc câu trả lời cuối, hai vấn đề này dễ bị gộp thành một.

Điểm cần cải thiện là kiểm tra lại toàn bộ luồng trên bản tích hợp. Em sẽ ưu tiên thử tình huống thiếu thông tin để xác nhận agent hỏi tên tài khoản trước khi gọi tool, rồi lưu transcript mới. Sau đó, em sẽ nhờ một người ngoài nhóm mở link demo và tự chạy các câu mẫu để kiểm tra hướng dẫn sử dụng.
