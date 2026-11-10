# Mẫu quyết định tool mới — Thành viên 2

Mẫu này dùng để chốt yêu cầu trước khi viết code. Giữ phần ví dụ để tham khảo và điền câu trả lời vào các dòng **Bạn điền**. Nếu chưa biết, ghi `CHƯA CHỐT` và người cần trao đổi. Không cần viết code trong tài liệu này.

Các tên người, mã tài khoản, địa chỉ và sản phẩm dưới đây là dữ liệu giả phục vụ demo. Không điền mật khẩu, API key, mã OTP, số thẻ hoặc thông tin cá nhân thật vào file sẽ commit lên Git.

## 1. Thông tin người thực hiện

| Trường | Demo để hiểu cách điền | Bạn điền |
|---|---|---|
| Họ tên / MSSV | Chu Quang Linh / 2A202603809 | ... |
| Nhánh Git | `feat/new-tool` — nơi bạn làm code riêng trước khi merge | ... |
| Tool dự định làm | `update_profile` — sửa trường cho phép trong hồ sơ demo | ... |
| Người chốt schema cùng bạn | Võ Hồng Lương phụ trách registry và YAML | ... |
| Người nhận tình huống eval | Hồ Anh Tú phụ trách bộ câu hỏi kiểm tra model | ... |
| Mốc bàn giao dự kiến | Trước mốc tích hợp tool của nhóm | ... |

## 2. Chọn chức năng muốn làm

**Tool** là một hàm mà agent có thể gọi để đọc dữ liệu hoặc thực hiện hành động. Một yêu cầu của người dùng có thể cần nhiều tool.

Những gợi ý dưới đây là phương án thiết kế demo, chưa có sẵn trong starter:

| Tool đề xuất | Ví dụ người dùng nói | Tool làm gì? | Có thay đổi dữ liệu? | Phạm vi triển khai |
|---|---|---|---|---|
| `get_my_profile` | “Địa chỉ giao hàng hiện tại của tôi là gì?” | Đọc hồ sơ của tài khoản đang đăng nhập, trả những trường cần thiết | Không | Nhỏ; cần nguồn dữ liệu demo |
| `update_profile` | “Đổi địa chỉ giao hàng của tôi sang địa chỉ mới.” | Cập nhật các trường hồ sơ được cho phép sau khi xác nhận | Có | Vừa; cần kiểm tra input, quyền và xác nhận |
| `preview_order` | “Hai cuốn sổ này tổng cộng bao nhiêu?” | Tạo bản xem trước giá, số lượng, phí giao hàng; chưa đặt đơn | Không tạo đơn | Vừa; cần danh mục và bảng giá demo |
| `place_order` | “Tôi xác nhận đặt đơn vừa xem.” | Tạo đơn từ bản xem trước đã xác nhận | Có | Lớn hơn; cần chống đặt trùng và kiểm tra giá/tồn kho |
| `get_order_status` | “Đơn DEMO-1001 đang ở đâu?” | Xem đơn thuộc tài khoản hiện tại | Không | Nhỏ–vừa; cần dữ liệu đơn demo |
| `cancel_order` | “Hủy đơn DEMO-1001 giúp tôi.” | Hủy đơn của tài khoản hiện tại nếu trạng thái cho phép | Có | Vừa; cần quy tắc trạng thái và xác nhận |
| `save_research_preferences` | “Lưu chủ đề AI và ngôn ngữ tiếng Việt cho bản tin của tôi.” | Lưu sở thích research để dùng lại trong các yêu cầu sau | Có | Nhỏ–vừa; gần chủ đề research của lab hơn |

**Lưu ý về bài lab:** nhiệm vụ gốc là research agent. Nếu chọn đặt hàng hoặc sửa hồ sơ, cần thống nhất với nhóm cách chức năng đó phù hợp với sản phẩm demo; nếu định đổi hẳn chủ đề agent, trao đổi coach. Vẫn phải giữ các yêu cầu eval và deliverable của lab. Bạn chỉ cần ít nhất **một tool mới**, không bắt buộc làm cả danh sách.

