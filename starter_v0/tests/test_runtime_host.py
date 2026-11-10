from pathlib import Path
import json

from commerce_demo import demoSession, initializeDemoDatabase
from tools.update_profile.tool import updateProfile
from tools.get_my_profile.tool import getMyProfile
from chat import approve_commerce_pending


def test_console_approval_requires_yes_and_records_no_capability(tmp_path,monkeypatch):
    path=tmp_path/'db.sqlite3'
    initializeDemoDatabase(path)
    with demoSession(path):
        pending=updateProfile('display_name','Tên kiểm tra console')
        result={'status':'waiting_for_user','tool_events':[{'tool':'update_profile','args':{},'result':pending}]}
        monkeypatch.setattr('builtins.input',lambda prompt:'NO')
        assert approve_commerce_pending(result)['status']=='rejected'
        assert getMyProfile()['profile']['display_name']=='Khách demo An'
        monkeypatch.setattr('builtins.input',lambda prompt:'YES')
        approved=approve_commerce_pending(result)
        assert approved['status']=='host_action'
        assert getMyProfile()['profile']['display_name']=='Tên kiểm tra console'
        assert 'confirmation_key' not in json.dumps(approved)


def test_env_loader_accepts_root_and_starter_specific_override(tmp_path,monkeypatch):
    from env_loader import load_lab_env
    root=tmp_path/'repo'; starter=root/'starter_v0'; starter.mkdir(parents=True)
    (root/'.env').write_text('AUDIT_SETTING=root\n',encoding='utf-8')
    (starter/'.env').write_text('AUDIT_SETTING=starter\n',encoding='utf-8')
    monkeypatch.delenv('DAY03_ENV_FILE',raising=False)
    monkeypatch.setenv('AUDIT_SETTING','before')
    load_lab_env(starter)
    import os
    assert os.environ['AUDIT_SETTING']=='starter'


def test_cli_eval_runs_with_fake_provider_and_marks_actions_disabled(tmp_path,monkeypatch):
    import run_eval
    from providers.base import ModelResponse,ToolCall
    class Provider:
        default_model='test-only'
        def complete(self,*args,**kwargs):
            return ModelResponse(text=None,tool_calls=[ToolCall('get_my_profile',{})])
    cases=tmp_path/'cases.json'
    cases.write_text(json.dumps({'cases':[{'id':'test','phase':'B','query':'x','failure_type':'wrong_tool',
        'expect':{'tool_calls':[{'name':'get_my_profile','args':{}}]},'metadata':{'what_it_tests':'test'}}]}))
    monkeypatch.setattr('sys.argv',['run_eval.py','--provider','openrouter','--version','offline-test',
                                    '--eval-cases',str(cases),'--runs-dir',str(tmp_path/'runs')])
    monkeypatch.setattr(run_eval,'make_provider',lambda name:Provider())
    run_eval.main()
    run=json.loads(next((tmp_path/'runs').glob('*.json')).read_text(encoding='utf-8'))
    assert run['summary']['passed_cases']==1
    assert run['results'][0]['tool_results'][0]['result']['status']=='ok'
    assert run['execution_policy']['external_actions_enabled'] is False
