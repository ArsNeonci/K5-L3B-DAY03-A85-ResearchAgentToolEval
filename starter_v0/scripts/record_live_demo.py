"""Scripted user interactions in the real UI with a REAL model, not fake output.

No Telegram delivery: app's default no-send policy remains active.
"""
from pathlib import Path
import json
import os
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from env_loader import load_lab_env
from runtime_support import atomic_json
from streamlit.testing.v1 import AppTest


def main():
    load_lab_env(ROOT)
    if not os.getenv('OPENROUTER_API_KEY'):raise SystemExit('Configure OPENROUTER_API_KEY first.')
    os.environ['DAY03_TRANSCRIPTS_DIR']=str(ROOT/'transcripts')
    summary=[]
    scenarios=[
        ('research_policy',['Tìm quy định công ty về trích dẫn nguồn nghiên cứu và tóm tắt các điểm chính, dẫn nguồn nội bộ.']),
        ('clarify_then_profile',['Đổi địa chỉ giao hàng của tôi.','Đổi sang Địa chỉ demo B.']),
        ('send_confirmation',['Gửi lên Telegram đúng nội dung: Bản tin nghiên cứu demo A85.',
                              'Tôi xác nhận gửi nguyên văn: Bản tin nghiên cứu demo A85.']),
    ]
    for name,messages in scenarios:
        at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=90).run()
        for text in messages:
            at.chat_input[0].set_value(text).run(timeout=90)
            if at.exception:raise RuntimeError('Streamlit exception: '+at.exception[0].message)
        if name=='clarify_then_profile' and 'chat_pending_action' in at.session_state:
            next(x for x in at.button if x.label=='Đồng ý thực hiện').click().run(timeout=90)
        transcript=at.session_state['ui_transcript']
        row={'scenario':name,'transcript':f"transcripts/{transcript['transcript_id']}.transcript.json",
             'evidence_kind':'live','user_input_source':'scripted_AppTest_widgets_not_manual_user',
             'turns':len(transcript['turns']),
             'statuses':[x['status'] for x in transcript['turns']],
             'tools':[e['tool'] for x in transcript['turns'] for e in x.get('tool_events',[])]}
        summary.append(row)
        print(json.dumps(row,ensure_ascii=False),flush=True)
        atomic_json(ROOT/'analysis/live_demo_summary.json',summary)


if __name__=='__main__':main()