- **Bạn điền — Tool chọn làm:** get_my_profile, update_profile, preview_order, place_order, get_order_status, cancel_order
- **Bạn điền — Vì sao cần tool này:** Vì các tools đã khái quát được đa dạng cách thức mà Agent hoạt động với dữ liệu.
- **Bạn điền — Nó phù hợp với research agent như thế nào:** Nó phù hợp với research agent do có nhiều tools hoạt động theo nhiều kiểu khác nhau để người thực hành lab có thể quan sát được hành vi của agent cũng như test được đa dạng cho mỗi trường hợp.
- **Bạn điền — Làm một tool hay nhiều tool:** thực hiện tất cả các tools cần làm.
- **Bạn điền — Các việc chủ động để ngoài phạm vi:** Phân quyền chi tiết ai có quyền truy cập, chỉ là demo cho nghiên cứu nên không cần thiết lập nhiều về security. Không thực hiện các nghiệp vụ phức tạp ngoài danh sách.

Demo phạm vi nhỏ: “Chỉ làm `update_profile` cho địa chỉ giao hàng và tên hiển thị trong dữ liệu giả. Chưa làm thanh toán, đổi mật khẩu, email đăng nhập hoặc đặt đơn.”

## 3. Chốt dữ liệu và môi trường chạy

**Backend** là phần lưu và xử lý dữ liệu phía sau tool. **API** là giao diện để code gửi yêu cầu đến một hệ thống khác. **Mock** là dữ liệu/hệ thống giả dùng trong test, không tạo tác động thật.

| Quyết định | Demo | Bạn điền |
|---|---|---|
| Nguồn dữ liệu | File JSON chứa 2 hồ sơ giả | Lấy theo demo |
| Nơi lưu thay đổi | File JSON demo riêng, không ghi vào dữ liệu cá nhân thật | Lấy theo demo |
| Chế độ demo tích hợp | Ghi thay đổi thật vào kho dữ liệu giả cục bộ | Lấy theo demo |
| Cách test | Dùng thư mục tạm; mỗi test có dữ liệu riêng | Lấy theo demo |
| API bên ngoài | Không dùng ở phiên bản đầu | Lấy theo demo |
| Dependency cần thêm | Không thêm; dùng thư viện Python có sẵn | Lấy theo demo |
| Biến môi trường cần thêm | Không có; nếu có thì ghi tên biến, không ghi giá trị secret | Lấy theo demo |
| Dữ liệu khởi tạo | Hồ sơ `demo-user-01`, địa chỉ cũ “Địa chỉ demo A” | Lấy theo demo |
| Cách khôi phục sau demo | Nạp lại dữ liệu khởi tạo | Lấy theo demo |

Phân biệt: unit test dùng mock/offline theo starter; demo tích hợp phải chứng minh implementation thực sự hoạt động trên nguồn dữ liệu đã chọn. Không ghi là đã đặt đơn thật nếu chỉ trả kết quả giả hoặc chạy trên kho demo.

## 4. Đầu vào của tool — agent phải truyền gì?

**Arguments / tham số** là các giá trị truyền vào hàm. **Schema** là bản mô tả tên, kiểu và điều kiện của các tham số để model biết cách gọi. **Required** nghĩa là bắt buộc; **default** là giá trị dùng khi không truyền; **enum** là danh sách giá trị được phép.

### Demo: tool cập nhật hồ sơ

Tên tool: `update_profile`

Chữ ký hàm dự kiến, chỉ để hình dung:

```python
def update_profile(field: str = "", new_value: str = "", confirmed: bool = False) -> dict:
    ...
```

| Tham số | Kiểu | Bắt buộc? | Mặc định | Quy tắc |
|---|---|---|---|---|
| `field` | string — chuỗi văn bản | Có | `""` để code bắt lỗi nếu thiếu | Chỉ `display_name` hoặc `shipping_address` |
| `new_value` | string | Có | `""` để code bắt lỗi nếu thiếu | Bỏ khoảng trắng hai đầu; không được rỗng; tối đa 200 ký tự |
| `confirmed` | boolean — đúng/sai | Không | `false` | Chỉ ghi dữ liệu khi giá trị là boolean `true`; không nhận chuỗi `"true"` |

