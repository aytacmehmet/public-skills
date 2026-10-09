# SPDX-License-Identifier: GPL-3.0-only
"""One final qualification entry; focused checks during edits, no automatic LLM runs."""
import argparse
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
IMPACT={
    'work_profiles.py':('test_work_profiles','test_profile_integration','test_profile_hooks','test_coordination_limits'),
    'dispatch_registry.py':('test_profile_integration','test_profile_hooks','test_coordination_limits'),
    'profile_runtime.py':('test_work_profiles','test_profile_integration','test_profile_hooks','test_coordination_limits'),
    'profile_hooks.py':('test_profile_hooks',),
    'workspace_lock.py':('test_profile_integration','test_profile_hooks','test_coordination_limits','test_workspace_paths'),
    'source_pool.py':('test_source_pool','test_review_safety','test_profile_integration'),
    'review_contract.py':('test_release','test_profile_integration','test_review_safety','test_source_pool'),
    'preflight.py':('test_effectiveness','test_handoff3','test_profile_integration','test_review_safety','test_source_pool'),
}


def selected(changed,final=False):
    available={path.stem for path in (ROOT/'tests').glob('test_*.py')}
    if final or not changed:return sorted(available)
    modules=set()
    for raw in changed:
        path=Path(raw)
        if path.is_absolute() or '..' in path.parts:
            raise ValueError('Changed paths must be relative to the plugin')
        if path.parts[:1]==('tests',) and path.stem in available:
            modules.add(path.stem)
        elif path.name in IMPACT:modules.update(IMPACT[path.name])
        elif path.parts[:1]==('hooks',) or path.parts[:1]==('agents',):modules.add('test_profile_hooks')
        elif path.suffix=='.md' or path.parts[:1] in (('.claude-plugin',),('.codex-plugin',),('metadata',)):
            continue
        else:return sorted(available)
    return sorted(modules)


def needs_package(changed,final=False):
    if final or not changed:return True
    return any(Path(path).parts[:1] in (('skills',),('metadata',),('.claude-plugin',),('.codex-plugin',),('vendor',))
               or Path(path).name=='requirements.txt' for path in changed)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--changed',action='append',default=[])
    parser.add_argument('--final',action='store_true')
    parser.add_argument('--evidence',help='Explicit JSON output outside the plugin')
    args=parser.parse_args()
    target=Path(args.evidence).resolve() if args.evidence else None
    if target and target.is_relative_to(ROOT):
        parser.error('Evidence belongs outside the plugin')
    start=time.perf_counter()
    modules=selected(args.changed,args.final)
    if needs_package(args.changed,args.final):
        package=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'skills/belirtim-yazmani/scripts/check_package.py')],capture_output=True,text=True)
        package_result={'status':'PASS' if package.returncode==0 else 'FAIL','exit_code':package.returncode,
                        'output':(package.stdout+package.stderr).strip()}
    else:
        package_result={'status':'NOT_RUN','reason':'Focused runtime/test change; package interface is outside this check scope'}
    sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
        suite=unittest.defaultTestLoader.loadTestsFromNames(modules)
        result=unittest.TextTestRunner(stream=stream,verbosity=0).run(suite)
    value={'mode':'FINAL' if args.final else 'FOCUSED','modules':modules,
           'tests':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
           'failures':len(result.failures),'errors':len(result.errors),
           'skipped':[{'test':str(test),'reason':reason} for test,reason in result.skipped],
           'package':package_result,
           'seconds':round(time.perf_counter()-start,3),
           'status':'PASS' if result.wasSuccessful() and package_result['status']!='FAIL' else 'FAIL',
           'provider_evaluation':'NOT_RUN','scope':'Deterministic synthetic qualification; not actual handoff-reader execution'}
    if target:
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(value,ensure_ascii=False))
    if value['status']!='PASS':
        print(stream.getvalue()[-12000:])
        return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())
