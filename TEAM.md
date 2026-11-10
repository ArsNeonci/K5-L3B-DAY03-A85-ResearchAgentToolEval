# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A / L3B
- Repo nhóm: `K5-L3B-DAY03-A85-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/ArsNeonci/K5-L3B-DAY03-A85-ResearchAgentToolEval, main,

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Võ Hồng Lương| 2A202603839| 26ai.luongvh@vinuni.edu.vn| luongvh2510 | Prompt, phiên bản và tích hợp |
|   2 | Chu Quang Linh | 2A202603809 | Chưa cung cấp | Chưa xác nhận tài khoản cá nhân | TV2 — SQLite demo tools, unit test và bàn giao tích hợp |
|   3 | Hồ Anh Tú | 2A202603811 | 26ai.tuha2@vinuni.edu.vn | TuHoAnh | Eval nhóm, phân tích log và báo cáo |
|   4 | Nguyễn Minh Quân | 2A202603794 | 26ai.quannm10@vinuni.edu.vn | nmqdhtb | UI Streamlit, demo và transcript |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

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
