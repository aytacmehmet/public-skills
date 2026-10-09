# SPDX-License-Identifier: GPL-3.0-only
"""Managed CLI/review/physical-input regression; all reader answers are synthetic."""
import copy
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout,chdir
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bv2 as b
import delivery as d
import profile_runtime as runtime
import review_contract
import work_profiles as w
import workspace_lock
import dispatch_registry
from fixture_v4 import valid


class ProfileIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.doc=valid(self.root)
        self.control=self.doc['delivery']['control']
        self.control['eval_rounds']=[]
        self.control['eval_requests']=[]
        self.source=self.root/'fixture-workspace.toon'

    def select(self,profile='lite'):
        assessment={name:0 for name in w.FACTORS}
        caps={'host':'manual','reader_isolation':True,'vision':True,'child_limit':3,
              'coordinator_file':str(self.root/'.byw-dispatch.json')}
        capacity={'status':'PASS','context_limit':1000000,'packet_tokens':200000,
                  'output_reserve':50000,'image_tokens':4096,
                  'evidence':'SYNTHETIC_CONSERVATIVE_ESTIMATE_NOT_PROVIDER_PROOF'}
        assessment,caps,capacity=runtime.bind_inputs(self.doc,assessment,caps,capacity,self.root)
        w.choose(self.doc,profile,assessment,caps,capacity,
                 {'confirmed':True,'receipt':'SYNTHETIC_USER_SELECTION'})

    def answer(self,packet):
        spec=self.doc['delivery']['spec']
        row={'reader_id':packet['reader_id'],'context_id':packet['context_id'],
             'request_sha256':packet['request_sha256'],'isolated':True,'saw_other_results':False,
             'status':'COMPLETED','covered_requirements':[r['id'] for r in spec['requirements']],
             'questions':[{'requirement_ref':r['id'],'question':'Stated functional behavior?',
                          'pointer':'/requirements/'+str(i)+'/statement','answer':r['statement']}
                         for i,r in enumerate(spec['requirements'])],
             'expected_results':{r['id']:r['expected'] for r in spec['test_cases']},
             'visual_matches':[{'media_ref':r['media_ref'],'ui_element_ref':r['ui_element_ref'],
                               'method':'PNG_INSPECTION','label_match':True,'layout_match':True}
                              for r in spec['ui_callouts']],
             'plan_completed':True,'plan_decisions':[{'decision':'Preserve stated object.','pointer':'/objects/0/name'},
                         {'decision':'Preserve stated constraint.','pointer':'/architecture/constraints/0/statement'}],
             'findings':[],'execution_evidence':'SYNTHETIC_NOT_REAL_REVIEW'}
        row['response_sha256']=review_contract.response_sha(row)
        return row

    def complete(self,packet):
        task=packet['work_task']['task_id']
        attempt=w.begin(self.doc,task,'reviewer',packet['request_sha256'],packet['context_id'])
        row=self.answer(packet)
        w.finish(self.doc,task,'COMPLETED',packet['request_sha256'],packet['context_id'],
                 {'response_sha256':row['response_sha256'],'receipt':row['execution_evidence']},
                 attempt_id=attempt['attempt_id'])
        return row

    def test_lite_two_clean_rounds_keep_six_dispatches_and_neutral_package(self):
        self.select()
        for n in (1,2):
            packets=d.eval_request(self.doc,n,self.root)
            self.assertEqual(w.status(self.doc)['usage']['total_attempts'],3*(n-1))
            answers=[self.complete(packet) for packet in packets]
            d.record_round(self.doc,{'revision_sha256':d.revision(self.doc['delivery']['spec']),
                                    'readers':answers,'new_open_count':0})
        self.assertEqual(d.evaluate(self.doc)['decision'],'DELIVERABLE')
        self.assertEqual(w.status(self.doc)['usage']['review_attempts'],6)
        result=d.package(self.doc,self.root/'out',self.root,include_excel=False)
        self.assertIn('path',result)
        import zipfile
        with zipfile.ZipFile(result['path']) as archive:
            self.assertFalse(any('work-profile' in name for name in archive.namelist()))
            text=archive.read('fixture-talep-belirtim.toon').decode()
            self.assertNotIn('work_profile',text)
            self.assertNotIn('gpt-',text)

    def test_missing_counted_dispatch_cannot_record_clean_round(self):
        self.select()
        packets=d.eval_request(self.doc,1,self.root)
        with self.assertRaisesRegex(b.Invalid,'no counted dispatch'):
            d.record_round(self.doc,{'revision_sha256':d.revision(self.doc['delivery']['spec']),
                                    'readers':[self.answer(p) for p in packets],'new_open_count':0})
        self.assertEqual(self.control['eval_rounds'],[])

    def test_preparation_receipt_cannot_replace_final_reader(self):
        self.select('ultra')
        packet=d.eval_request(self.doc,1,self.root)[0]
        row=self.answer(packet)
        task=packet['work_task']['task_id']
        attempt=w.begin(self.doc,task,'prep',packet['request_sha256'],packet['context_id'])
        w.finish(self.doc,task,'PASS',packet['request_sha256'],packet['context_id'],
                 {'response_sha256':row['response_sha256'],'receipt':'SYNTHETIC_PREPARATION'},
                 attempt_id=attempt['attempt_id'])
        with self.assertRaisesRegex(b.Invalid,'dispatch receipt'):
            d.record_round(self.doc,{'revision_sha256':d.revision(self.doc['delivery']['spec']),
                                    'readers':[row],'new_open_count':0})

    def test_new_profile_dispatch_metadata_is_rejected_in_public_spec(self):
        for field in ('work_profile','coordinatorFile','model_suggestion','byw_task','tool_use_id','native_dispatch','review_role','blindness_sha256'):
            value=copy.deepcopy(self.doc['delivery']['spec'])
            value['naming_rules'][field]='private operational metadata'
            self.assertIn('C5_PRIVATE',{row['code'] for row in d.privacy(value)})

    def test_managed_missing_request_reports_blocked_without_crashing(self):
        self.select()
        packets=d.eval_request(self.doc,1,self.root)
        answers=[self.complete(packet) for packet in packets]
        d.record_round(self.doc,{'revision_sha256':d.revision(self.doc['delivery']['spec']),
                                'readers':answers,'new_open_count':0})
        self.control['eval_requests']=[]
        report=d.evaluate(self.doc)
        self.assertEqual(report['decision'],'BLOCKED')
        self.assertIn('F2_WORK_DISPATCH',{row['code'] for row in report['issues']})

    def test_failed_reader_can_retry_fresh_context_without_refunding(self):
        self.select()
        first=d.eval_request(self.doc,1,self.root)[0]
        task=first['work_task']['task_id']
        attempt=w.begin(self.doc,task,'reviewer',first['request_sha256'],first['context_id'])
        w.finish(self.doc,task,'UNKNOWN',first['request_sha256'],first['context_id'],
                 {'receipt':'SYNTHETIC_TIMEOUT'},attempt_id=attempt['attempt_id'])
        fresh=d.eval_request(self.doc,1,self.root)
        self.assertEqual(fresh[0]['work_task']['task_id'],task)
        self.assertNotEqual(fresh[0]['context_id'],first['context_id'])
        answers=[self.complete(packet) for packet in fresh]
        d.record_round(self.doc,{'revision_sha256':d.revision(self.doc['delivery']['spec']),
                                'readers':answers,'new_open_count':0})
        self.assertEqual(w.status(self.doc)['usage']['review_attempts'],4)
        self.assertEqual(w.status(self.doc)['unresolved_attempts'],[])

    def test_asset_drift_blocks_review_and_package_without_hook(self):
        self.select()
        asset=self.root/self.control['assets'][0]['path']
        asset.write_bytes(asset.read_bytes()+b'changed')
        with self.assertRaisesRegex(b.Invalid,'snapshot changed'):
            d.eval_request(self.doc,1,self.root)
        with self.assertRaises(b.Invalid):d.package(self.doc,self.root/'out',self.root,False)

    def test_packet_capacity_includes_envelope_and_reference_volume(self):
        spec=self.doc['delivery']['spec']
        self.assertGreater(runtime.packet_byte_bound(self.doc,self.root),len(b.canonical(spec)))
        for n in range(21):self.control['assets'].append({'path':'ref-'+str(n)+'.txt','sha256':'a'*64})
        self.assertEqual(runtime.volume(self.doc)['assets'],22)
        self.assertEqual(w.recommend({**{f:0 for f in w.FACTORS},'counts':runtime.volume(self.doc)})['recommended'],'pro')

    def test_capacity_arithmetic_rejects_underbound_and_bool(self):
        args={'status':'PASS','context_limit':100000,'packet_tokens':100,'output_reserve':5000,
              'image_tokens':500,'evidence':'SYNTHETIC'}
        caps={'vision':True}
        with self.assertRaisesRegex(b.Invalid,'complete-packet bound'):
            runtime.bind_inputs(self.doc,{},caps,args,self.root)
        args['packet_tokens']=True
        with self.assertRaisesRegex(b.Invalid,'positive'):
            runtime.bind_inputs(self.doc,{},caps,args,self.root)

    def test_ancestor_patch_cannot_remove_episode_and_failure_is_atomic(self):
        self.select('pro')
        b.save(self.doc,self.source)
        before=self.source.read_bytes()
        for pointer,value in [('/delivery/control',{}),('/delivery',None)]:
            with self.assertRaisesRegex(b.Invalid,'episode'):
                with redirect_stdout(io.StringIO()):
                    b.main(['patch',str(self.source),'--path',pointer,'--value',json.dumps(value)])
            self.assertEqual(self.source.read_bytes(),before)
        self.assertFalse(self.source.with_name(self.source.name+'.byw.lock').exists())

    def test_new_cli_release_init_requires_explicit_selection(self):
        self.doc['delivery']=None
        b.save(self.doc,self.source)
        with redirect_stdout(io.StringIO()):b.main(['release-init',str(self.source)])
        self.assertTrue(b.load(self.source)['delivery']['control']['work_profile_required'])

    def test_writer_lock_never_removes_other_owner(self):
        self.source.write_text('fixture')
        lock=self.source.with_name(self.source.name+'.byw.lock')
        with workspace_lock.held(self.source):
            before=lock.read_bytes()
            with self.assertRaisesRegex(b.Invalid,'writer lock'):
                with workspace_lock.held(self.source,timeout=0):pass
            self.assertEqual(lock.read_bytes(),before)
        self.assertFalse(lock.exists())

    def test_shared_registry_hard_limit_across_workspaces(self):
        self.select('ultra')
        doc2=copy.deepcopy(self.doc)
        rows=[]
        for n in range(3):
            attempt=w.begin(self.doc,'prep:'+str(n),'prep','a'*64,'context'+str(n))
            dispatch_registry.reserve(self.doc,self.source,attempt)
            rows.append(attempt)
        blocked=w.begin(doc2,'prep:other','prep','b'*64,'other')
        with self.assertRaisesRegex(b.Invalid,'no free child'):
            dispatch_registry.reserve(doc2,self.root/'second.toon',blocked)
        first=rows[0]
        terminal=w.finish(self.doc,first['task_id'],'FAIL',first['input_sha256'],first['context_id'],
                          {'receipt':'SYNTHETIC_FAIL'},attempt_id=first['attempt_id'])
        dispatch_registry.finish(self.doc,self.source,terminal)
        dispatch_registry.reserve(doc2,self.root/'second.toon',blocked)
        registry=json.loads((self.root/'.byw-dispatch.json').read_text())
        self.assertEqual(sum(r['status']=='RUNNING' for r in registry['rows']),3)

    def test_native_call_claim_is_idempotent_and_rejects_reservation_replay(self):
        self.select('plus')
        attempt=w.begin(self.doc,'lookup','prep','a'*64,'lookup-context')
        dispatch_registry.reserve(self.doc,self.source,attempt)
        dispatch_registry.claim_native_dispatch(self.doc,self.source,attempt,'codex','native-1')
        before=(self.root/'.byw-dispatch.json').read_bytes()
        dispatch_registry.claim_native_dispatch(self.doc,self.source,attempt,'codex','native-1')
        self.assertEqual(before,(self.root/'.byw-dispatch.json').read_bytes())
        with self.assertRaisesRegex(b.Invalid,'different native call'):
            dispatch_registry.claim_native_dispatch(self.doc,self.source,attempt,'codex','native-2')
        self.assertEqual(w.status(self.doc)['usage']['preparation_attempts'],1)

    def test_shared_registry_concurrent_cold_start_never_oversubscribes(self):
        from concurrent.futures import ThreadPoolExecutor
        self.select('ultra')
        def dispatch(n):
            attempt={'task_id':'prep:'+str(n),'attempt_id':str(n),'status':'RUNNING'}
            try:
                dispatch_registry.reserve(self.doc,self.root/('workspace-'+str(n)+'.toon'),attempt)
                return True
            except b.Invalid:return False
        with ThreadPoolExecutor(max_workers=8) as pool:
            outcomes=list(pool.map(dispatch,range(8)))
        self.assertEqual(sum(outcomes),3)
        registry=json.loads((self.root/'.byw-dispatch.json').read_text())
        self.assertEqual(sum(row['status']=='RUNNING' for row in registry['rows']),3)

    def test_cli_catalog_works_from_foreign_cwd_without_write(self):
        output=io.StringIO()
        before=set(self.root.iterdir())
        with chdir(self.root),redirect_stdout(output):b.main(['work-profiles','catalog'])
        self.assertEqual(len(json.loads(output.getvalue())['profiles']),5)
        self.assertEqual(before,set(self.root.iterdir()))


if __name__=='__main__':unittest.main()
