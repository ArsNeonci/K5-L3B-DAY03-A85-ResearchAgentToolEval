# Báo cáo cá nhân — Chu Quang Linh

**Cập nhật bản cuối:** các số 122 passed/17 skipped bên dưới là kết quả giai đoạn trước. Đợt hoàn thiện 11/11/2026 đã đạt 155 passed +16 subtests, 0 skipped; live base 20/20 và group 10/10. Chi tiết thay đổi thiết kế G09 và giới hạn API nằm ở [báo cáo nhóm](group_report.md), [runbook](../../docs/FINAL_RUNBOOK.md) và [manifest](../../starter_v0/analysis/submission_evidence.json).

## 1. Thông tin thành viên

- Họ tên: Chu Quang Linh.
- MSSV: 2A202603809.
- Vai trò: Thành viên 2 — tool mới, backend dữ liệu demo, unit test và bàn giao tích hợp.
- Nhánh làm việc: `tv2-linh`.
- Ngày cập nhật báo cáo: 11/11/2026 (giờ Việt Nam).

## 2. Phần việc phụ trách

Phần việc TV2 là xây dựng tool độc lập để nhóm kiểm tra hành vi agent khi đọc thông tin, chuẩn bị thay đổi dữ liệu và thực hiện hành động sau xác nhận. Phạm vi đã chọn gồm sáu tool hồ sơ và đơn hàng, chạy trên SQLite với dữ liệu giả. Không kết nối cửa hàng, không thu tiền và không xử lý tài khoản thật.

Các đầu ra gồm implementation Python, tài liệu TOOL.md, schema mô tả tool, test offline, console demo và tài liệu bàn giao. TV1 phụ trách registry, YAML và prompt chung; TV3 phụ trách eval và báo cáo nhóm; TV4 phụ trách UI và nút phê duyệt. Sau khi TV1 tích hợp, phần TV2 tiếp tục kiểm tra contract và toàn suite pytest.

## 3. Đóng góp cụ thể

### 3.1. Đặc tả và triển khai sáu tool

Các quyết định về chức năng, input/output, nguồn dữ liệu, xác nhận và test được ghi trong [mẫu quyết định tool](../../docs/TV2_MAU_QUYET_DINH_TOOL.md). SQLite được chọn theo quyết định cụ thể ở mục đặt hàng, thay cho cách lưu JSON trong ví dụ ban đầu.

| Tool | Hành vi đã triển khai | Điều kiện chính |
|---|---|---|
| `get_my_profile` | Đọc tên hiển thị và địa chỉ giao hàng của tài khoản demo hiện tại | Có session do host thiết lập; không nhận user_id từ model |
| `update_profile` | Sửa `display_name` hoặc `shipping_address` | Kiểm tra input và khóa xác nhận đúng phiên/nội dung |
| `preview_order` | Tính tổng và lưu bản xem trước đơn | Số lượng nguyên 1–10; giá từ SQLite; chưa tạo đơn/trừ tồn |
| `place_order` | Tạo đơn pending và trừ tồn kho trong một transaction | Preview còn hạn, giá/tồn hợp lệ, có phê duyệt; chống trùng theo request_id ở backend |
| `get_order_status` | Đọc thông tin và trạng thái đơn | Đơn thuộc tài khoản demo hiện tại |
| `cancel_order` | Hủy đơn pending, hoàn lại tồn kho | Có phê duyệt; gọi lại đơn đã hủy không hoàn tồn thêm |

Backend chung đặt tại [commerce_demo/backend.py](../../starter_v0/commerce_demo/backend.py), tránh lặp logic SQLite, validation và xác nhận giữa các tool. Mỗi tool có `tool.py` và `TOOL.md` riêng dưới `starter_v0/tools/`. Tên tool dùng snake_case; hàm Python dùng camelCase theo đặc tả.

### 3.2. Kiểm soát thay đổi dữ liệu và lỗi

