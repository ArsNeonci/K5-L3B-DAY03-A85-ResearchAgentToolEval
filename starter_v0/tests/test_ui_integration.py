"""Offline UI tests: real SQLite, real widgets, fake provider, no model calls."""
import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest
from providers.base import ModelResponse, ToolCall

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture
def ui_env(tmp_path,monkeypatch):
    monkeypatch.setenv('DAY03_TRANSCRIPTS_DIR',str(tmp_path/'transcripts'))
    monkeypatch.setenv('DAY03_ENV_FILE',str(tmp_path/'no-env'))
    monkeypatch.setenv('DAY03_PROVIDER','openrouter')
    return tmp_path/'transcripts'


def click(at,label):
    next(x for x in at.button if x.label==label).click().run()
    assert not at.exception


def commerce_result(at):
    return at.session_state['commerce_event']['result']


def test_ui_commerce_full_lifecycle_and_rejection(ui_env):
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
    assert not at.exception
    at.radio[0].set_value('Hồ sơ & đơn hàng').run()
    click(at,'Xem hồ sơ')
    assert commerce_result(at)['profile']['shipping_address']=='Địa chỉ demo A'
    at.selectbox[0].set_value('update_profile').run()
    at.selectbox[1].set_value('shipping_address')
    at.text_input[0].set_value('Địa chỉ test UI')
    click(at,'Cập nhật hồ sơ')
    assert commerce_result(at)['status']=='needs_confirmation'
    click(at,'Từ chối')
    assert commerce_result(at)['status']=='rejected'
    at.selectbox[0].set_value('get_my_profile').run()
    click(at,'Xem hồ sơ')
    assert commerce_result(at)['profile']['shipping_address']=='Địa chỉ demo A'
    at.selectbox[0].set_value('preview_order').run()
    at.number_input[0].set_value(2)
    click(at,'Xem trước đơn')
    assert commerce_result(at)['preview']['total_vnd']==60000
    at.selectbox[0].set_value('place_order').run()
    click(at,'Tạo đơn từ bản xem trước')
    assert commerce_result(at)['status']=='needs_confirmation'
    click(at,'Đồng ý thực hiện')
    assert commerce_result(at)['status']=='created'
    at.selectbox[0].set_value('get_order_status').run()
    click(at,'Xem trạng thái đơn')
    assert commerce_result(at)['order']['status']=='pending'
    at.selectbox[0].set_value('cancel_order').run()
    click(at,'Hủy đơn')
    click(at,'Đồng ý thực hiện')
    assert commerce_result(at)['status']=='cancelled'
    assert list(ui_env.glob('*.transcript.json'))


def test_ui_chat_session_approval_history_and_sanitized_transcript(ui_env,monkeypatch):
    class FakeProvider:
        is_test_provider=True
        default_model='scripted-offline-test'
        def __init__(self):self.calls=0
        def complete(self,*args,**kwargs):
            self.calls+=1
            if self.calls==1:
                return ModelResponse(text=None,tool_calls=[ToolCall('update_profile',{'field':'shipping_address','new_value':'Địa chỉ test chat'})])
            if self.calls==2:
                return ModelResponse(text=None,tool_calls=[ToolCall('get_my_profile',{})])
            return ModelResponse(text='Kết quả kiểm tra offline.',tool_calls=[])
    provider=FakeProvider()
    monkeypatch.setattr('providers.make_provider',lambda name:provider)
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
    at.chat_input[0].set_value('Đổi địa chỉ giao hàng').run()
    assert not at.exception
    pending=at.session_state['chat_pending_action']
    assert pending['result']['status']=='needs_confirmation'
    click(at,'Đồng ý thực hiện')
    assert at.session_state['turns'][-1]['tool_events'][0]['result']['status']=='updated'
    at.chat_input[0].set_value('Xem địa chỉ hiện tại').run()
    assert not at.exception
    event=at.session_state['turns'][-1]['tool_events'][0]
    assert event['result']['profile']['shipping_address']=='Địa chỉ test chat'
    file=next(ui_env.glob('*.transcript.json'))
    transcript=json.loads(file.read_text(encoding='utf-8'))
    assert transcript['evidence_kind']=='offline_test'
    assert len(transcript['turns'])==3
    assert transcript['prompt_hash'] and transcript['tools_hash']
    assert 'confirmation_key' not in file.read_text(encoding='utf-8')


def test_transcript_writer_redacts_secrets_and_capabilities(tmp_path,monkeypatch):
    from runtime_support import atomic_json
    monkeypatch.setenv('OPENROUTER_API_KEY','dummy-private-key')
    path=tmp_path/'transcript.json'
    atomic_json(path,{'args':{'confirmation_key':'private-capability'},'message':'dummy-private-key'})
    text=path.read_text(encoding='utf-8')
    assert 'dummy-private-key' not in text and 'private-capability' not in text
    assert json.loads(text)['args']['confirmation_key']=='[redacted]'