Trong ví dụ, tài khoản đang thao tác lấy từ phiên đăng nhập đáng tin cậy. Không cho model tùy chọn `user_id` của người khác. Với demo local chưa có đăng nhập, nhóm có thể cố định một tài khoản giả và ghi rõ giới hạn đó.

### Bạn điền

- **Tên tool theo dạng snake_case** (chữ thường, nối bằng `_`): Chấp nhận
- **Tên hàm Python:** Theo cấu trúc lạc đà

| Tham số | Ý nghĩa bằng tiếng Việt | Kiểu dữ liệu | Bắt buộc? | Mặc định | Giá trị hợp lệ / giới hạn |
|---|---|---|---|---|---|
| tự đề xuất | tự đề xuất | tự đề xuất | tự đề xuất | tự đề xuất | tự đề xuất |
| tự đề xuất | tự đề xuất | tự đề xuất | tự đề xuất | tự đề xuất | tự đề xuất |
| tự đề xuất | tự đề xuất | tự đề xuất | tự đề xuất | tự đề xuất | tự đề xuất |

- **Thông tin lấy từ hệ thống thay vì để model tự truyền:** Thông tin tạo trước 1 vài dòng data mock demo
- **Nếu thiếu thông tin thì agent phải hỏi gì:** thiếu thông tin thì agent báo thiếu nội dung gì và yêu cầu người dùng cấp đầy đủ trong 1 promt
- **Nếu người dùng yêu cầu trường không hỗ trợ thì xử lý thế nào:** cảnh báo thừa trường và cần xác nhận loại bỏ để thực thi

## 5. Đầu ra — tool trả gì để agent hiểu?

**Output** là kết quả hàm trả về. **Dict / JSON object** là dữ liệu gồm các cặp tên và giá trị. **Status** là trạng thái xử lý; **error code** là mã lỗi ổn định để code hoặc test nhận biết.

Demo khi cập nhật thành công:

```json
{
  "status": "updated",
  "field": "shipping_address",
  "message": "Đã cập nhật địa chỉ giao hàng cho tài khoản demo hiện tại."
}
```

Demo khi chưa xác nhận — không được ghi dữ liệu:

```json
{
  "status": "needs_confirmation",
  "message": "Bạn xác nhận đổi địa chỉ giao hàng sang Địa chỉ demo B chứ?"
}
```

Demo lỗi đầu vào — không raise exception ra ngoài:

```json
{
  "status": "error",
  "error": "invalid_field",
  "message": "Chỉ hỗ trợ display_name và shipping_address."
}
```

### Bạn điền

- **Kết quả khi thành công:** Chấp nhận theo các đề xuất của bạn
- **Kết quả khi chưa xác nhận:** Chấp nhận theo các đề xuất của bạn
- **Kết quả khi không tìm thấy hồ sơ/đơn:** Chấp nhận theo các đề xuất của bạn
- **Kết quả khi dữ liệu không hợp lệ:** Chấp nhận theo các đề xuất của bạn
- **Kết quả khi lỗi file/API:** Chấp nhận theo các đề xuất của bạn
- **Thông tin nào không cần trả về hoặc cần che bớt:** Chấp nhận theo các đề xuất của bạn

## 6. Khi nào agent dùng tool và hỏi xác nhận?

**Routing** là quyết định chọn tool nào. **Side effect** là tác động làm thay đổi dữ liệu hoặc thế giới bên ngoài, như sửa địa chỉ hoặc tạo đơn. **Guardrail** là điều kiện kiểm tra trong code để ngăn hành động sai.

### Demo hội thoại cập nhật địa chỉ

1. User: “Đổi địa chỉ giao hàng của tôi.”
2. Agent: “Bạn muốn đổi sang địa chỉ nào?” Chưa ghi dữ liệu.
3. User: “Địa chỉ demo B.”
4. Agent: “Bạn xác nhận đổi địa chỉ giao hàng của tài khoản hiện tại sang Địa chỉ demo B chứ?”
5. User: “Tôi xác nhận.”
6. Agent gọi `update_profile(field="shipping_address", new_value="Địa chỉ demo B", confirmed=True)`.
7. Tool kiểm tra điều kiện rồi ghi dữ liệu; agent báo kết quả theo output thật.