- Thiếu dữ liệu: liệt kê các trường còn thiếu để hỏi đủ trong một lượt. Trường ngoài phạm vi: báo rõ, yêu cầu người dùng đồng ý bỏ trường đó trước khi tiếp tục.
- Không có session hợp lệ: từ chối thao tác. Session chỉ là lựa chọn tài khoản giả do host thiết lập, không được trình bày như hệ thống đăng nhập thật.
- Ba action sửa hồ sơ/tạo đơn/hủy đơn chỉ chuẩn bị `pending_action` khi chưa có khóa xác nhận. Host/UI cấp khóa sau lựa chọn đồng ý của người dùng; model không được cấp hay tự tạo khóa.
- Khóa có hạn 300 giây, dùng một lần và ràng buộc tài khoản, phiên, action, payload. Thay đổi nội dung cần phê duyệt lại.
- Preview có hạn 600 giây; giá hoặc tồn kho không hợp lệ thì yêu cầu xem trước lại. Tổng tiền lấy từ danh mục demo, không tin giá do model gửi.
- Transaction đảm bảo ghi đơn, trừ tồn và dùng khóa cùng thành công hoặc cùng rollback. Lỗi storage trả error dict thay vì báo thành công hoặc làm agent crash.
- Database tạm và khóa xác nhận không được commit hoặc ghi vào transcript công khai. Không thêm API key, dependency hoặc dịch vụ bên ngoài cho backend này.

### 3.3. Kiểm thử và khắc phục vấn đề môi trường

Đã chuẩn bị 30 test offline trong [test_tv2_tools.py](../../starter_v0/tests/test_tv2_tools.py). Mỗi tool có kiểm tra thành công, input không hợp lệ và lỗi storage; các test bổ sung kiểm tra session, xác nhận sai/hết hạn, retry không tạo trùng, trạng thái đơn và rollback.

Test dùng SQLite tạm riêng từng ca để không làm thay đổi dữ liệu demo chung. Console demo đi qua cả sáu tool, từ đọc/sửa hồ sơ đến xem trước/tạo/xem/hủy đơn. Smoke test này được chạy tự động bằng subprocess và ba dòng `YES` qua stdin; đây không phải bằng chứng Linh đã kiểm thử thủ công trên UI.

Trong lần chạy đầu, Windows sandbox chặn truy cập thư mục do tempfile tạo. Cách xử lý là chạy kiểm tra ngoài sandbox với dữ liệu giả; không bỏ guardrail hoặc sửa kết quả test. Các kết nối SQLite được đóng rõ ràng để tránh giữ file khi dọn thư mục tạm trên Windows.

Sau tích hợp của TV1, đã chạy lại contract test và toàn suite. Không có lỗi cần sửa source tool trong đợt kiểm tra này.

### 3.4. Đối chiếu checklist TV2

| Mục | Nội dung hoàn thành | Bằng chứng |
|---|---|---|
| TV2-01–02 | Chọn chức năng; xác định tên hàm, input/output và quy tắc lỗi | Mẫu quyết định; schema và tài liệu bàn giao |
| TV2-03 | Xác định SQLite local, không API/dependency mới; chỉ ra các action ghi và điều kiện xác nhận | Backend và TOOL.md |
| TV2-04 | Đối chiếu contract folder tool và mẫu test của starter khi triển khai | TOOL.md từng tool; test mới; kết quả contract test |
| TV2-05–06 | Triển khai sáu tool và sáu TOOL.md | Sáu thư mục tool trong commit `4d6cfb4` |
| TV2-07–09 | Có happy path, input xấu và nhánh lỗi cho từng tool | 30 test mới đều chạy, không skip |
| TV2-10 | Bàn giao code, schema và import/registry key cho TV1 | Schema fragment; TV1 đã tích hợp vào registry/YAML |
| TV2-11 | Bàn giao query, expected tool/arguments và tình huống boundary cho TV3 | Mục TV3 trong tài liệu bàn giao; đã xác nhận hoàn thành |
| TV2-12 | Kiểm tra contract và toàn suite sau tích hợp | Contract 85 passed; full suite 122 passed, 17 skipped, 0 failed |
| TV2-13 | Bàn giao bằng chứng tool/test và hạn chế để tổng hợp B5a | Báo cáo kiểm tra riêng; đã xác nhận hoàn thành |
| TV2-14 | Hoàn thiện báo cáo cá nhân và khai báo đóng góp trong TEAM.md | Báo cáo này và mục Chu Quang Linh trong TEAM.md |

