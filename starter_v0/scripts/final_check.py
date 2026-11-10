"""One-command submission checks. Offline tests are never labeled live evals."""
from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from env_loader import load_lab_env
from tools import load_tool_declarations
from run_eval import load_cases, validate_expected_tools
from runtime_support import atomic_json
from runtime_support import VERSION


def run(*args):
    return subprocess.call([sys.executable,*args],cwd=ROOT)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='Also preflight and run real provider base/group evals (API credits).')
    args=parser.parse_args()
    load_lab_env(ROOT)
    names=['OPENROUTER_API_KEY','TAVILY_API_KEY','FIRECRAWL_API_KEY','RAPIDAPI_KEY']
    configuration={name:bool(os.getenv(name)) for name in names}
    declarations=load_tool_declarations(ROOT/'artifacts/tools.yaml')
    for suite in ['base','group','research_extension']:
        file=ROOT/'data'/f'eval_{suite}.json'
        cases=load_cases(file,'B')
        validate_expected_tools(cases,declarations,file)
        assert len({x['id'] for x in cases})==len(cases)
        if suite=='group':
            assert len(cases)==10 and sum('query'in x for x in cases)==5 and sum('turns'in x for x in cases)==5
            routed={t['name'] for x in cases for t in x['expect'].get('tool_calls',[])}
            assert {'get_my_profile','update_profile','preview_order','place_order','get_order_status','cancel_order'} <= routed
    reports=['2A202603839_VoHongLuong.md','2A202603809_ChuQuangLinh.md','2A202603811_HoAnhTu.md','2A202603794_NguyenMinhQuan.md']
    assert all((ROOT.parent/'report/team'/p).is_file() for p in reports)
    code=run('-m','pytest','-q','--junitxml=analysis/pytest_final.xml')
    junit=ET.parse(ROOT/'analysis/pytest_final.xml').getroot()
    test_counts={name:sum(int(s.get(name,0)) for s in junit.iter('testsuite'))
                 for name in ['tests','failures','errors','skipped']}
    if any(test_counts[name] for name in ['failures','errors','skipped']):code=1
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'pytest_exit_code':code,
            'test_counts':test_counts,
            'configuration_present':configuration,'live_requested':args.live,'live_runs':[],
            'note':'No numerical /100 grade is inferred from pytest or case accuracy.'}
    if code==0 and args.live:
        if not configuration['OPENROUTER_API_KEY']:
            result['live_status']='blocked_missing_provider_key'
            code=2
        elif run('scripts/preflight_provider.py','--provider','openrouter')!=0:
            result['live_status']='provider_preflight_failed'
            code=2
        else:
            for suite in ['base','group']:
                before=set((ROOT/'runs').glob('*.json'))
                rc=run('run_eval.py','--provider','openrouter','--version',VERSION,'--suite',suite,
                       '--eval-cases',f'data/eval_{suite}.json')
                paths=set((ROOT/'runs').glob('*.json'))-before
                for path in paths:
                    payload=json.loads(path.read_text(encoding='utf-8'))
                    result['live_runs'].append({'file':str(path.relative_to(ROOT)),'summary':payload['summary']})
                    measured=payload['summary']
                    if measured['provider_error_cases'] or measured['measured_cases']!=measured['total_cases']:
                        code=2
                    elif measured['passed_cases']!=measured['total_cases']:
                        code=max(code,1)
                if rc:code=rc
            result['live_status']='completed_see_measured_cases_and_tool_errors'
    elif not args.live:
        result['live_status']='not_requested'
    atomic_json(ROOT/'analysis/final_check.json',result)
    if args.live and result['live_runs']:
        report_code=run('scripts/build_evidence_report.py')
        if report_code:code=report_code
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(code)


if __name__=='__main__':main()
