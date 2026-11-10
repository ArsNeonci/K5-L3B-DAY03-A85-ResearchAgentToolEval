# Kết quả kiểm tra riêng tool — TV2 Linh

Ngày ghi nhận: 10/11/2026 (giờ Việt Nam). Nhánh bàn giao: `tv2-linh`.

## Phạm vi

Chỉ kiểm tra trực tiếp 6 tool của Linh và backend SQLite mới. Không dùng model, provider, API hoặc mạng. Chưa chạy full pytest, contract test chung, eval base/group hoặc UI chung, theo yêu cầu bàn giao giai đoạn này.

## Auto test

Từ `starter_v0/`:

```powershell
python -m unittest discover -s tests -p test_tv2_tools.py -v
```

Kết quả thực tế sau lần sửa cuối về thông báo hỏi lại (chạy cùng lệnh với `-q` thay `-v`):

```text
Ran 30 tests in 1.707s
OK
```

| Tool | Các hành vi đã kiểm tra |
|---|---|
| get_my_profile | Đọc đúng hồ sơ demo, từ chối trường thừa, lỗi storage |
| update_profile | Ghi đúng trường và đúng tài khoản, từ chối input xấu, không ghi khi thiếu/sai key, rollback khi lỗi ghi |
| preview_order | Tính đúng 60.000 VND cho 2 cuốn sổ, không tạo đơn/trừ tồn, số lượng sai, thiếu trường, không có hàng, lỗi storage |
| place_order | Tạo đơn và trừ tồn, retry không tạo trùng, request conflict, thiếu xác nhận, preview hết hạn, giá/tồn đổi, rollback |
| get_order_status | Đọc đơn pending đúng tổng tiền, input sai/không tồn tại, lỗi storage |
| cancel_order | Hủy pending và hoàn tồn một lần, chặn đơn shipped, thiếu xác nhận, rollback |

Kiểm tra bổ sung: thiếu session thì cả 6 tool từ chối; tài khoản demo không tồn tại; không xem đơn tài khoản khác; key khác phiên/hết hạn; khởi tạo không ghi đè database có sẵn.

Môi trường Windows sandbox chặn truy cập thư mục do `tempfile` tạo ở lần thử đầu. Chạy lại lệnh test với quyền thực thi ngoài sandbox đã thành công; test vẫn chỉ thao tác dữ liệu giả trong `runtime/`. Không thay đổi logic tool để bỏ qua lỗi quyền.

## Console smoke demo

Lệnh để Linh tự thử tương tác:

```powershell
python scripts/demo_tv2_tools.py
```

Đã chạy hết kịch bản console bằng Python subprocess, cung cấp ba dòng `YES` qua stdin để giả lập phê duyệt; đây là smoke test tự động, chưa phải kiểm thử người dùng trên UI:

```powershell
python -c "import subprocess,sys; subprocess.run([sys.executable,'scripts/demo_tv2_tools.py'], input='YES\nYES\nYES\n', text=True, check=True)"
```

Quan sát output thực tế:

1. Hồ sơ ban đầu có địa chỉ `Địa chỉ demo A`.
2. Sau phê duyệt, update trả `updated`, đọc lại thấy `Địa chỉ demo B`.
3. Preview 2 `DEMO-NOTEBOOK` có `total_vnd=60000` và địa chỉ mới.
4. Place sau phê duyệt trả `created`, đơn có trạng thái `pending`.
5. Get status trả `pending` đúng đơn.
6. Cancel sau phê duyệt trả `cancelled`; đọc lại thấy đơn `cancelled`.

Exit code: 0. Database được tạo riêng trong thư mục tạm và dọn sau kịch bản. Không đưa khóa xác nhận vào output.

## Việc để TV1/TV3/TV4 tiếp tục

- Đăng ký registry và ghép schema fragment vào YAML.
- Mở session từ host, bổ sung nút phê duyệt và nhánh thực thi action với key.
- Viết master prompt/routing và eval case cho tool mới.
- Chạy contract/full suite và eval sau tích hợp; không suy diễn kết quả test tool thành độ chính xác của model.

Hướng dẫn chi tiết: `docs/TV2_LINH_HANDOFF.md` ở gốc repo.
