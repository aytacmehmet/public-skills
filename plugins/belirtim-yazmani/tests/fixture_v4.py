# SPDX-License-Identifier: GPL-3.0-only
"""Synthetic contract/review records, NOT a real model eval or tenant proof."""
import copy,hashlib,struct,zlib
from pathlib import Path
import bv2 as b
import delivery as d

def png():
    # Small neutral PNG; visual-review answers below are synthetic fixtures only.
    def chunk(t,p): return len(p).to_bytes(4,'big')+t+p+(zlib.crc32(t+p)&0xffffffff).to_bytes(4,'big')
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',2,2,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00\xff\xff\xff\xff\xff\xff'*2))+chunk(b'IEND',b'')

def valid(root):
    image=png();rel='mockup/screens/fixture-talep-screen-01.png';path=Path(root)/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(image)
    content={'sema':'1.0','meta':{'surum':'v1','tarih':'2026-09-30','hazirlayan':'Fixture','durum':'Taslak','musteri':'Fixture'},'turler':['U'],'profil':'standart','bolumler':{'1.1':{'alanlar':{'gel_id':'DEMO-01','baslik':'Fixture talep','sistem':'S/4HANA Cloud Public Edition'}}},'surum_gecmisi':[],'onaylar':[]}
    doc=b.wrap(content,'DEMO-01','fixture-talep','Fixture talep','1.0.0');d.release_init(doc)
    spec={
      'schemaVersion':'3.0','developer_decisions':[],'references':[],
      'architecture':{'summary':'Quantity persistence and authorization follow the stated business contract.',
        'boundaries':[{'id':'BOUNDARY-01','object_refs':['OBJ-01'],'responsibility':'Own the request quantity record.'}],
        'constraints':[{'id':'ARCH-01','statement':'Every implementation preserves positive quantity and authorization outcomes.','requirement_refs':['REQ-01','REQ-02']}]},
      'meta':{'development_id':'DEMO-01','name':'Fixture talep','development_name':'fixture-talep','handoff_version':'v1','fs_version':'v1','edition':'S/4HANA Cloud Public Edition','release':'2608','types':['U'],'language':'tr','mode':'NEW'},
      'scope_items':{'included':['Talep miktarı doğrulama'],'excluded':['SAP tenant işlemleri'],'preserved':['Mevcut süreçte değişiklik yok']},
      'naming_rules':{'name':'Fixture naming','version':'1.0','development_pattern':'[a-z]+(?:-[a-z]+)*','version_pattern':'v[0-9]+','object_pattern':'Z[A-Z_]+','description':'Fixture adı küçük harf ve tire, sürüm v ve sayı, özel nesne Z ile başlar.'},
      'functional_defaults':{'name':'Fixture iş varsayılanları','version':'1.0','rules':[{'id':'DEF-01','text':'Miktar KG ve üç ondalık basamakla gösterilir; otomatik yuvarlama yapılmaz.'}]},
      'sections':{},
      'requirements':[{'id':'REQ-01','statement':'Sistem sıfırdan büyük KG miktarı kabul eder.','acceptance_criteria':['AC-01','AC-02']},{'id':'REQ-02','statement':'Yetkisiz kullanıcı talep kaydedemez.','acceptance_criteria':['AC-03']}],
      'acceptance_criteria':[{'id':'AC-01','requirement_ref':'REQ-01','statement':'Yetkili kullanıcı pozitif miktarı kaydeder.','test_cases':['TC-01']},{'id':'AC-02','requirement_ref':'REQ-01','statement':'Sıfır miktar kayıt oluşturmaz.','test_cases':['TC-02']},{'id':'AC-03','requirement_ref':'REQ-02','statement':'Yetkisiz kayıt denemesi reddedilir.','test_cases':['TC-03']}],
      'test_cases':[{'id':'TC-01','acceptance_ref':'AC-01','kind':'HAPPY','input':{'Quantity':'1.250','authorized':True},'expected':{'result':'SAVED'},'object_refs':['OBJ-01']},{'id':'TC-02','acceptance_ref':'AC-02','kind':'VALIDATION_ERROR','input':{'Quantity':'0','authorized':True},'expected':{'result':'NO_RECORD','message':'MSG-01'},'object_refs':['OBJ-01']},{'id':'TC-03','acceptance_ref':'AC-03','kind':'AUTHORIZATION_ERROR','input':{'Quantity':'1.250','authorized':False},'expected':{'result':'NO_RECORD','message':'MSG-02'},'object_refs':['OBJ-01']}],
      'objects':[{'id':'OBJ-01','name':'ZDEMO_REQUEST','object_type':'TABL','operation':'NEW','owner_development':'DEMO-01','requirement_refs':['REQ-01','REQ-02']}],
      'business_rules':[{'id':'BR-01','text':'Miktar sıfırdan büyük olmalıdır.','multi_condition':False,'decision_table':[],'examples':[{'input':{'quantity':'1.250'},'output':{'valid':True},'boundary':False},{'input':{'quantity':'0'},'output':{'valid':False},'boundary':True}]},{'id':'BR-02','text':'Kayıt yetkisi gerekir.','multi_condition':False,'decision_table':[],'examples':[{'input':{'authorized':True},'output':{'allowed':True},'boundary':False},{'input':{'authorized':False},'output':{'allowed':False},'boundary':True}]}],
      'screens':[{'id':'SCR-01','title':'Talep','media_refs':['MED-01'],'ui_element_ids':['EL-01','EL-02']}],
      'media':[{'id':'MED-01','path':rel,'sha256':b.digest(image),'screen_ref':'SCR-01','format':'PNG'}],
      'ui_callouts':[{'id':'CALL-01','media_ref':'MED-01','number':1,'ui_element_ref':'EL-01','label':'Miktar'},{'id':'CALL-02','media_ref':'MED-01','number':2,'ui_element_ref':'EL-02','label':'Kaydet'}],
      'ui_elements':[{'id':id_,'screen_ref':'SCR-01','label':label,'source':{'kind':'UI_ONLY','ref':None},'mandatory':mandatory,'editable':editable,'default':{'kind':'NONE','value':None,'ref':None},'value_help':{'kind':'NONE','ref':None,'values':[]}} for id_,label,mandatory,editable in [('EL-01','Miktar',True,True),('EL-02','Kaydet',False,False)]],
      'ui_actions':[{'id':'ACT-01','screen_ref':'SCR-01','enabled_when':'Yetkili kullanıcı düzenleme durumundadır.','result':'Geçerli kayıt kaydedilir; geçersiz giriş veya yetkisizlik kayıt oluşturmaz.','trace_paths':{'happy':['TC-01'],'validation_error':['TC-02'],'authorization_error':['TC-03']}}],
      'messages':[{'id':'MSG-01','tr':'Miktar sıfırdan büyük olmalıdır.','en':'Quantity must be positive.','type':'E','trigger_rule_ref':'BR-01'},{'id':'MSG-02','tr':'Kayıt yetkiniz yok.','en':'You are not authorized to save.','type':'E','trigger_rule_ref':'BR-02'}],
      'statuses':[{'id':'ST-01','name':'Düzenleme','final':False},{'id':'ST-02','name':'Kaydedildi','final':True}],
      'status_transitions':[{'id':'TRANS-01','from_ref':'ST-01','to_ref':'ST-02','actor':'Yetkili kullanıcı','condition':'Pozitif miktar ve kayıt yetkisi bulunur.'}],
      'cds_fields':[],'table_fields':[{'id':'FLD-01','object_ref':'OBJ-01','field':'Quantity','data_type':'decimal scale 3 KG','derivation':None}],
      'dependencies':[],'baseline':{'kind':'NEW','system':None,'client':None,'verified_at':None,'reference_name':None,'reference_version':None,'reference_sha256':None,'spec_sha256':None,'evidence_paths':[]},
      'change_rationale':'Fixture başlangıcı','changelog':[{'version':'v1','date':'2026-09-30','change':'Fixture ilk sürüm'}]
    }
    doc['delivery']['spec']=spec;control=doc['delivery']['control'];control['decisions_gaps']=[]
    control['assets']=[{'path':rel,'sha256':b.digest(image)}]
    seal(doc)
    return doc

