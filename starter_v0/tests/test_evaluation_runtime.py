from pathlib import Path
from tools import TOOL_FUNCTIONS
from evaluation_runtime import evaluation_runtime
from run_eval import evaluate_phase_b, load_cases
import json
import hashlib


def test_eval_fixture_supports_profile_preview_order_without_session_errors():
    original=TOOL_FUNCTIONS['send']
    with evaluation_runtime():
        assert TOOL_FUNCTIONS['get_my_profile']()['status']=='ok'
        assert TOOL_FUNCTIONS['get_order_status']('DEMO-EVAL-ORDER')['order']['status']=='pending'
        assert TOOL_FUNCTIONS['place_order']('PREVIEW-EVAL-001')['status']=='needs_confirmation'
        assert TOOL_FUNCTIONS['send']('demo',True)['error']=='action_disabled_in_eval'
    assert TOOL_FUNCTIONS['send'] is original


def test_fixed_base_and_extension_have_not_changed_from_starter():
    root=Path(__file__).resolve().parents[1]
    hashes={'eval_base.json':'97225d4c4ded7da5dd6d1dc397ba88812ca001d1f60a35c63249a4aec3442e85',
            'eval_research_extension.json':'e977d052f9db30af64fde5c75b8233814da88670fc1de89ca2b30d05c6c6a8f2'}
    for name,expected in hashes.items():
        data=json.loads((root/'data'/name).read_text(encoding='utf-8'))
        actual=hashlib.sha256(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert actual==expected


def test_original_base_scorer_detects_wrong_confirmation_and_passes_correct_one():
    root=Path(__file__).resolve().parents[1]
    case=next(c for c in load_cases(root/'data/eval_base.json','B') if c['id']=='R12_confirm_before_send')
    assert not evaluate_phase_b(case,[{'name':'clarify','args':{'response_type':'text'}}],None)['passed']
    assert evaluate_phase_b(case,[{'name':'clarify','args':{'response_type':'yes_no'}}],None)['passed']
