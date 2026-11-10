# Team

## Thông tin nhóm

- Tên nhóm: A85
- Lớp: K5-L3B
- Repo nhóm: `K5-L3B-DAY03-A85-ResearchAgentToolEval`
- URL repo: https://github.com/ArsNeonci/K5-L3B-DAY03-A85-ResearchAgentToolEval
- Nhánh nộp: main. Bản chốt: Git tag `submission-final-20261111` (tra mã commit bằng `git rev-parse submission-final-20261111`).

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Võ Hồng Lương| 2A202603839| 26ai.luongvh@vinuni.edu.vn| luongvh2510 | Prompt, phiên bản và tích hợp |
|   2 | Chu Quang Linh | 2A202603809 | quanglinh1286@gmail.com (Git author) | ArsNeonci (Git author/repo) | TV2 — SQLite demo tools, unit test và bàn giao tích hợp |
|   3 | Hồ Anh Tú | 2A202603811 | 26ai.tuha2@vinuni.edu.vn | TuHoAnh | Eval nhóm, phân tích log và báo cáo |
|   4 | Nguyễn Minh Quân | 2A202603794 | 26ai.quannm10@vinuni.edu.vn | nmqdhtb | UI Streamlit, demo và transcript |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## Võ Hồng Lương — 2A202603839

### Phần việc phụ trách

- TV1 — provider setup, baseline, prompt/declaration, version log và tích hợp registry.

### Đóng góp và bằng chứng

- Các vòng v1–v3 có giả thuyết, run JSON và bảng phân tích; tích hợp sáu tool TV2 qua commit `3f23e69` và PR #1.
- [Báo cáo cá nhân](report/team/2A202603839_VoHongLuong.md), [version log](starter_v0/artifacts/version_log.csv), [ghi chú tích hợp](docs/TV1_INTEGRATION_NOTES.md).
- Công cụ AI được TV1 khai báo: Claude Code. Các chỉnh sửa bổ sung của đợt hoàn thiện dùng Codex được ghi riêng.

## Chu Quang Linh — 2A202603809

### Phần việc phụ trách

- Đặc tả, triển khai và kiểm thử sáu tool hồ sơ/đơn hàng trên SQLite với dữ liệu giả.
- Chuẩn bị TOOL.md, schema fragment, console demo và hướng dẫn cho TV1/TV3/TV4 tích hợp.

### Đóng góp cụ thể

- Sáu tool: get_my_profile, update_profile, preview_order, place_order, get_order_status, cancel_order; backend chung trong `starter_v0/commerce_demo/`.
- 30 test riêng cho tool mới; kiểm tra sau tích hợp: contract 85 passed, toàn suite 122 passed, 17 skipped, 0 failed.
- Hoàn thành bàn giao TV2-11/13 và kiểm tra TV2-12; báo cáo cá nhân TV2-14 có đối chiếu checklist, công cụ AI đã dùng và giới hạn xác nhận.
- Registry, prompt/YAML chung, eval và UI do các thành viên phụ trách tương ứng; không tính thay đổi tích hợp của TV1 thành code riêng của TV2.

### Bằng chứng

- Nhánh: `tv2-linh`; commit code ban đầu `4d6cfb4`, commit bằng chứng kiểm tra sau tích hợp `5ccabb6`.
- [Báo cáo cá nhân](report/team/2A202603809_ChuQuangLinh.md).
- [Báo cáo kiểm tra tool](report/team/TV2_LINH_TOOL_TESTS.md).
- [Tài liệu bàn giao](docs/TV2_LINH_HANDOFF.md).

## Hồ Anh Tú — 2A202603811

### Phần việc phụ trách

- TV3 — Thiết kế eval nhóm, phân tích run JSON và tổng hợp bằng chứng báo cáo.

### Đóng góp cụ thể

- Bộ eval nhóm 10 case, đúng 5 single turn và 5 multi turn; có case cho tool mới của TV2.
- Bổ sung run group và nội dung B2/B3 của báo cáo nhóm. Run group ghi 8/10 PASS, routing 100%; kết quả này đo tool call/arguments, không chứng minh mọi tool thực thi thành công.

### Bằng chứng

- Commit `73e83be`: cập nhật eval nhóm và báo cáo.
- [Báo cáo cá nhân](report/team/2A202603811_HoAnhTu.md).
- [Eval nhóm](starter_v0/data/eval_group.json).
- [Run group](starter_v0/runs/v3_B_group_openrouter_20261111T000148799392.json).

## Nguyễn Minh Quân — 2A202603794

### Phần việc phụ trách

- TV4 — UI Streamlit, demo và transcript.

### Đóng góp cụ thể

- UI chat nghiên cứu với lịch sử trong phiên, hiển thị tool calls/kết quả và lỗi.
- Form chạy trực tiếp tool hồ sơ/đơn hàng SQLite, có nút đồng ý/từ chối thao tác ghi.
- Dependency Streamlit và ba transcript demo. Chưa coi đây là bằng chứng UI chat commerce hoặc transcript bản tối ưu cuối đã hoàn thiện.
- Công cụ AI hỗ trợ: Codex.

### Bằng chứng

- Commit kỹ thuật `dbd5b70`.
- [Báo cáo cá nhân](report/team/2A202603794_NguyenMinhQuan.md).
- [UI](starter_v0/app.py), [dependency](starter_v0/requirements.txt), [transcript](starter_v0/transcripts/).

## Bổ sung bản hoàn thiện ngày 11/11/2026

- Theo ủy quyền của người dùng, Codex hỗ trợ sửa guardrail send, wrapper retry, nối chat/session/approval, lưu transcript và hoàn thiện test/report. Không gán các thay đổi bổ sung này thành trải nghiệm tự viết thủ công của thành viên khác.
- Kết quả: 155 passed + 16 subtests, 0 skipped; v7-final live base 20/20 và group 10/10. Group có điều chỉnh expectation G09 đúng mục tiêu timeframe, giữ bản strict và log cũ.
- [Báo cáo nhóm](report/team/group_report.md), [runbook](docs/FINAL_RUNBOOK.md), [manifest evidence](starter_v0/analysis/submission_evidence.json).
- UI chỉ localhost theo lựa chọn người dùng; không tự khai đã nộp LMS, có public deployment hoặc hoàn thành Phần A trước showdown.