`confirmed=true` là tín hiệu xác nhận, **không phải bằng chứng đăng nhập hay quyền sở hữu tài khoản**. Prompt và UI phải bảo đảm tín hiệu này tương ứng với lời xác nhận đúng nội dung. Backend vẫn kiểm tra quyền; nếu có nhiều người dùng, cần cơ chế gắn xác nhận với đúng phiên và đúng dữ liệu thao tác. Khi dữ liệu thay đổi sau xác nhận, phải xác nhận lại.

### Bạn điền

- **Ví dụ yêu cầu nên dùng tool này:** vì key khá rộng nên thay vì liệt kê tôi muốn hoạt động theo kiểu gắn vai trò của tools với master promt để khi hoạt động là Agent biết sử dụng tools nào
- **Ví dụ yêu cầu không nên dùng tool này:** vì key khá rộng nên thay vì liệt kê tôi muốn hoạt động theo kiểu gắn vai trò của tools với master promt để khi hoạt động là Agent biết sử dụng tools nào
- **Nếu chỉ hỏi xem thông tin, dùng tool nào:** các hàm get thì chỉ cần lấy thông tin để xem
- **Thông tin phải có trước khi hỏi xác nhận:** đồng ý
- **Câu hỏi xác nhận cụ thể agent sẽ hiển thị:** chấp nhận
- **Nếu người dùng từ chối hoặc đổi ý:** dừng luôn tại lựa chọn đấy
- **Code ngăn ghi dữ liệu khi chưa xác nhận bằng cách nào:** thêm điều kiện gắn kèm nút xác nhận và kiểm tra kèm xác nhận mới thực hiện thay đổi dữ liệu. không sử dụng AI để biết trạng thái mà có thể gửi kèm khi nhấn button xác nhận một key cơ bản để tools xác nhận key.
- **Tài khoản hiện tại và quyền thao tác lấy từ đâu:** hiện tại chưa cần quyền hay phân quyền mà là một bản test chạy nghiên cứu về hành vi AI
- **Nếu không có xác thực thật trong demo, giới hạn cần công bố:** nếu không có xác thực thì hành vi không được thực thi.

## 7. Nếu chọn đặt hàng, cần quyết định thêm

Nếu chỉ chọn cập nhật hồ sơ, ghi `Không áp dụng` tại đây. Không cần xây chức năng đặt hàng chỉ để điền mẫu.

| Quyết định | Demo | Bạn điền |
|---|---|---|
| Dữ liệu sản phẩm | `DEMO-NOTEBOOK`, giá 25.000 VND/cuốn từ danh mục giả | Chấp nhận chạy theo demo |
| Giới hạn số lượng | Số nguyên từ 1 đến 10 | Chấp nhận chạy theo demo |
| Cách tính tổng | 2 cuốn × 25.000 + phí giao hàng demo 10.000 = 60.000 VND | Chấp nhận chạy theo demo |
| Nội dung cần xác nhận | Mặt hàng, số lượng, tổng tiền, địa chỉ và cách thanh toán | Chấp nhận chạy theo demo |
| Thanh toán | Chỉ mô phỏng COD, không thu tiền thật | Chấp nhận chạy theo demo |
| Khi giá hoặc tồn kho thay đổi | Trả yêu cầu xem lại đơn; xác nhận lại nội dung mới | Chấp nhận chạy theo demo |
| Khi bị gọi lặp | Cùng mã yêu cầu trả lại đơn đã tạo, không tạo đơn thứ hai | Chấp nhận chạy theo demo |
| Khi timeout sau tạo đơn | Kiểm tra trạng thái theo mã yêu cầu trước khi thử lại | Chấp nhận chạy theo demo |
| Điều kiện hủy | Chỉ hủy đơn demo chưa giao; hỏi xác nhận | Chấp nhận chạy theo demo |

**Idempotency / chống tạo trùng** nghĩa là gọi lại cùng một yêu cầu tạo đơn không tạo thêm đơn thứ hai. Đây là vấn đề khác với việc người dùng đã xác nhận hay chưa.