Test mới đặt riêng trong `tests/test_tv2_tools.py` để không sửa file stub chung `test_tools_todo.py`; pytest vẫn thu thập và thực thi. Các mục bonus TV2-15–16 về hoàn thiện test tool cũ/tìm bug tool cũ chưa được ghi nhận hoàn thành.

## 4. Bằng chứng, công cụ và cách kiểm tra

### 4.1. File và commit

| Đầu ra | Đường dẫn / commit |
|---|---|
| Implementation backend | [commerce_demo/backend.py](../../starter_v0/commerce_demo/backend.py) |
| Implementation tool và TOOL.md | `starter_v0/tools/get_my_profile/`, `update_profile/`, `preview_order/`, `place_order/`, `get_order_status/`, `cancel_order/` |
| Schema bàn giao | [tools_tv2.fragment.json](../../starter_v0/artifacts/tools_tv2.fragment.json) |
| Unit test riêng | [test_tv2_tools.py](../../starter_v0/tests/test_tv2_tools.py) |
| Console demo | [demo_tv2_tools.py](../../starter_v0/scripts/demo_tv2_tools.py) |
| Hướng dẫn tích hợp | [TV2_LINH_HANDOFF.md](../../docs/TV2_LINH_HANDOFF.md) |
| Bằng chứng kiểm tra | [TV2_LINH_TOOL_TESTS.md](TV2_LINH_TOOL_TESTS.md) |
| Đóng góp nhóm | [TEAM.md](../../TEAM.md) |
| Code/tool/test bàn giao ban đầu | [4d6cfb4](https://github.com/ArsNeonci/K5-L3B-DAY03-A85-ResearchAgentToolEval/commit/4d6cfb4) |
| Bản tích hợp TV1 được dùng để kiểm tra | [c04f5da](https://github.com/ArsNeonci/K5-L3B-DAY03-A85-ResearchAgentToolEval/commit/c04f5da) |
| Ghi kết quả hoàn thành TV2-12 | [5ccabb6](https://github.com/ArsNeonci/K5-L3B-DAY03-A85-ResearchAgentToolEval/commit/5ccabb6) |

TV1 bổ sung wrapper `place_order_auto_request_id`: model chỉ truyền preview_id; request_id được tạo trong registry. Khi phê duyệt, host gọi hàm gốc với request_id của pending action. Đây là đóng góp tích hợp của TV1, không tính thành phần code TV2 tự bổ sung. Chi tiết tại [TV1_INTEGRATION_NOTES.md](../../docs/TV1_INTEGRATION_NOTES.md).

### 4.2. Kết quả đã đo

Chạy từ `starter_v0/`:

| Lệnh kiểm tra | Kết quả thực tế |
|---|---|
| `python -m unittest discover -s tests -p test_tv2_tools.py -q` | 30 tests, OK |
| `.\.venv\Scripts\python.exe -m pytest tests/test_tool_contract.py -q` | 85 passed |
| `.\.venv\Scripts\python.exe -m pytest -q` | 122 passed, 17 skipped, 16 subtests passed; 0 failed |

85 contract test và 30 test tool mới nằm trong kết quả toàn suite, không cộng các số này để báo cáo thành tổng test khác. 17 skipped là stub tool cũ, không phải test mới của TV2; điều kiện bắt buộc 0 failed đã đạt, bonus toàn suite 0 skipped chưa đạt.

Các con số trên lấy từ lần chạy ngày 10/11/2026 được ghi trong báo cáo kiểm tra, không phải kết quả chạy mới vào ngày cập nhật tài liệu. Chưa có metric model/eval hoặc bằng chứng UI chung trong phần kiểm tra TV2 này.

### 4.3. Sử dụng AI và kiểm chứng

Codex được dùng để hỗ trợ triển khai code, viết test, tài liệu, thao tác Git và chạy lệnh kiểm tra theo đặc tả Linh cung cấp. Báo cáo ghi nhận phần việc có hỗ trợ AI, không coi toàn bộ code là kết quả tự viết thủ công.

Kết quả hỗ trợ được kiểm chứng bằng test chạy thật, assert dữ liệu SQLite trước/sau, lỗi đầu vào, khóa xác nhận, idempotency và rollback; contract test đối chiếu declaration với registry và code. Không dùng AI/model trong backend tool hoặc để quyết định trạng thái xác nhận khi chạy test. Không sử dụng số liệu mô phỏng thay cho output test thực tế.

## 5. Tự đánh giá phần việc theo bằng chứng

Phần việc bắt buộc TV2 đã có đầy đủ đầu ra: sáu tool, tài liệu, schema, test, bàn giao và kiểm tra sau tích hợp. Việc tách backend khỏi prompt/UI giúp triển khai độc lập, còn contract test giúp phát hiện sai lệch giữa schema và implementation trước khi nhóm chạy eval.

Điểm kỹ thuật quan trọng là phân biệt ba lớp: model chọn tool/arguments; tool kiểm tra và xử lý dữ liệu; host/UI thu nhận phê duyệt. Test tool xanh chỉ chứng minh hành vi code trong những tình huống đã kiểm tra, không chứng minh model route đúng hoặc UI đã bảo đảm xác nhận. Việc có chuỗi đồng ý trong hội thoại cũng không thay thế khóa do host cấp.

Các giới hạn còn lại:

- Chỉ có dữ liệu giả và lựa chọn tài khoản demo; chưa có đăng nhập thật, phân quyền chi tiết hoặc thanh toán.
- Chưa xác nhận UI chung, luồng chat live và routing của model trong phần việc TV2. Các phần này thuộc quá trình tích hợp/eval của nhóm.
- Backend chống trùng theo request_id, nhưng wrapper TV1 sinh request_id mới ở mỗi lần model gọi. Vì vậy kết quả backend không được suy diễn thành bảo đảm chống trùng cho mọi lần gọi lặp từ model/UI.
- Bộ test chưa khẳng định mọi tình huống đồng thời hoặc vận hành production; chưa hoàn thành bonus test các tool cũ.

Hướng cải thiện tiếp theo là kiểm tra UI phê duyệt từ đầu đến cuối, thống nhất giữ request_id theo từng ý định đặt hàng và bổ sung eval đo lỗi routing/arguments trên các tình huống do TV3 chọn. Không tự chấm điểm cá nhân hoặc khẳng định đã thực hiện kiểm thử thủ công chưa có bằng chứng.

## 6. Bổ sung trong đợt hoàn thiện theo ủy quyền

- Codex hỗ trợ sửa strict boolean ở send, wrapper request_id ổn định theo preview và trả error dict khi argument thừa.
- Nối chat/console với SQLite session, phê duyệt qua host, lưu transcript có che khóa; có test UI/CLI/serialization thực tế.
- Thay toàn bộ stub TODO bằng test offline có assertion; chạy 155 test và 16 subtest, không fail/skip.
- Chạy provider thật: base v7 đạt 20/20; group cuối 10/10. Bản strict query trước đó 9/10 được giữ; G09 cuối chỉ chấm topic/timeframe đúng mục tiêu, không nhận thay đổi expectation là cải thiện model.
- Ghi ba kịch bản UI bằng model thật với input script hóa; không coi đó là kiểm thử thủ công cá nhân hoặc Telegram gửi thật.
- Hoàn thiện báo cáo nhóm/cá nhân theo bằng chứng, hướng dẫn một lệnh và CI. UI chỉ localhost theo quyết định người dùng; các API key Tavily/Firecrawl/RapidAPI vẫn cần bổ sung nếu dùng các nguồn đó.