def seal(doc):
    spec,control=d.get_state(doc);control['eval_rounds']=[];control['eval_requests']=[]
    control.update(approved_spec_sha256=d.revision(spec),approval_receipt='SYNTHETIC_FIXTURE_ONLY',approved_defaults_sha256=d.defaults_sha(spec),defaults_approval_receipt='SYNTHETIC_FIXTURE_ONLY',review_execution_confirmed=True,review_confirmation_receipt='SYNTHETIC_FIXTURE_ONLY')
    for n in [1,2]:
        packets=d._issue_review_packets(doc,n,{'assets':[],'references':[],'input_sha256':'SYNTHETIC_FIXTURE_ONLY'});readers=[]
        for i,packet in enumerate(packets):
            reader={'reader_id':packet['reader_id'],'context_id':packet['context_id'],'request_sha256':packet['request_sha256'],'isolated':True,'saw_other_results':False,'status':'COMPLETED',
              'covered_requirements':[x['id'] for x in spec['requirements']],
              'questions':[{'requirement_ref':r['id'],'question':'What is the stated functional behavior?','pointer':'/requirements/'+str(j)+'/statement','answer':r['statement']} for j,r in enumerate(spec['requirements'])],
              'expected_results':{r['id']:r['expected'] for r in spec['test_cases']},
              'visual_matches':[{'media_ref':r['media_ref'],'ui_element_ref':r['ui_element_ref'],'method':'PNG_INSPECTION','label_match':True,'layout_match':True} for r in spec['ui_callouts']],
              'plan_completed':True,'plan_decisions':[{'decision':'Use the stated object.','pointer':'/objects/0/name'}]+[{'decision':'Preserve the stated constraint.','pointer':'/architecture/constraints/'+str(j)+'/statement'} for j,r in enumerate(spec.get('architecture',{}).get('constraints',[]))]+[{'decision':'Respect dependency rollout.','pointer':'/dependencies/'+str(j)+'/contract'} for j,r in enumerate(spec.get('dependencies',[]))]+[{'decision':'Defer the bounded implementation choice.','pointer':'/developer_decisions/'+str(j)+'/question'} for j,r in enumerate(spec.get('developer_decisions',[])) if r['status']=='OPEN'],
              'execution_evidence':'SYNTHETIC_RESPONSE_NOT_REAL_MODEL_EXECUTION','response_sha256':b.digest(b.canonical({'fixture':n,'reader':i}))}
            reader['findings']=[]
            import review_contract
            reader['response_sha256']=review_contract.response_sha(reader)
            readers.append(reader)
        d.record_round(doc,{'revision_sha256':d.revision(spec),'readers':readers,'new_open_count':0})