- **Bạn điền — Có làm luồng đặt hàng không:** không cần làm luồng, chỉ cần demo tạo mới trong một bảng data chỉ để hiển thị ra giao diện khi hoàn thành request
- **Bạn điền — Tool nào xem trước, tool nào thực sự tạo đơn:** theo như bảng đề xuất cũng đã mô tả rõ vấn đề này
- **Bạn điền — Mã yêu cầu chống trùng được tạo và lưu ở đâu:** tất cả data chỉ cần thiết lập cơ bản để CRUD lưu vào SQLite

## 8. Các test TV2 sẽ viết

**Unit test** kiểm tra code của tool bằng input cụ thể. **Eval case** kiểm tra model chọn tool/arguments có đúng không. Tool chạy đúng chưa có nghĩa model sẽ gọi đúng tool, và ngược lại.

Lab bắt buộc **≥3 unit test cho mỗi tool mới**, gồm thành công, input xấu và nhánh lỗi. Với tool hành động, nên thêm test xác nhận và quyền thao tác. Mọi HTTP trong unit test phải mock theo `tests/conftest.py`.

| Test | Demo với update_profile | Bạn điền |
|---|---|---|
| Thành công | confirmed=True, field hợp lệ: đúng hồ sơ được sửa, trường khác giữ nguyên | Chấp nhận theo demo và bạn từ đề xuất tương ứg cho các tools khác |
| Input xấu | new_value chỉ có khoảng trắng: trả lỗi và dữ liệu không đổi | Chấp nhận theo demo và bạn từ đề xuất tương ứg cho các tools khác |
| Lỗi xử lý | Giả lập lỗi ghi file: trả error dict, không báo thành công, không để dữ liệu dở dang | Chấp nhận theo demo và bạn từ đề xuất tương ứg cho các tools khác |
| Chưa xác nhận | confirmed=False: trả needs_confirmation, không ghi file/gọi API ghi | Chấp nhận theo demo và bạn từ đề xuất tương ứg cho các tools khác |
| Sai kiểu | confirmed="true": từ chối, không coi chuỗi là xác nhận hợp lệ | Chấp nhận theo demo và bạn từ đề xuất tương ứg cho các tools khác |
| Quyền thao tác | Thiếu phiên hợp lệ: từ chối cập nhật; nếu demo tài khoản cố định, ghi rõ phần chưa hỗ trợ | Chấp nhận theo demo và bạn từ đề xuất tương ứg cho các tools khác |
| Gọi lặp nếu tạo đơn | Cùng mã yêu cầu hai lần: chỉ có một đơn | Chấp nhận theo demo và bạn từ đề xuất tương ứg cho các tools khác |

- **Bạn điền — Ít nhất 3 test bắt buộc đã chọn:** tất cả test
- **Bạn điền — Những test bổ sung cho hành động ghi:** bạn tự đề xuất
- **Bạn điền — Cách kiểm tra dữ liệu trước/sau hoặc request đã gửi:** manual test và auto test

## 9. Tình huống bàn giao TV3 để viết eval

Demo một case multi turn, các bước dưới đây là mô tả yêu cầu, chưa phải JSON theo schema runner:

| Lượt | Người dùng nói | Hành vi mong đợi |
|---|---|---|
| 1 | “Đổi địa chỉ giao hàng của tôi.” | Dùng clarify để hỏi địa chỉ mới; không cập nhật |
| 2 | “Địa chỉ demo B.” | Hỏi xác nhận đúng nội dung; chưa cập nhật |
| 3 | “Tôi xác nhận đổi sang Địa chỉ demo B.” | Gọi update_profile với field, new_value đúng và confirmed=true |

TV3 cần kiểm tra runner hỗ trợ kỳ vọng từng lượt như thế nào rồi chuyển thành format thật của `eval_group.json`. Các case cho tool mới nằm **trong tổng 10 case** của nhóm.

- **Bạn điền — User query hoặc chuỗi turns:** ...
- **Bạn điền — Tool và arguments kỳ vọng:** ...
- **Bạn điền — Lúc nào tuyệt đối chưa được gọi hành động ghi:** ...
- **Bạn điền — failure_type dự kiến:** ...
- **Bạn điền — metadata.what_it_tests (case kiểm tra điều gì):** ...

