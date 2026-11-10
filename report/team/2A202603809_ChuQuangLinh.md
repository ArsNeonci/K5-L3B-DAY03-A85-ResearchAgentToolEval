# Báo cáo cá nhân — Chu Quang Linh

## 1. Thông tin thành viên

- Họ tên: Chu Quang Linh.
- MSSV: 2A202603809.
- Email: Linh bổ sung nếu cần.

## 2. Phần việc phụ trách

TV2: đặc tả và triển khai 6 tool demo hồ sơ/đơn hàng, backend SQLite, TOOL.md, schema bàn giao và test trực tiếp từng tool. Đã hoàn tất kiểm tra contract và toàn suite sau khi lấy bản đăng ký tool của TV1; chưa kiểm tra AI/eval hoặc UI chung trong đợt này.

## 3. Đóng góp kỹ thuật trong nhánh tv2-linh

- Chọn scope và điền mục 1–8 của `docs/TV2_MAU_QUYET_DINH_TOOL.md`.
- Code mới trong `starter_v0/commerce_demo/` và sáu thư mục tool tương ứng.
- Chuẩn bị `starter_v0/artifacts/tools_tv2.fragment.json` để TV1 đăng ký.
- Có 30 auto test offline và console smoke demo qua cả 6 tool.
- Hoàn tất mục TV2-12 trên bản tích hợp `c04f5da`: contract 85 passed; toàn suite 122 passed, 17 skipped, 0 failed. Test tool mới không skipped; các skipped còn lại là stub tool cũ.
- Bàn giao `docs/TV2_LINH_HANDOFF.md` cho các thành viên tiếp tục tích hợp.

## 4. Bằng chứng và công cụ

- Nhánh: `tv2-linh`.
- Kết quả kiểm tra thực tế: `report/team/TV2_LINH_TOOL_TESTS.md`.
- Công cụ hỗ trợ: Codex hỗ trợ triển khai, viết tài liệu và chạy kiểm tra. Không gọi model/AI bên trong các tool hoặc trong lần kiểm tra này.
- Linh tự kiểm tra: chạy `python scripts/demo_tv2_tools.py`, đọc output và nhập xác nhận theo hướng dẫn; bổ sung nhận xét thực tế sau khi tự thực hiện.

## 5. Tự đánh giá

Linh tự điền sau khi đọc code và chạy thử. Chưa ghi thay kết quả tự đánh giá hoặc xác nhận rằng Linh đã kiểm tra thủ công.
