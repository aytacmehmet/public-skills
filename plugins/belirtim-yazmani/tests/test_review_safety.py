# SPDX-License-Identifier: GPL-3.0-only
"""Adversarial acceptance boundaries; synthetic records never prove real review."""
import copy
import io
import itertools
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bv2 as b
import delivery as d
import preflight
import review_contract as review
import source_pool as pool
from fixture_v4 import valid,seal


class ReviewSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.doc=valid(self.root)
        self.spec,self.control=d.get_state(self.doc)

    def test_permutations_cannot_hide_wrong_or_missing_scenario_results(self):
        for order in itertools.permutations(range(3)):
            correct=copy.deepcopy(self.doc)
            for rnd in correct['delivery']['control']['eval_rounds']:
                rnd['readers'][2]['expected_results']={}
                rnd['readers'][2]['response_sha256']=review.response_sha(rnd['readers'][2])
                rnd['readers']=[rnd['readers'][index] for index in order]
            self.assertEqual(d.evaluate(correct)['decision'],'DELIVERABLE')
            for scenario in review.SCENARIO_READERS:
                for result in ({'TC-01':{'result':'WRONG'}},{}):
                    wrong=copy.deepcopy(correct)
                    for rnd in wrong['delivery']['control']['eval_rounds']:
                        row=next(row for row in rnd['readers'] if row['reader_id']==scenario)
                        row['expected_results']=result
                        row['response_sha256']=review.response_sha(row)
                    codes={row['code'] for row in d.evaluate(wrong)['issues']}
                    self.assertIn('F3_DISAGREEMENT',codes)
                    self.assertIn('F5_TWO_CLEAN',codes)

    def test_missing_duplicate_and_substituted_roles_never_release(self):
        for ids in (['reader-1','reader-1','reader-3'],['reader-1','reader-3'],['reader-1','reader-2','reader-4']):
            doc=copy.deepcopy(self.doc)
            for rnd in doc['delivery']['control']['eval_rounds']:
                rows=copy.deepcopy(rnd['readers'])
                rnd['readers']=[{**rows[min(index,2)],'reader_id':identity} for index,identity in enumerate(ids)]
            self.assertIn('F2_READERS',{row['code'] for row in d.evaluate(doc)['issues']})

    def test_ref_oracle_blocks_preflight_and_issuance_without_source_mutation(self):
        content={'test_cases':copy.deepcopy(self.spec['test_cases'])}
        raw=b.encode(content).encode('utf-8')
        name='fixture-talep-test-source.toon'
        (self.root/name).write_bytes(raw)
        self.spec['references']=[{'id':'REF-TESTS','kind':'LIST','path':name,'sha256':b.digest(raw),
                                 'pointer':'/test_cases','purpose':'Original test source'}]
        self.control['assets'].append({'path':name,'sha256':b.digest(raw)})
        seal(self.doc)
        before=copy.deepcopy(self.control['eval_requests'])
        result=preflight.inspect(self.doc,self.root)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertIn('REVIEW_ORACLE_EXPOSURE',json.dumps(result))
        with self.assertRaisesRegex(b.Invalid,'Preflight blocked'):
            d.eval_request(self.doc,3,self.root)
        self.assertEqual(before,self.control['eval_requests'])
        self.assertEqual((self.root/name).read_bytes(),raw)

    def test_dependency_text_and_peer_oracles_block_without_issuance(self):
        before=copy.deepcopy(self.control['eval_requests'])
        cases=[{'id':'TC-01','expected':{'result':'SAVED'}},
               {'expected_results':{'TC-01':{'result':'SAVED'}}},
               {'reader_id':'other','context_id':'peer-context','request_sha256':'a'*64,'findings':[]},
               'id: TC-01\nexpected: {result: SAVED}',
               {'TC-01':{'expectedResult':'SAVED'}}]
        for content in cases:
            prepared={'assets':[],'references':[],'dependency_contracts':[{'content':content}]}
            with self.assertRaisesRegex(b.Invalid,'REVIEW_(ORACLE|PEER)_EXPOSURE'):
                d._issue_review_packets(self.doc,3,prepared)
            self.assertEqual(before,self.control['eval_requests'])
        review.assert_blind_content({'id':'TC-01','expected_quantity':3,'rule':'A saved record is expected.'},{'TC-01'})

    def test_reader_validates_current_roles_and_oracles_and_reads_32_only_explicitly(self):
        prepared={'assets':[],'references':[],'source_pool':{'version':pool.POOL_VERSION,'sources':[]}}
        packet=d._issue_review_packets(self.doc,3,prepared)[0]
        pool.Reader(packet)
        for field,value in (('review_role','FULL_REVIEW'),('scenario_reader',False),('blindness_sha256',None)):
            changed=copy.deepcopy(packet)
            changed[field]=value
            changed['request_sha256']=pool.value_sha({k:v for k,v in changed.items() if k!='request_sha256'})
            with self.assertRaises(b.Invalid):pool.Reader(changed)
        changed=copy.deepcopy(packet)
        changed['spec']['test_cases'][0]['expected']={'result':'SAVED'}
        changed['request_sha256']=pool.value_sha({k:v for k,v in changed.items() if k!='request_sha256'})
        with self.assertRaisesRegex(b.Invalid,'ORACLE_EXPOSURE'):pool.Reader(changed)
        legacy=copy.deepcopy(packet)
        legacy['protocol']='3.2'
        legacy.pop('review_role')
        legacy.pop('blindness_sha256')
        legacy['request_sha256']=pool.value_sha({k:v for k,v in legacy.items() if k!='request_sha256'})
        with self.assertRaisesRegex(b.Invalid,'stale'):pool.Reader(legacy)
        self.assertTrue(pool.Reader(legacy,allow_legacy=True).legacy_read_only)

    def test_multi_reference_cli_loads_once_and_preserves_single_reference_output(self):
        raw=b.encode({'rows':[{'value':1},{'value':2}]}).encode('utf-8')
        refs=[{'id':'REF-'+str(i),'kind':'LIST','path':'fixture-talep-source.toon','sha256':b.digest(raw),
               'pointer':'/rows/'+str(i),'purpose':'Functional input'} for i in range(2)]
        bindings,sources=pool.collect(refs,{refs[0]['path']:raw})
        packet=d._issue_review_packets(self.doc,3,{'assets':[],'references':bindings,'source_pool':sources})[0]
        source=self.root/'packet.toon'
        source.write_text(b.encode(packet),encoding='utf-8')
        output=io.StringIO()
        with patch.object(b,'load',wraps=b.load) as load, patch.object(pool,'Reader',wraps=pool.Reader) as reader, redirect_stdout(output):
            b.main(['read-reference',str(source),'--reference-id','REF-0','--reference-id','REF-1'])
        self.assertEqual(load.call_count,1)
        self.assertEqual(reader.call_count,1)
        self.assertEqual(json.loads(output.getvalue())['values'],{'REF-0':{'value':1},'REF-1':{'value':2}})
        output=io.StringIO()
        with redirect_stdout(output):b.main(['read-reference',str(source),'--reference-id','REF-0'])
        self.assertEqual(set(json.loads(output.getvalue())),{'reference_id','legacy_read_only','value'})

    def test_status_evaluates_current_snapshot_once(self):
        with patch.object(d,'evaluate',wraps=d.evaluate) as evaluate:
            result=preflight.status(self.doc,self.root)
        self.assertEqual(result['preflight'],'PASS')
        self.assertEqual(evaluate.call_count,1)

    def test_malformed_packet_and_empty_round_fail_with_structured_diagnostics(self):
        packet=d._issue_review_packets(self.doc,3,{'assets':[],'references':[]})[0]
        for changed in ([],{**packet,'source_pool':None},{**packet,'references':None},{**packet,'reader_id':{}}):
            with self.assertRaises(b.Invalid):pool.Reader(changed)
        before=copy.deepcopy(self.control['eval_rounds'])
        with self.assertRaisesRegex(b.Invalid,'three unique'):
            d.record_round(self.doc,{'revision_sha256':d.revision(self.spec),'readers':[]})
        self.assertEqual(self.control['eval_rounds'],before)