Demo failure_type: `wrong_boundary` — kiểm tra agent có cập nhật hồ sơ trước khi được xác nhận không. Các giá trị lab cho phép: `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`.

## 10. Bàn giao để merge

Theo phân công: TV2 sở hữu implementation, TOOL.md và test; TV1 cập nhật registry/YAML; TV3 sở hữu eval nhóm; TV4 sở hữu UI và requirements.txt. TV2 gửi dependency cần thêm cho TV4.

- [ ] Chức năng, phạm vi và nguồn dữ liệu đã chốt.
- [ ] Tên tool, tham số và output thống nhất với TV1/TV3.
- [ ] Có `starter_v0/tools/<ten_tool>/tool.py`.
- [ ] Có `starter_v0/tools/<ten_tool>/TOOL.md` đúng contract trong `tools/README.md`.
- [ ] TOOL.md khai báo đúng side_effect; tool hành động có requires_confirmation.
- [ ] Có ≥3 test/tool mới trong `starter_v0/tests/test_tools_todo.py` và không còn skip.
- [ ] Gửi schema và import/registry key cho TV1.
- [ ] Gửi dependency và tên biến môi trường cho TV4 nếu có.
- [ ] Gửi tình huống eval và expected arguments cho TV3.
- [ ] Sau đăng ký tool, contract test và toàn suite `pytest` đều 0 failed.
- [ ] Không commit dữ liệu cá nhân thật hoặc secret; log demo dùng dữ liệu giả.
- [ ] Gửi bằng chứng code/test và hạn chế cho báo cáo nhóm B5a.
- [ ] Hoàn thành báo cáo cá nhân `report/team/MSSV_HoTen.md`.

**Bạn điền — Link PR / commit / bằng chứng test:** ...

**Bạn điền — Các quyết định còn cần nhóm hỗ trợ:** ...

## 11. Từ điển nhanh và nơi tra trong repo

| Thuật ngữ | Hiểu đơn giản | Nơi tra / ví dụ |
|---|---|---|
| Contract | Thỏa thuận code và model cùng tuân theo | `starter_v0/tools/README.md` |
| Tool declaration | Mô tả tool để model biết tên, công dụng và input | `starter_v0/artifacts/tools.yaml` |
| Registry | Danh bạ nối tên tool với hàm Python | `TOOL_FUNCTIONS` trong `starter_v0/tools/__init__.py` |
| Frontmatter | Khối metadata YAML ở đầu TOOL.md, nằm giữa hai dòng `---` | TOOL.md của tool có sẵn |
| Validation | Kiểm tra input có đúng kiểu, hợp lệ và đủ dữ liệu không | Không nhận số lượng âm hoặc địa chỉ rỗng |
| Authentication | Xác định người đang dùng là ai | Phiên đăng nhập do hệ thống kiểm chứng |
| Authorization | Kiểm tra người đó được phép làm gì | Chỉ sửa hồ sơ của chính tài khoản hiện tại |
| Confirmation | Người dùng đồng ý với nội dung hành động cụ thể | “Tôi xác nhận đổi sang Địa chỉ demo B” |
| Mock / fixture | Dữ liệu và môi trường giả, có thể dùng lại trong test | `starter_v0/tests/conftest.py` |
| Regression test | Test giữ lại để lỗi đã sửa không tái xuất hiện | Sau sửa bug input rỗng, test đó luôn được chạy lại |
| Atomic update | Ghi thành công toàn bộ hoặc giữ nguyên dữ liệu cũ | Lỗi ghi không làm file hồ sơ bị hỏng một nửa |
| Timeout | Hết thời gian chờ phản hồi | Không tự kết luận đặt hàng thất bại rồi tạo trùng |
| Merge / PR | Ghép code nhánh riêng về nhánh chung / đề nghị ghép để review | TV1 tích hợp PR sau khi kiểm tra |

Nguồn yêu cầu bắt buộc: `README.md`, `RULES.md`, `starter_v0/README.md`, `starter_v0/tools/README.md`. Ví dụ hồ sơ và đặt hàng trong mẫu này là thiết kế minh họa để bạn tự chọn, không phải chức năng starter đã triển khai.
