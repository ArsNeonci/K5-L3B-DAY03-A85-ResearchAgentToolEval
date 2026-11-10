# Chạy và kiểm tra bản hoàn thiện A85

## Dùng ngay trên máy hiện tại

UI: **http://127.0.0.1:8502**. Dịch vụ chỉ bind localhost theo lựa chọn của người dùng; không có tunnel public.

Hai khu vực: **Chat nghiên cứu** dùng provider thật; **Hồ sơ & đơn hàng** chạy trực tiếp sáu tool SQLite giả. Khi chat chuẩn bị cập nhật/tạo/hủy, kiểm tra nội dung rồi bấm Đồng ý thực hiện hoặc Từ chối. Khóa xác nhận không xuất hiện trong prompt/transcript.

## Một lệnh kiểm tra toàn bộ offline

Từ `starter_v0/`:

```powershell
.\.venv\Scripts\python.exe scripts/final_check.py
```

Kết quả đã chạy: 155 passed, 16 subtests passed; 0 failed, 0 skipped. Có contract test, unit test tool cũ/mới, regression send, wrapper retry, UI approval, CLI và transcript. JUnit đếm 171 gồm subtests, không phải 171 hàm test độc lập.

## Một lệnh kiểm tra và eval thật

```powershell
.\.venv\Scripts\python.exe scripts/final_check.py --live
```

Lệnh chạy pytest, kiểm tra dataset/report, preflight provider, rồi base và group eval bằng model thật. Có dùng hạn mức API. Output nằm ở `analysis/final_check.json`, `analysis/pytest_final.xml`, `runs/*.json`. Mặc định không gửi Telegram thật. Điểm agent có thể dao động ở lần khác; không bảo đảm mọi lần đều đạt cùng tỷ lệ.

Kết quả live đã có của v7-final: **20/20 base**, **10/10 group**, provider errors=0. Group cuối có sửa đúng phạm vi expectation G09 (topic/timeframe thay vì chuỗi query đồng nghĩa); bản strict và log 9/10 vẫn được lưu. Không sửa base/extension gốc hoặc scorer để tăng điểm.

## Setup khi clone sang máy khác

```powershell
cd starter_v0
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Điền key trong `.env` (không commit), hoặc dùng file `.env` ở gốc repo. File `starter_v0/.env` override file gốc; `DAY03_ENV_FILE` override cả hai.

- `OPENROUTER_API_KEY`: cần cho chat/eval thật; hiện đã cấu hình trên máy này.
- `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY`: cần nếu muốn lookup/fetch/X trả kết quả thật. Hiện chưa có ba key này; các tool trả lỗi cấu hình có thông báo, không giả dữ liệu.
- Policy và SQLite chạy local. Papers/paper_text dùng API/PDF arXiv công khai và cần mạng.
- Telegram token/chat ID chỉ cần nếu nhóm chủ động làm bonus gửi thật. UI demo và eval mặc định chặn gửi; mock/test PASS không được coi là gửi thật.

Khởi động UI:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1 --server.headless true
```

Chat console có session SQLite và xác nhận YES cho action commerce:

```powershell
.\.venv\Scripts\python.exe chat.py --provider openrouter --version v7-final
```

Ghi lại ba kịch bản UI với model thật, input script hóa (không phải người kiểm thử thủ công):

```powershell
.\.venv\Scripts\python.exe scripts/record_live_demo.py
```

## Evidence và nộp bài

- [Báo cáo nhóm](../report/team/group_report.md): tất cả mục bắt buộc đã có nội dung và dẫn chứng.
- [TEAM](../TEAM.md): bốn thành viên và phạm vi đóng góp; báo cáo từng người ở report/team/.
- `analysis/submission_evidence.json`: run cuối, transcript thật và kiểm tra offline.
- `artifacts/version_log.csv`: v0–v3 và các vòng hoàn thiện, gồm cả lần FAIL.
- `data/history/`: bộ group cũ/strict để giải thích thay đổi thiết kế; không sửa run cũ.
- `artifacts/history/`: snapshot prompt/tool theo version.
- Chạy `python scripts/build_evidence_report.py` để dựng lại bảng số liệu từ các file evidence hiện có.

Không tự nhận đạt 100 điểm rubric: còn phụ thuộc đánh giá của coach, mốc nộp và yêu cầu link public. Phần A được hoàn thiện sau showdown, không sửa ngày để giả đạt hạn. Bonus đã có bằng chứng cho ≥4 tool mới và Test challenge; không thực hiện local model hoặc Telegram thật.

Không có thao tác nộp LMS tự động; từng thành viên nộp link repo bằng tài khoản cá nhân. Chỉ dùng localhost là quyết định rõ ràng của người dùng, không trình bày là link người ngoài nhóm có thể mở.
