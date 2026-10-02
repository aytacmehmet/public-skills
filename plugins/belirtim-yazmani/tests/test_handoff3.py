# SPDX-License-Identifier: GPL-3.0-only
"""Synthetic role/batch regressions, never real reviewer or tenant evidence."""
import copy,json,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bv2 as b
import delivery as d
import handoff3 as h
from fixture_v4 import valid,seal

class Handoff3Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.doc=valid(self.root);self.spec,self.control=d.get_state(self.doc)
    def tearDown(self): self.temp.cleanup()
    def decision(self):
        return {'id':'TECH-01','owner':'ABAP_DEVELOPER','domain':'IMPLEMENTATION',
          'question':'Choose the persistence implementation within the specified data contract.',
          'context':'Quantity behavior, object responsibility and authorization outcomes are already fixed.',
          'constraints':['Preserve every acceptance outcome and the declared data contract.'],
          'architecture_constraint_refs':['ARCH-01'],'reference_ids':[],
          'affects_functional_contract':False,'status':'OPEN','answer':None}
    def add_technical(self):
        row=self.decision();self.spec['developer_decisions'].append(row)
        self.control['open_questions'].append({k:row[k] for k in ('id','owner','domain','question','status')})
    def question(self):
        return {'id':'OPEN-01','owner':'CONSULTANT','domain':'BUSINESS','status':'OPEN',
          'question':'Which business approval behavior is required?',
          'options':[{'text':'Explicit approval','rationale':'Preserves the stated control intent.','assumptions':['Business owner can approve.'],
              'scores':{'consistency':5,'suitability':4,'quality':5}},
            {'text':'Approval after validation','rationale':'Fits the supplied task flow.','assumptions':['Validation rules are approved.'],
              'scores':{'consistency':3,'suitability':4,'quality':3}}]}
    def test_consultant_only_questions_sorted_and_scored(self):
        self.add_technical();self.control['intake'].append(self.question())
        result=h.consultant_questions(self.doc)
        self.assertEqual([r['id'] for r in result],['OPEN-01'])
        self.assertEqual([r['label'] for r in result[0]['options']],['A','B'])
        self.assertGreater(result[0]['options'][0]['score'],result[0]['options'][1]['score'])
        self.assertEqual(d.evaluate(self.doc)['decision'],'BLOCKED')
    def test_options_cap_range_and_information_without_invented_choices(self):
        options=self.question()['options']
        with self.assertRaises(b.Invalid): h.score_options(options*2)
        options[0]['scores']['quality']=6
        with self.assertRaises(b.Invalid): h.score_options(options)
        q=self.question();q['options']=[];q['options_reason']='The provided facts do not support a safe suggestion.'
        self.control['intake']=[q];self.assertEqual(h.consultant_questions(self.doc)[0]['options'],[])
    def test_mixed_or_unowned_technical_question_not_sent_to_consultant(self):
        q=self.question();q.update(domain='IMPLEMENTATION')
        self.control['intake']=[q]
        with self.assertRaises(b.Invalid): h.consultant_questions(self.doc)
        q.update(owner='ABAP_DEVELOPER',domain='BUSINESS')
        with self.assertRaises(b.Invalid): h.consultant_questions(self.doc)
    def test_bounded_technical_open_is_deliverable_but_not_coding_ready(self):
        self.add_technical();seal(self.doc)
        report=d.evaluate(self.doc)
        self.assertEqual(report['decision'],'DELIVERABLE',report['issues'])
        self.assertEqual(report['coding_readiness'],'READY_FOR_DEVELOPER_DECISIONS')
        self.assertEqual(report['technical_open_count'],1)
        result=d.package(self.doc,self.root/'out',self.root,False)
        with zipfile.ZipFile(result['path']) as archive:
            row=json.loads(b.codec('decode',archive.read('fixture-talep-developer-decisions.toon').decode()))
            self.assertEqual(row['decisions'][0]['status'],'OPEN')
        self.spec['developer_decisions'][0]['affects_functional_contract']=True
        self.assertEqual(d.evaluate(self.doc)['decision'],'BLOCKED')
    def test_architecture_missing_context_blocks(self):
        self.add_technical();self.spec['developer_decisions'][0]['architecture_constraint_refs']=['MISSING']
        self.assertIn('TECHNICAL_CONTEXT',{r['code'] for r in d.evaluate(self.doc)['issues']})
        self.spec['developer_decisions'][0]['architecture_constraint_refs']=['ARCH-01'];self.spec['architecture']['boundaries']=[]
        self.assertIn('ARCHITECTURE_BOUNDARIES',{r['code'] for r in d.evaluate(self.doc)['issues']})
    def test_all_file_prefixes_manifest_roles_and_standalone_contract(self):
        result=d.package(self.doc,self.root/'out',self.root,False)
        with zipfile.ZipFile(result['path']) as archive:
            names=archive.namelist()
            self.assertTrue(all(Path(n).name.startswith('fixture-talep-') for n in names))
            self.assertFalse(any(Path(n).name in ('fsts.toon','README.md','manifest.toon') for n in names))
            manifest=json.loads(b.codec('decode',archive.read('fixture-talep-manifest.toon').decode()))
            self.assertEqual(manifest['roles']['specification'],'fixture-talep-belirtim.toon')
            self.assertEqual(set(names),{r['path'] for r in manifest['files']})
            self.assertFalse(any(n.endswith('.py') for n in names))
    def test_missing_file_document_list_pointer_and_free_text_ref_block(self):
        self.spec['references']=[{'id':'REF-DATA-01','kind':'LIST','path':'fixture-talep-data.toon',
          'pointer':'/values/0','sha256':'a'*64,'purpose':'Allowed data values.'}];seal(self.doc)
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'missing',self.root,False)
        text=b.encode({'values':['approved']}).encode();(self.root/'fixture-talep-data.toon').write_bytes(text)
        self.spec['references'][0]['sha256']=b.digest(text)
        self.control['assets'].append({'path':'fixture-talep-data.toon','sha256':b.digest(text)})
        self.spec['references'][0]['pointer']='/values/9';seal(self.doc)
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'pointer',self.root,False)
        self.spec['references'][0]['pointer']='/values/0';self.spec['change_rationale']='[Values](fixture-talep-data.toon#/values/9)';seal(self.doc)
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'text-pointer',self.root,False)
        self.spec['change_rationale']='See missing-list.md';seal(self.doc)
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'text-ref',self.root,False)
        self.spec['change_rationale']='Initial approved design';seal(self.doc)
        self.assertEqual(d.package(self.doc,self.root/'complete',self.root,False)['verification']['status'],'PASS')
    def test_local_skill_plugin_and_model_references_rejected(self):
        for text in ['Use $local-skill','Use plugin/local','Generated by Claude']:
            self.spec['change_rationale']=text
            with self.assertRaises(b.Invalid): d.package(self.doc,self.root/('bad-'+str(len(text))),self.root,False)
    def test_incremental_reuse_dependency_closure_and_stale_result_rejection(self):
        initial=h.check_plan(self.doc)
        for name,digest in initial['input_sha256'].items(): h.record_check(self.doc,name,digest,'PASS')
        self.assertEqual(h.check_plan(self.doc)['run'],[])
        self.spec['architecture']['constraints'][0]['statement']+=' Preserve the declared unit.'
        changed=h.check_plan(self.doc)
        self.assertIn('decisions',changed['run']);self.assertIn('architecture',changed['run'])
        self.assertIn('core',changed['reuse']);self.assertIn('references',changed['reuse'])
        with self.assertRaises(b.Invalid): h.record_check(self.doc,'architecture',initial['input_sha256']['architecture'],'PASS')
        self.assertTrue(h.check_plan(self.doc,True)['final_integrity_required'])
    def partner(self):
        root=self.root/'partner';doc=valid(root);spec,control=d.get_state(doc)
        doc['development'].update(id='OTHER-01',slug='linked-change')
        spec['meta'].update(development_id='OTHER-01',development_name='linked-change',name='Linked change')
        spec['objects'][0].update(name='ZOTHER_REQUEST',owner_development='OTHER-01')
        for row in spec['media']:
            old=row['path'];row['path']=old.replace('fixture-talep-','linked-change-')
            control['assets'][0].update(path=row['path'],source_path=old)
        spec['sections']['shared-contract']={'quantity':'positive KG scale 3','authorization':'required'}
        seal(doc);return doc,root
    def link(self,partner):
        spec,_=d.get_state(partner)
        self.spec['dependencies']=[{'development_id':'OTHER-01','handoff_name':'handoff-linked-change-v1.zip','version':'v1',
          'contract':'Quantity interface','implementation_order':1,'partial_rollout_behavior':'Consumer stays disabled until the provider version is available.'}]
        self.control['dependency_contracts']=[{'development_id':'OTHER-01','version':'v1','contract':'Quantity interface',
          'requires_change':True,'source_pointer':'/sections/shared-contract','spec_sha256':d.revision(spec),'content':spec['sections']['shared-contract']}]
        seal(self.doc)
    def test_separate_zip_batch_is_atomic_and_contracts_self_contained(self):
        partner,assets=self.partner();self.link(partner)
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'single',self.root,False)
        result=h.batch([{'doc':self.doc,'assets_root':self.root},{'doc':partner,'assets_root':assets}],self.root/'batch','cohort-v1',False)
        self.assertEqual(len(result['zip_files']),2);self.assertEqual(result['delivery_order'],['OTHER-01','DEMO-01'])
        for item in result['zip_files']: self.assertEqual(d.verify(item['path'])['status'],'PASS')
        with zipfile.ZipFile(result['zip_files'][0]['path']) as archive:
            record=json.loads(b.codec('decode',archive.read('fixture-talep-dependency-contracts.toon').decode()))
            self.assertEqual(record['contracts'][0]['content']['quantity'],'positive KG scale 3')
        with self.assertRaises(b.Invalid): h.batch([{'doc':self.doc,'assets_root':self.root}],self.root/'batch','cohort-v1',False)
    def test_blocked_partner_and_missing_member_publish_nothing(self):
        partner,assets=self.partner();self.link(partner)
        with self.assertRaises(b.Invalid): h.batch([{'doc':self.doc,'assets_root':self.root}],self.root/'out','missing-member',False)
        self.assertFalse((self.root/'out'/'missing-member').exists())
        partner['delivery']['control']['intake']=[self.question()]
        with self.assertRaises(b.Invalid): h.batch([{'doc':self.doc,'assets_root':self.root},{'doc':partner,'assets_root':assets}],self.root/'out','blocked-member',False)
        self.assertFalse((self.root/'out'/'blocked-member').exists())
    def test_old_handoff_is_readable_baseline_but_not_new_export(self):
        legacy=copy.deepcopy(self.doc);legacy['delivery']['spec']=h.core_spec(self.spec);seal(legacy)
        result=d._legacy_package(legacy,self.root/'old',self.root,False)
        self.assertEqual(d.verify(result['path'])['status'],'PASS')
        with self.assertRaises(b.Invalid): d.package(legacy,self.root/'legacy-export',self.root,False)
        before=d.revision(legacy['delivery']['spec']);upgraded=h.upgrade(legacy)
        self.assertEqual(upgraded['source_sha256'],before)
        self.assertEqual(legacy['delivery']['spec']['schemaVersion'],'3.0')
        self.assertIsNone(legacy['delivery']['control']['approved_spec_sha256'])

    def test_batch_object_ownership_cycle_and_duplicate_contract_block(self):
        partner,assets=self.partner();self.link(partner)
        partner['delivery']['spec']['objects'][0]['name']=self.spec['objects'][0]['name']
        with self.assertRaises(b.Invalid): h.batch([{'doc':self.doc,'assets_root':self.root},{'doc':partner,'assets_root':assets}],self.root/'out','overlap',False)
        partner['delivery']['spec']['objects'][0]['name']='ZOTHER_REQUEST'
        partner['delivery']['spec']['dependencies']=[{'development_id':'DEMO-01','implementation_order':1}]
        with self.assertRaises(b.Invalid): h.batch([{'doc':self.doc,'assets_root':self.root},{'doc':partner,'assets_root':assets}],self.root/'out','cycle',False)
        self.control['dependency_contracts']*=2
        with self.assertRaises(b.Invalid): h.dependency_records(self.doc)
        self.assertFalse((self.root/'out').exists())

    def test_contract_change_invalidates_dependent_check_plan(self):
        partner,_=self.partner();self.link(partner)
        original=h.check_plan(self.doc)
        for name,digest in original['input_sha256'].items(): h.record_check(self.doc,name,digest,'PASS')
        self.control['dependency_contracts'][0]['content']={'quantity':'revised contract'}
        plan=h.check_plan(self.doc)
        self.assertIn('references',plan['run']);self.assertIn('decisions',plan['run']);self.assertIn('packaging',plan['run'])
        self.assertIn('core',plan['reuse'])

    def test_selected_context_includes_technical_architecture_and_reference_closure(self):
        self.add_technical();media=self.spec['media'][0]
        self.spec['references']=[{'id':'REF-PNG-01','kind':'FILE','path':media['path'],'pointer':None,'sha256':media['sha256'],'purpose':'Approved layout.'}]
        self.spec['developer_decisions'][0]['reference_ids']=['REF-PNG-01']
        packet=d.context_packet(self.spec,['developer_decisions'])
        self.assertFalse(packet['authoritative'])
        self.assertTrue({'TECH-01','REF-PNG-01','ARCH-01','REQ-01','OBJ-01'}<=set(packet['included_ids']))
        self.assertIn('architecture',packet['data']);self.assertIn('references',packet['data'])
        self.assertNotIn('control',packet['data']);self.assertNotIn('approval_receipt',json.dumps(packet))

    def test_offline_mockup_cannot_reference_a_missing_local_asset(self):
        name='mockup/interactive/fixture-talep-index.html';path=self.root/name;path.parent.mkdir(parents=True)
        path.write_text('<html><script src="fixture-talep-missing.js"></script></html>',encoding='utf-8')
        self.control['assets'].append({'path':name,'sha256':b.digest(path.read_bytes())})
        self.control['mockup_exception']={'authorized':True,'receipt':'Synthetic test exception','offline_verified':True,'offline_evidence':'Synthetic fixture only'}
        with self.assertRaises(b.Invalid): d.package(self.doc,self.root/'bad-local-ref',self.root,False)
        self.assertFalse((self.root/'bad-local-ref'/'handoff-fixture-talep-v1.zip').exists())

if __name__=='__main__': unittest.main()
