# SPDX-License-Identifier: GPL-3.0-only
import copy,json,sys,tempfile,unittest,zipfile,io,struct,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import bv2 as b
import delivery as d
from fixture_v4 import valid,seal,png

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.doc=valid(self.root)
        self.spec,self.control=d.get_state(self.doc)
    def tearDown(self): self.temp.cleanup()
    def codes(self): return {x['code'] for x in d.evaluate(self.doc)['issues']}
    def test_complete_fixture_record_gate(self): self.assertEqual(d.evaluate(self.doc)['decision'],'DELIVERABLE')
    def test_selected_context_closure_excludes_review_answers(self):
        packet=d.context_packet(self.spec,['requirements'])
        self.assertFalse(packet['authoritative']);self.assertIn('OBJ-01',packet['included_ids']);self.assertIn('TC-03',packet['included_ids'])
        self.assertNotIn('control',packet['data']);self.assertNotIn('eval_rounds',packet['data'])
    def test_missing_delivery_and_old_draft_never_packages(self):
        old=copy.deepcopy(self.doc);old['delivery']=None
        with self.assertRaises(b.Invalid): b.package(old,self.root,self.root)
    def test_open_intake_decision_question_and_safe_default(self):
        for name,row in [('intake',{'status':'OPEN'}),('decisions_gaps',{'status':'BLOCKED'}),('open_questions',{'status':'OPEN'}),('safe_default_answers',{'owner_approved':False}),('system_conflicts',{'status':'OPEN'})]:
            old=copy.deepcopy(self.control[name]);self.control[name]=[row]
            self.assertIn('D2_ZERO_OPEN',self.codes());self.control[name]=old
    def test_closed_flag_without_owner_answer_is_not_closed(self):
        self.control['open_questions']=[{'status':'CLOSED'}];self.assertIn('D2_ZERO_OPEN',self.codes())
        self.control['open_questions']=[{'status':'CLOSED','owner_confirmed':True,'answer_pointer':'/requirements/0/statement'}]
        self.assertNotIn('D2_ZERO_OPEN',self.codes())
    def test_evasive_marker(self):
        for phrase in ['uygun şekilde','gerekirse','vb.','mümkünse','…','TBD','NEEDS CLARIFICATION']:
            self.spec['change_rationale']=phrase;self.assertIn('D2_D4_GAP',self.codes())
    def test_code_and_expression(self):
        for phrase in ['SELECT x FROM zfoo','CAST( x AS decimal )','CASE WHEN x THEN y','define view entity ZFOO','METHOD save.','```pseudo\nif x\n```']:
            self.spec['change_rationale']=phrase;self.assertIn('B2_B4_CODE',self.codes())
        self.spec['change_rationale']='Known reason';self.spec['table_fields'][0]['derivation']='width * length'
        self.assertIn('B4_EXPRESSION',self.codes())
    def test_producer_model_private_and_syntax(self):
        for phrase in ['Claude','Codex','tool_receipts','mutation_policy','/plan','[[vault]]']:
            self.spec['change_rationale']=phrase;self.assertIn('C7_ATTRIBUTION',self.codes())
        self.spec['change_rationale']='Known reason';self.spec['sections']['producerApproval']={'by':'Someone'}
        self.assertIn('C5_PRIVATE',self.codes())
    def test_business_model_is_not_developer_model_setting(self):
        self.spec['sections']['domain']={'model':'mill-type-a','approval':{'business_status':'REQUIRED'}}
        self.assertNotIn('C5_PRIVATE',self.codes())
    def test_snake_case_private_metadata_and_build_prompt(self):
        self.spec['sections']['execution_mode']='normal';self.assertIn('C5_PRIVATE',self.codes())
        self.spec['sections']={'note':'You are an assistant developer. Implement everything.'}
        self.assertIn('B7_AI_PROMPT',self.codes())
    def test_profile_missing_mandatory_attribute(self):
        del self.spec['ui_elements'][0]['mandatory'];self.assertIn('D3_SCHEMA',self.codes())
    def test_callout_missing_and_label_conflict(self):
        self.spec['ui_callouts'].pop();self.assertIn('B5_CALLOUT_COVERAGE',self.codes())
        self.spec['ui_callouts'][0]['label']='Different';self.assertIn('F4_LABEL',self.codes())
    def test_action_three_trace_paths(self):
        self.spec['ui_actions'][0]['trace_paths']['authorization_error']=[];self.assertIn('D3_TRACE_PATH',self.codes())
    def test_boundary_and_decision_table(self):
        self.spec['business_rules'][0]['examples'][1]['boundary']=False;self.assertIn('D3_BOUNDARY',self.codes())
        self.spec['business_rules'][0]['multi_condition']=True;self.assertIn('D3_DECISION_TABLE',self.codes())
    def test_nonfinal_state_has_exit(self):
        self.spec['status_transitions']=[];self.assertIn('D3_STATE_EXIT',self.codes())
    def test_requirement_ac_test_object_chains(self):
        self.spec['requirements'][0]['acceptance_criteria']=[];self.assertIn('D7_AC',self.codes())
        self.spec['acceptance_criteria'][0]['test_cases']=[];self.assertIn('D7_TEST',self.codes())
        self.spec['objects'][0]['requirement_refs']=[];self.assertIn('D7_ORPHAN_OBJECT',self.codes())
    def test_wrong_reference_and_duplicate(self):
        self.spec['messages'][0]['trigger_rule_ref']='NONE';self.assertIn('D7_REF',self.codes())
        self.spec['objects'][0]['id']='REQ-01';self.assertIn('D7_DUPLICATE',self.codes())
    def test_project_name_version_rule(self):
        self.spec['meta']['handoff_version']='1.0.0';self.assertIn('A4_NAMING',self.codes())
    def test_workspace_foreign_identity(self):
        self.spec['meta']['development_id']='RMP';self.assertIn('A2_SCOPE_ID',self.codes())
    def test_foreign_object_changes_need_separate_handoff(self):
        self.spec['objects'][0]['owner_development']='RMP';self.assertIn('E1_FOREIGN_MUTATION',self.codes())
        self.spec['objects'][0]['operation']='UNTOUCHED';self.assertNotIn('E1_FOREIGN_MUTATION',self.codes())
    def test_current_approval_and_defaults_approval(self):
        self.spec['requirements'][0]['statement']='Changed behavior';self.assertIn('APPROVAL_CURRENT',self.codes())
        self.spec['functional_defaults']['rules'][0]['text']='Changed default';self.assertIn('D5_APPROVED_DEFAULTS',self.codes())
    def test_no_semantic_execution_does_not_pass(self):
        self.control['review_execution_confirmed']=False;self.assertIn('F2_EXECUTION_CONFIRMATION',self.codes())
        self.control['eval_rounds']=[];report=d.evaluate(self.doc)
        self.assertIn('F5_TWO_CLEAN',self.codes());self.assertTrue(all(x['status']=='NOT_RUN' for x in report['layers'][1:]))
    def test_three_independent_fresh_readers(self):
        self.control['eval_rounds'][1]['readers']=self.control['eval_rounds'][1]['readers'][:2];self.assertIn('F2_READERS',self.codes())
    def test_reused_context_or_shared_answers(self):
        readers=self.control['eval_rounds'][1]['readers'];readers[1]['context_id']=readers[0]['context_id'];readers[2]['saw_other_results']=True
        self.assertIn('F2_INDEPENDENCE',self.codes())
    def test_wrong_question_pointer_answer_or_requirement_coverage(self):
        reader=self.control['eval_rounds'][1]['readers'][0];reader['questions'][0]['pointer']='/missing';self.assertIn('F2_POINTER',self.codes())
        reader['questions'][0]['pointer']='/requirements/0/statement';reader['questions'][0]['answer']='Wrong';self.assertIn('F2_ANSWER',self.codes())
        reader['covered_requirements']=[];self.assertIn('F2_COVERAGE',self.codes())
    def test_reader_findings_cannot_be_ignored_by_zero_summary(self):
        self.control['eval_rounds'][1]['readers'][0]['findings']=['A design question remains']
        self.assertIn('F2_OPEN_FINDING',self.codes())
    def test_independent_scenario_disagreement(self):
        self.control['eval_rounds'][1]['readers'][1]['expected_results']['TC-01']={'result':'OTHER'};self.assertIn('F3_DISAGREEMENT',self.codes())
    def test_visual_actual_inspection_coverage(self):
        for r in self.control['eval_rounds'][1]['readers']: r['visual_matches']=[]
        self.assertIn('F4_COVERAGE',self.codes())
    def test_plan_invents_decision(self):
        self.control['eval_rounds'][1]['readers'][0]['plan_decisions'][0]['pointer']='/not-stated';self.assertIn('F5_PLAN_DECISION',self.codes())
    def test_two_clean_and_current_revision(self):
        self.control['eval_rounds'].pop();self.assertIn('F5_TWO_CLEAN',self.codes())
        self.control['eval_rounds'][0]['new_open_count']=1;self.assertIn('F5_NEW_OPEN',self.codes())
        self.control['eval_rounds'][0]['revision_sha256']='wrong';self.assertIn('F5_STALE_ROUND',self.codes())
    def test_review_request_binding_and_round_limit(self):
        self.control['eval_rounds'][1]['readers'][0]['request_sha256']='wrong';self.assertIn('F2_REQUEST_BINDING',self.codes())
        self.control['round_limit']=2
        with self.assertRaises(b.Invalid): d.eval_request(self.doc,3)
    def test_unknown_baseline_and_no_access_no_absence(self):
        self.spec['meta']['mode']='UPDATE';self.spec['baseline']['kind']='UNKNOWN';self.assertIn('E3_BASELINE_UNKNOWN',self.codes())
        self.spec['baseline']['kind']='FINAL_HANDOFF';self.control['baseline_system_state']='UNKNOWN';self.assertIn('E3_ABSENCE',self.codes())
    def test_public_package_self_hash_metadata_optional_excel(self):
        result=d.package(self.doc,self.root/'out',self.root);p=Path(result['path'])
        self.assertEqual(p.name,'handoff-fixture-talep-v1.zip');self.assertEqual(result['verification']['status'],'PASS')
        with zipfile.ZipFile(p) as z:
            self.assertIn('fixture-talep-schema.toon',z.namelist());self.assertIn('fixture-talep-specification.xlsx',z.namelist())
            self.assertFalse(any('approval' in n or n.endswith('.py') for n in z.namelist()))
            manifest=json.loads(b.codec('decode',z.read('fixture-talep-manifest.toon').decode()))
            self.assertEqual(set(r['path'] for r in manifest['files']),set(z.namelist()))
            self.assertIsNone(next(r for r in manifest['files'] if r['path']=='fixture-talep-manifest.toon')['sha256'])
            spec=json.loads(b.codec('decode',z.read('fixture-talep-belirtim.toon').decode()));self.assertNotIn('control',spec)
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'out',self.root)
        second=d.package(self.doc,self.root/'without-excel',self.root,False)
        with zipfile.ZipFile(second['path']) as z: self.assertNotIn('fixture-talep-specification.xlsx',z.namelist())
    def test_missing_png_and_png_metadata_block_export(self):
        media=self.root/self.spec['media'][0]['path'];media.unlink()
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'out',self.root)
        data=png();i=data.rfind(b'\x00\x00\x00\x00IEND');payload=b'Software\x00Producer'
        chunk=len(payload).to_bytes(4,'big')+b'tEXt'+payload+(zlib.crc32(b'tEXt'+payload)&0xffffffff).to_bytes(4,'big')
        with self.assertRaises(b.Invalid): d.clean_png(data[:i]+chunk+data[i:])
    def test_excel_visible_parity_and_formula_injection(self):
        from openpyxl import load_workbook
        path=self.root/'excel.xlsx';d.render_excel(self.spec,d.evaluate(self.doc),path);d.verify_excel(self.spec,path)
        wb=load_workbook(path);wb['requirements']['B2']='Changed';wb.save(path)
        with self.assertRaises(b.Invalid): d.verify_excel(self.spec,path)
    def test_zip_hash_tamper_rejected(self):
        result=d.package(self.doc,self.root/'out',self.root);path=Path(result['path'])
        with zipfile.ZipFile(path) as z: files={n:z.read(n) for n in z.namelist()}
        files['fixture-talep-readme.md']+=b'changed'
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            for n,data in files.items(): z.writestr(n,data)
        with self.assertRaises(b.Invalid): d.verify(path)
    def test_feedback_creates_regression_and_requires_new_version(self):
        d.feedback(self.doc,'Authorization outcome unclear','authorization')
        self.assertEqual(self.control['feedback'][0]['status'],'OPEN');self.assertIn('D2_ZERO_OPEN',self.codes());self.assertIn('A6_FEEDBACK_VERSION',self.codes())
    def test_delta_stable_ids_presence_and_full_target(self):
        before=copy.deepcopy(self.spec);after=copy.deepcopy(self.spec);after['requirements'].reverse()
        delta=d.changes(before,after)
        self.assertTrue(any(r['pointer']=='/requirements/@order' for r in delta['changes']))
        self.assertTrue(all(r['kind']=='MODIFIED' for r in delta['changes']))
    def test_update_with_confirmed_baseline_and_full_source(self):
        base=copy.deepcopy(self.spec);prior=d.package(self.doc,self.root/'baseline',self.root);self.spec['meta'].update(mode='UPDATE',handoff_version='v2',fs_version='v2')
        self.spec['changelog'].append({'version':'v2','date':'2026-09-30','change':'Fixture update'})
        self.spec['change_rationale']='Fixture correction';path=self.root/'evidence/fixture-talep-system.md';path.parent.mkdir(exist_ok=True);path.write_text('Controlled fixture: system absent. Not tenant proof.')
        self.control['assets'].append({'path':'evidence/fixture-talep-system.md','sha256':b.digest(path.read_bytes())})
        self.spec['baseline']={'kind':'FINAL_HANDOFF','system':None,'client':None,'verified_at':None,'reference_name':'handoff-fixture-talep-v1.zip','reference_version':'v1','reference_sha256':prior['zipSha256'],'spec_sha256':d.revision(base),'evidence_paths':['evidence/fixture-talep-system.md']}
        self.control.update(baseline_spec=base,baseline_system_state='ABSENT_VERIFIED',baseline_final_approved=True,baseline_reference_path='baseline/handoff-fixture-talep-v1.zip');seal(self.doc)
        result=d.package(self.doc,self.root/'update',self.root)
        with zipfile.ZipFile(result['path']) as z:
            self.assertIn('fixture-talep-baseline.toon',z.namelist());self.assertIn('fixture-talep-changes.toon',z.namelist());self.assertIn('fixture-talep-belirtim.toon',z.namelist())
    def test_interactive_offline_exception_scope(self):
        path=self.root/'mockup/interactive/fixture-talep-index.html';path.parent.mkdir(parents=True);path.write_text('<html><button>Demo</button></html>')
        asset={'path':'mockup/interactive/fixture-talep-index.html','sha256':b.digest(path.read_bytes())};self.control['assets'].append(asset)
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'out',self.root)
        self.control['mockup_exception']={'authorized':True,'receipt':'Fixture-only explicit exception','offline_verified':True,'offline_evidence':'Fixture simulated offline receipt'}
        self.assertEqual(d.package(self.doc,self.root/'out',self.root)['verification']['status'],'PASS')
        path.write_text('<script>fetch("https://example.com")</script>');asset['sha256']=b.digest(path.read_bytes())
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'network',self.root)

if __name__=='__main__': unittest.main(verbosity=2)
