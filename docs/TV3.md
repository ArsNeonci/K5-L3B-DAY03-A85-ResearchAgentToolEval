# Bàn giao TV3 — Bộ eval cuối A85

- TV2: Chu Quang Linh; TV3: Hồ Anh Tú, 2A202603811.
- Dataset chính: [eval_group.json](../starter_v0/data/eval_group.json).
- Đúng 10 case: 5 single + 5 multi; route đủ 6 tool mới.
- Bản đề xuất ban đầu: [history/TV3_initial.md](history/TV3_initial.md).

## Nội dung theo mẫu mục 9

| Trường | Bàn giao hiện tại |
|---|---|
| User query / turns | Mỗi case ghi đầy đủ trong dataset; giữ ID duy nhất và phase B |
| Tool/args kỳ vọng | get_my_profile; preview_order(product_id,quantity); get_order_status(order_id); cancel_order(order_id); update_profile(field,new_value); place_order(preview_id). Không đưa request_id/key vào model schema |
| Chưa được ghi khi nào | Chưa có host session, input sai, chưa phê duyệt đúng payload, key sai/hết hạn, đã từ chối hoặc trạng thái đơn không hợp lệ |
| failure_type | wrong_tool, wrong_arg_value, wrong_boundary, missing_info theo mục tiêu từng case |
| metadata.what_it_tests | Có trong từng case, phân biệt routing/args với việc backend thực thi |

## Fixture và hành động ghi

`evaluation_runtime.py` mở tài khoản demo, chuẩn bị PREVIEW-EVAL-001 và DEMO-EVAL-ORDER. Model không tự bịa các ID này. Wrapper place_order cấp request_id ổn định. Gọi tool ghi không key chỉ chuẩn bị pending_action; host/UI mới cấp khóa sau nút đồng ý. Eval chặn Telegram thật mặc định.

## Sửa thiết kế G09 có truy vết

G09 đo việc đổi timeframe week → year và giữ topic=news. Query “Tesla electric vehicles” vẫn đúng chủ đề; bộ cuối không chấm exact chuỗi query “Tesla”. Bản strict lưu tại `data/history/eval_group_v4_strict_query.json`, log 9/10 giữ nguyên. Không mô tả thay đổi expectation này như cải thiện model hoặc sửa log FAIL thành PASS.

## Kết quả và lệnh chạy

```powershell
cd starter_v0
python scripts/final_check.py --live
```

Kết quả đã có: base v7 20/20, group cuối 10/10, 0 provider errors. Bảng B3, đường dẫn run chính xác và phân tích nằm trong [báo cáo nhóm](../report/team/group_report.md); [version_log.csv](../starter_v0/artifacts/version_log.csv) giữ cả lần chưa đạt.

Không dùng PASS routing để khẳng định Tavily/X đã có key hoặc Telegram đã gửi thật. Hướng dẫn hiện tại: [FINAL_RUNBOOK.md](FINAL_RUNBOOK.md).
