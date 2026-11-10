"""Build factual report tables from saved runs and live UI transcript evidence."""
from pathlib import Path
import csv
import json
import sys
import hashlib
import yaml

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
GROUP=REPO/'report/team/group_report.md'


def read(path):return json.loads(path.read_text(encoding='utf-8'))
def link(path):return f'[{path.name}](../../starter_v0/{path.relative_to(ROOT).as_posix()})'
def metric(d):
    s=d['summary']
    return f"case {s['case_accuracy']:.2f}; routing {s.get('tool_routing_accuracy',0):.2f}; args {s.get('argument_accuracy',0):.2f}; multi {s.get('multiturn_accuracy',0):.2f}"


def main():
    runs=[(p,read(p)) for p in sorted((ROOT/'runs').glob('*.json'))]
    cases=read(ROOT/'data/eval_group.json')['cases']
    expected={c['id']:c['expect'] for c in cases}
    candidates=[(p,d) for p,d in runs if d['suite']=='group' and d['version']=='v7-final'
                and {r['id']:r['expect'] for r in d['results']}==expected]
    group_path,group=max(candidates,key=lambda x:x[0].name)
    base_path,base=max(((p,d) for p,d in runs if d['suite']=='base' and d['version']=='v7-final'),key=lambda x:x[0].name)
    summary=read(ROOT/'analysis/live_demo_summary.json')
    check=read(ROOT/'analysis/final_check.json')
    old=GROUP.read_text(encoding='utf-8')
    archive=REPO/'report/team/history'
    archive.mkdir(exist_ok=True)
    original_report=archive/'group_report_before_final.md'
    if not original_report.exists():original_report.write_text(old,encoding='utf-8')
    original=original_report.read_text(encoding='utf-8')
    failure=original.split('### B2. Failure Analysis',1)[1].split('### B3.',1)[0] if '### B2. Failure Analysis' in original else ''
    if not failure.strip():raise RuntimeError('Preserve the original baseline analysis before rebuilding report.')
    log_path=ROOT/'artifacts/version_log.csv'
    with log_path.open(encoding='utf-8',newline='') as handle:
        reader=csv.DictReader(handle); fields=reader.fieldnames; rows=list(reader)
    known={x['run_file'] for x in rows}
    hypotheses={
        'v4-integrated':('code + system_prompt.md','Integration baseline: host session, strict confirmation, no-send eval and priority rules.'),
        'v5-final':('system_prompt.md','Explicit decision order prevents empty social search and makes send clarification yes_no take priority.'),
        'v6-confirmation':('system_prompt.md','Accept explicit confirmation of exact content from user context without asking again.'),
        'v7-final':('system_prompt.md','Minimal entity-query convention should reduce unrelated query expansions; evaluate without altering base cases.'),
    }
    before={'base':'case_accuracy=0.95 (v3 base)','group':'new group dataset; not directly comparable to v3'}
    for path,d in runs:
        if d['version'] not in hypotheses:continue
        relative='starter_v0/'+path.relative_to(ROOT).as_posix()
        changed,hypothesis=hypotheses[d['version']]
        reason=f"suite={d['suite']}; openai/gpt-4o-mini; external sending disabled"
        if path==group_path:
            changed='data/eval_group.json (G09 expectation)'
            hypothesis='G09 measures topic/timeframe correction, not exact wording of synonymous queries; archive strict dataset and keep 9/10 run.'
            reason+='; evaluator-design correction, NOT claimed as model improvement'
        if relative not in known:
            rows.append(dict(version=d['version'],author='Chu Quang Linh (Codex-assisted)',changed_artifact=changed,
                artifact_version=d['artifact_version'],prompt_hash=d['prompt_hash'],tools_hash=d['tools_hash'],
                reason=reason,hypothesis=hypothesis,metric_before=before[d['suite']],metric_after=metric(d),run_file=relative))
        before[d['suite']]=metric(d)
    with log_path.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader();writer.writerows(rows)
    table='\n'.join(f"| {d['version']} | {d['suite']} | {d['summary']['passed_cases']}/{d['summary']['total_cases']} | {d['summary']['tool_routing_accuracy']:.0%} | {d['summary']['argument_accuracy']:.0%} | {link(p)} |" for p,d in runs)
    declarations=yaml.safe_load((ROOT/'artifacts/tools.yaml').read_text(encoding='utf-8'))['tools']
    descriptions={
        'clarify':'Hỏi lại và chờ người dùng','timeline':'Bài đăng theo tài khoản X (RapidAPI)',
        'social_search':'Bài đăng theo chủ đề X (RapidAPI)','lookup':'Tìm web/tin tức (Tavily)',
        'fetch':'Đọc URL (Firecrawl)','format':'Định dạng dữ liệu đã có',
        'send':'Gửi Telegram sau xác nhận; bị chặn trong UI/eval mặc định',
        'policy':'Tra cứu policy markdown nội bộ','papers':'Tìm paper arXiv qua API công khai',
        'paper_text':'Đọc PDF arXiv','get_my_profile':'Đọc hồ sơ demo','update_profile':'Chuẩn bị/sửa tên hoặc địa chỉ',
        'preview_order':'Xem trước giá và địa chỉ, chưa tạo đơn','place_order':'Tạo đơn demo sau phê duyệt',
        'get_order_status':'Xem đơn demo','cancel_order':'Hủy đơn pending sau phê duyệt'}
    tool_table='\n'.join(f"| {x['name']} | {descriptions[x['name']]} | {'Có' if x['name'] in {'get_my_profile','update_profile','preview_order','place_order','get_order_status','cancel_order'} else 'Không'} |" for x in declarations)
    case_table='\n'.join(f"| {r['id']} | {'Multi' if r['is_multiturn'] else 'Single'} | {', '.join(t['name'] for t in r['expect'].get('tool_calls',[]))} | {'PASS' if r['result']['passed'] else 'FAIL'} | {r['metadata']['what_it_tests'].replace('|','/')} |" for r in group['results'])
    chat_rows=[]
    for scenario in summary:
        path=ROOT/scenario['transcript'];doc=read(path)
        for turn in doc['turns']:
            tools=', '.join(e['tool'] for e in turn.get('tool_events',[])) or 'Không gọi tool'
            outcome=turn['status']
            if any(e.get('result',{}).get('error')=='blocked_in_demo' for e in turn.get('tool_events',[])):outcome+='; Telegram bị chặn, chưa gửi'
            chat_rows.append(f"| {scenario['scenario']} / {turn['turn_index']} | {turn['user'].replace('|','/')} | {tools} | {outcome} | {link(path)} |")
    report=f'''# Báo cáo nhóm — A85 — Research Agent Tool Eval

## 1. Thông tin nhóm

- Lớp: K5-L3B. Phân công và báo cáo cá nhân: [TEAM.md](../../TEAM.md).
- Provider/model: OpenRouter / openai/gpt-4o-mini. Bản cuối: v7-final.
- Cập nhật: 11/11/2026 (GMT+7). Không hồi tố thời gian hoàn thành: bản Phần A hoàn thiện này được bổ sung sau mốc showdown.

## 2. PHẦN A — Giới thiệu agent

### A1. Chức năng, lệnh chạy và link dùng thử

Agent tra cứu web/X/arXiv hoặc policy nội bộ, định dạng kết quả và có sáu tool hồ sơ/đơn hàng demo trên SQLite. Các thay đổi hồ sơ/tạo/hủy đơn phải qua nút phê duyệt; dữ liệu commerce là dữ liệu giả, không thanh toán thật.

```powershell
cd starter_v0
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1
```

**Link dùng thử trên máy chạy:** http://127.0.0.1:8502 — đã kiểm tra health HTTP 200. Người dùng đã chọn chỉ localhost, không mở public. Link này không mở từ máy khác; chưa có bằng chứng người ngoài nhóm dùng được link public.

Key provider có trong .env ở gốc repo hoặc starter_v0/.env; DAY03_ENV_FILE được ưu tiên nếu dùng file ngoài. Không commit .env. Hiện provider hoạt động; Tavily/Firecrawl/RapidAPI chưa được cấu hình nên lookup/fetch/X trả lỗi cấu hình rõ ràng thay vì giả dữ liệu. Policy, SQLite và API arXiv công khai vẫn dùng được. UI chặn Telegram thật.

### A2. Tool của agent

| Tool | Chức năng | Nhóm tự viết mới? |
|---|---|---|
{tool_table}

### A3. Câu hỏi mẫu

1. Tìm quy định công ty về trích dẫn nguồn nghiên cứu và tóm tắt các điểm chính.
2. Đổi địa chỉ giao hàng của tôi. Sau khi được hỏi, trả lời: Địa chỉ demo B; kiểm tra nội dung rồi bấm Đồng ý hoặc Từ chối.
3. Xem trước 2 cuốn DEMO-NOTEBOOK, dùng địa chỉ hiện tại; chưa đặt đơn.
4. Xem tên hiển thị và địa chỉ giao hàng hiện tại của tôi.
5. Gửi lên Telegram đúng nội dung: Bản tin nghiên cứu demo A85. Quan sát hỏi xác nhận và thông báo chặn gửi trong demo.

## 3. Giải pháp

- Giữ nguyên testcase base/extension của starter, giữ run v0–v3 và snapshot prompt/tools lịch sử.
- Tối ưu prompt theo log: bỏ chỉ dẫn đoán/gửi luôn; thêm routing; sau tích hợp bổ sung thứ tự ưu tiên hỏi lại và xử lý xác nhận đúng nội dung. Không sửa scorer để làm đẹp điểm.
- Sáu tool SQLite có validation, error dict, transaction, khóa xác nhận dùng một lần. request_id được host sinh ổn định theo preview, không do model đoán; retry trả đơn cũ.
- Chat UI và console đều mở session cho tool commerce. UI hiển thị pending action trước nút đồng ý/từ chối và lưu transcript đầy đủ có hash/version, che khóa/credential.
- Eval dùng fixture SQLite riêng, mặc định không gửi Telegram; unit/UI tests dùng mock/fake provider, tách biệt với live model run.
- Hướng dẫn một lệnh: [FINAL_RUNBOOK.md](../../docs/FINAL_RUNBOOK.md).

## 4. PHẦN B — Kết quả và bằng chứng

### B1. Version Evidence

Chi tiết giả thuyết, metric trước/sau, prompt_hash, tools_hash và file run nằm trong [version_log.csv](../../starter_v0/artifacts/version_log.csv). Mỗi run dưới đây đo đủ case, provider_error_cases=0. Base v0–v3 lần lượt 65%, 85%, 95%, 95%; version không tăng vẫn được giữ và phân tích.

| Version | Suite | PASS | Routing | Arguments | Run JSON |
|---|---|---:|---:|---:|---|
{table}

v4/v5 giữ cả lần có regression; v6 xác nhận rõ nội dung giúp group từ 8/10 lên 9/10. v7 giữ base 20/20, group strict vẫn 9/10. Lần group cuối đạt {group['summary']['passed_cases']}/10 sau sửa thiết kế G09: chỉ chấm topic/timeframe, không exact-match query đồng nghĩa. Đây là **thay đổi thiết kế eval**, không nhận là model tự cải thiện. Bản strict ở data/history/eval_group_v4_strict_query.json và log 9/10 vẫn giữ nguyên. Bộ group v3 gốc lưu tại data/history/eval_group_v3.json.

Artifact cuối: `{base['artifact_version']}`. Base cuối {base['summary']['passed_cases']}/20 và group cuối {group['summary']['passed_cases']}/10 đều là API run thật, không phải replay hay fake provider. Không quy đổi các tỷ lệ này thành điểm toàn bài /100.

### B2. Failure Analysis
{failure}

**Bổ sung sau tích hợp:** G02 của group v3 có gọi clarify(text), không phải trả lời thẳng. G09 dùng đúng timeframe=year, chỉ khác query “Tesla electric vehicles” so với “Tesla”; mô tả cũ về timeframe đã được sửa tại đây. PASS routing của hai case TV2 trong group v3 vẫn đi kèm session_required; G06 send PASS routing nhưng thiếu cấu hình Telegram. Không coi các PASS đó là bằng chứng CRUD/gửi thành công.

v4 từng gọi social_search với query rỗng khi thiếu account/topic; sửa bằng thứ tự quyết định trong v5. v5/v6 còn hỏi xác nhận lặp khi user đã xác nhận nguyên văn; v6 giải thích rõ ngữ cảnh user. Lỗi send nhận chuỗi false và wrapper request_id trùng được tái hiện rồi sửa, có regression test.

### B3. Team Eval Cases

Dataset hiện tại: [eval_group.json](../../starter_v0/data/eval_group.json), đúng 10 case, 5 single + 5 multi; route đủ 6 tool mới. Run tương ứng: {link(group_path)}. Fixtures PREVIEW-EVAL-001 và DEMO-EVAL-ORDER thuộc tài khoản demo, do host tạo; không phải mã model tự bịa.

| Case | Loại | Tool kỳ vọng | Kết quả | Mục tiêu |
|---|---|---|---|---|
{case_table}

Scorer chỉ đo tool calls/args; multi-turn đưa lượt trước vào ngữ cảnh rồi chấm lượt cuối. G09 kiểm tra time range; chủ đề query vẫn được đọc từ actual_tool_calls. Tool lookup còn lỗi thiếu Tavily key; hành vi API bên ngoài chưa được chứng minh chỉ bởi PASS routing. Send bị chặn theo execution_policy, không tính là Telegram thật.

### B4. Live Chat Evidence

Các transcript sau dùng model thật qua OpenRouter và tool thật/local. Input và thao tác widget được script hóa bằng AppTest để tái lập; không trình bày là kiểm thử thủ công bởi người ngoài nhóm. Header evidence_kind=live; test fake-provider được lưu vào thư mục tạm riêng, không trộn vào bằng chứng live.

| Kịch bản / lượt | User input | Tool | Kết quả | Transcript |
|---|---|---|---|---|
{chr(10).join(chat_rows)}

Script tái lập: [record_live_demo.py](../../starter_v0/scripts/record_live_demo.py). Transcript v0 cũ được giữ để đối chiếu, không đổi nhãn thành bản cuối. Kịch bản sửa hồ sơ ghi cả bước host approval và kết quả updated; kịch bản Telegram chưa gửi ra ngoài.

### B5a. Tool, unit test và UI

| Thành phần | Bằng chứng | Kết quả / giới hạn |
|---|---|---|
| 6 tool mới | tools/get_my_profile, update_profile, preview_order, place_order, get_order_status, cancel_order; mỗi folder có TOOL.md | Đọc/ghi SQLite giả; khóa xác nhận gắn session/action/payload |
| Unit test | [test_tv2_tools.py](../../starter_v0/tests/test_tv2_tools.py), [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py) | ≥3 test/tool mới; test TODO đã được thay bằng assertion thực |
| UI/CLI integration | [test_ui_integration.py](../../starter_v0/tests/test_ui_integration.py), [test_runtime_host.py](../../starter_v0/tests/test_runtime_host.py) | Session chat, đồng ý/từ chối, transaction, transcript và console approval |
| Kết quả toàn suite | [JUnit](../../starter_v0/analysis/pytest_final.xml), [final_check.json](../../starter_v0/analysis/final_check.json) | 155 passed + 16 subtests; 0 failed, 0 skipped; JUnit đếm 171 gồm subtests |
| UI | [app.py](../../starter_v0/app.py), Streamlit trong requirements | Localhost hoạt động; public link không mở theo lựa chọn người dùng |

Ví dụ lỗi eval không bắt nhưng unit test bắt: model có thể gửi confirmed dưới dạng chuỗi “false”; Python truthiness trước đây vẫn gửi. Regression test khẳng định mọi giá trị khác boolean True đều không gọi mạng. Wrapper nhận request_id thừa cũng phải trả error dict, không raise TypeError.

### B5. Bonus Evidence

- Đề nghị xét bonus ≥4 tool mới: có 6 tool, registration, TOOL.md, ≥3 test/tool và eval route cả 6, đều PASS trong run cuối. Không tự cộng 3 điểm vào điểm chính.
- Đề nghị xét Test challenge: toàn suite 0 skipped và có regression cho bug send của tool có sẵn. Không tự cộng 1 điểm vào điểm chính.
- Telegram thật: không thực hiện; không có status sent thật để nhận bonus.

### B7. Small Local Model

Không thực hiện bonus này; không có hai model local hoặc hai vòng tối ưu local. Không dùng fake provider để giả bằng chứng model local.

## 5. Khó khăn và cách xử lý

1. Key đặt ở .env gốc repo thay vì starter_v0: env_loader đã hỗ trợ cả hai, file starter override root, DAY03_ENV_FILE có ưu tiên cao nhất. Không log giá trị key.
2. Tavily/Firecrawl/RapidAPI chưa có key: giữ error dict rõ ràng và ghi giới hạn; không giả kết quả tìm kiếm. Provider OpenRouter hoạt động và các run model đều có log thật.
3. Windows sandbox chặn tempfile: chạy kiểm tra với quyền thực thi phù hợp, SQLite tạm nằm trong runtime và được dọn; không bỏ validation để test xanh.
4. Prompt mơ hồ và eval query quá cứng: giữ cả log FAIL, sửa thứ tự rule bằng giả thuyết, rồi sửa đúng phạm vi expectation G09 có giải thích và archive.
5. Bật tunnel public đã bị auto-review chặn; sau đó người dùng chọn chỉ localhost. Không thử đường vòng và không ghi URL public giả.
6. Không xác nhận được deadline/gia hạn hoặc mốc Phần A trước showdown từ repo; báo cáo ghi ngày bổ sung thật, không sửa ngày commit.

## 6. Tổng hợp đóng góp

- TV1 Võ Hồng Lương: baseline, v1–v3, declaration/prompt và tích hợp registry.
- TV2 Chu Quang Linh: 6 tool/SQLite/test và bàn giao; đợt hoàn thiện dùng Codex sửa runtime, test, báo cáo và đo lại trên yêu cầu của người dùng.
- TV3 Hồ Anh Tú: bộ group v3, run group và phân tích B2/B3; bộ group bổ sung phủ 6 tool được điều chỉnh trong đợt hoàn thiện có lưu lịch sử.
- TV4 Nguyễn Minh Quân: UI/requirements/transcript ban đầu; dùng Codex. Đợt hoàn thiện bổ sung session chat, host approval và ghi transcript.
- Chi tiết/bằng chứng: [TEAM.md](../../TEAM.md) và 4 báo cáo cá nhân. Không tạo trải nghiệm tự đánh giá, commit hay kết quả giả cho cá nhân khác.

## 7. B6 — Reflection và giới hạn

Prompt/declaration điều khiển model lựa chọn hành động; backend phải tự chặn input sai và thao tác chưa được phê duyệt. Test fake-provider chứng minh code nhưng không thay thế eval thật. Eval routing 100% không chứng minh Tavily/Firecrawl/X đang hoạt động, không chứng minh Telegram đã gửi và không tự quy thành 100 điểm lab.

Chỉ một lần đo mỗi trạng thái không chứng minh tính ổn định thống kê; OpenRouter/model có thể dao động ở lần chạy khác. G09 cuối đạt nhờ expectation được sửa đúng mục tiêu đo, không được mô tả thành cải thiện model. Base gốc và scorer không bị sửa để tăng điểm.

SQLite chỉ dùng dữ liệu giả và host chọn tài khoản demo; chưa có authentication production, thanh toán, kiểm chứng tải hoặc concurrency nhiều người dùng thật. Localhost không dùng được từ máy khác. Những giới hạn này được nêu công khai thay vì đánh dấu hoàn thành giả.

## 8. Tài liệu tham khảo

- [README lab](../../README.md), [Rubric](../../RUBRIC.md), [Rules](../../RULES.md), [Submission](../../SUBMISSION.md).
- [Tool folder contract](../../starter_v0/tools/README.md), mẫu fixture/test có sẵn trong starter.
- [Bàn giao TV2](../../docs/TV2_LINH_HANDOFF.md), [ghi chú tích hợp TV1](../../docs/TV1_INTEGRATION_NOTES.md), [runbook cuối](../../docs/FINAL_RUNBOOK.md).
- Các số liệu và kết luận lấy từ run/transcript/JUnit trong repo; không dùng ảnh hoặc cảm nhận thay cho log.
'''
    GROUP.write_text(report,encoding='utf-8')
    (ROOT/'artifacts/history/v7_system_prompt.md').write_bytes((ROOT/'artifacts/system_prompt.md').read_bytes())
    (ROOT/'artifacts/history/v7_tools.yaml').write_bytes((ROOT/'artifacts/tools.yaml').read_bytes())
    manifest={'version':'v7-final','base_run':str(base_path.relative_to(ROOT)),'group_run':str(group_path.relative_to(ROOT)),
              'base_summary':base['summary'],'group_summary':group['summary'],
              'live_transcripts':summary,'offline_check':check,
              'limitations':['localhost_only_by_user_choice','Tavily/Firecrawl/RapidAPI keys not configured','No real Telegram/local-model bonus']}
    (ROOT/'analysis/submission_evidence.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Report, version log and submission evidence rebuilt from real files.')


if __name__=='__main__':main()
