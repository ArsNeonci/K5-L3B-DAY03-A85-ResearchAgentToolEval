# Kết quả kiểm tra riêng tool — TV2 Linh

Ngày ghi nhận: 10/11/2026 (giờ Việt Nam). Nhánh bàn giao: `tv2-linh`.

## Phạm vi

Giai đoạn bàn giao ban đầu chỉ kiểm tra trực tiếp 6 tool của Linh và backend SQLite mới, không dùng model, provider, API hoặc mạng. Kết quả chạy contract test và full pytest sau tích hợp được bổ sung tại mục TV2-12 bên dưới. Chưa chạy eval base/group hoặc UI chung trong đợt kiểm tra này.

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

## TV2-12 — Contract test và toàn suite sau tích hợp: hoàn thành

Ngày ghi nhận: 10/11/2026 (giờ Việt Nam).

### Trạng thái code đã kiểm tra

- Remote không có nhánh tên đúng `tv2`; nhánh của Linh là `tv2-linh`.
- Sau `git fetch origin`, nhánh `tv2-linh` được fast-forward tới `origin/main`, commit `c04f5da` (merge phần tích hợp TV1).
- Registry/YAML đã có đủ 6 tool. Riêng `place_order` dùng wrapper tự sinh request_id; model chỉ truyền preview_id. Đây là thay đổi tích hợp của TV1, không phải sửa backend TV2 trong lần kiểm tra này.
- Không thay đổi source tool, prompt, case eval hoặc stub TODO để làm test xanh.

### Lệnh và kết quả thực tế

Chạy từ `starter_v0/`, dùng `.venv` riêng với pytest 9.2.0 và các dependency có sẵn trên máy:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_tool_contract.py -q
```

```text
85 passed in 1.11s
```

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

```text
122 passed, 17 skipped, 16 subtests passed in 2.81s
```

Exit code của cả hai lệnh: 0. Có 0 failed và 0 errors.

### Đối chiếu điều kiện hoàn thành

- [x] Contract giữa tools.yaml, registry, chữ ký hàm, TOOL.md và tên tool trong bộ eval được kiểm tra, 85 test đạt.
- [x] Toàn suite 0 failed.
- [x] 30 test mới trong `tests/test_tv2_tools.py` được pytest thu thập và chạy, không skipped; mỗi tool có ít nhất ba test gồm thành công, input không hợp lệ và lỗi storage.
- [x] Kiểm tra offline, không gọi API/model thật.
- [x] Ghi bằng chứng để TV1/TV3 cập nhật checklist và báo cáo.

17 skipped đều là stub có sẵn trong `tests/test_tools_todo.py` (các tool cũ), không phải test của 6 tool mới. README cho phép giữ các stub này skipped ở phần bắt buộc. Chưa hoàn thành bonus toàn suite 0 skipped.

Phạm vi xác nhận: contract và unit test sau tích hợp. Không suy diễn kết quả này thành bằng chứng UI phê duyệt hoặc routing của model đã chạy thành công. Mục TV2-11 và TV2-13 được người dùng xác nhận đã hoàn thành; lần này chỉ hoàn tất TV2-12.
