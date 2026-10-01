"""Twelve source-grounded review scenarios. Runs offline; no model calls or token estimates."""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import os
import sqlite3
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plugin', required=True)
    parser.add_argument('--work', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--reuse-searches')
    parser.add_argument('--only',action='append')
    args = parser.parse_args()
    plugin = Path(args.plugin).resolve(); work = Path(args.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(plugin/'runtime'))
    from yula import mcp, query, snapshots, adapters, records
    from yula.common import connect, encode, digest, file_hash, atomic_json, now, validate_database, YulaError
    spec = importlib.util.spec_from_file_location('fixture_source', plugin/'tests/test_yula.py')
    fixture_module = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixture_module)
    small = work/'fixture.sqlite'; fixture_module.fixture(small)
    with connect(small, readonly=False) as db:
        for row in db.execute('select edition from corpus_snapshots').fetchall():
            db.execute("update corpus_snapshots set entry_count=(select count(*) from released_catalog where edition=? and release_state!='notListed'), released_count=(select count(*) from released_catalog where edition=? and release_state='released') where edition=?", (row[0],row[0],row[0]))
        db.execute('update doc_documents set topics=(select count(distinct topic_id) from doc_chunks c where c.document_id=doc_documents.document_id)')
    root=work/'corpus';snapshots.init(root)
    cache={}
    if args.reuse_searches:
        cache={(x['domain'],x['query']):x for x in json.loads(Path(args.reuse_searches).read_text(encoding='utf-8'))['queries']}
    results=[];current=None
    def call(name, arguments):
        t=time.perf_counter()
        pair=(arguments.get('domain'),arguments.get('query'))
        if name=='yula_search' and set(arguments)=={'domain','query'} and pair in cache:
            result=cache[pair]['result'];elapsed=cache[pair]['ms'];reused=True
        else:
            result=mcp.call(root,name,arguments);elapsed=(time.perf_counter()-t)*1000;reused=False
        current['calls'].append({'tool':name,'arguments':arguments,'outputBytes':len(encode(result)),
                                 'elapsedMs':round(elapsed,3),'reusedBaselineObservation':reused})
        return result
    def scenario(sid,title,oracle,fn):
        nonlocal current
        if args.only and sid not in args.only:return
        current={'id':sid,'task':title,'oracle':oracle,'calls':[]}
        try:
            fn();current['status']='PASS'
        except Exception as exc:
            current['status']='FAIL';current['observed']=str(exc) or type(exc).__name__
        current['responseBytes']=sum(x['outputBytes'] for x in current['calls'])
        results.append(current)
        print(sid,current['status'],current.get('observed',''),flush=True)
    def require(value,message):
        if not value:raise AssertionError(message)
    def rejected(fn, message):
        try:fn()
        except YulaError:return
        raise AssertionError(message)
    def altered(name):
        dest=work/(name+'.sqlite');snapshots.clone_database(small,dest);return dest

    def s01():
        r=call('yula_search',{'domain':'objects','query':'CL_ABAP_CONTEXT_INFO'})
        require(r['results'][0]['objectName']=='CL_ABAP_CONTEXT_INFO','Exact identity is not ranked first.')
    scenario('S01','Resolve an exact technical identity','objects.object_name exact equality; no semantic inference required',s01)

    def s02():
        for text in ('send PDF to print queue','PDF yazdırmak'):
            r=call('yula_search',{'domain':'objects','query':text})
            require(r['results'][0]['objectName']=='CL_PRINT_QUEUE_UTILS','Curated EN/TR print intent missed.')
        r=call('yula_search',{'domain':'objects','query':'delete print queue'})
        item=next(x for x in r['results'] if x['objectName']=='CL_PRINT_QUEUE_UTILS')
        require(item.get('matchEvidence')!='curated_mapping','Delete intent incorrectly labelled as a curated capability match; stored mappings cover create/list only.')
    scenario('S02','Find an EN/TR capability without inventing delete semantics','capabilities and capability_aliases: print create/list; no delete mapping',s02)

    def s03():
        rejected(lambda:call('yula_get',{'kind':'object','objectType':'CLAS','key':'CL_PRINT_QUEUE_UTILS','release':'1909'}),'Object release filter silently ignored.')
        r=call('yula_search',{'domain':'lessons','query':'Activity ID','release':'9999'})
        require(not r['results'],'Lesson release filter silently ignored.')
    scenario('S03','Respect release context and reject unsupported filters','Only latest Public Edition object catalog is stored; no release 9999 lesson exists',s03)

    def s04():
        r=call('yula_get',{'kind':'object','objectType':'CLAS','key':'CL_PRINT_QUEUE_UTILS','section':'members','member':'CREATE_QUEUE_ITEM_BY_DATA'})
        require('CREATE_QUEUE_ITEM_BY_DATA' in r['members'][0]['signature'],'Stored signature lost.')
        require(r.get('availability',{}).get('decision')=='REVIEW_REQUIRED' and r['availability'].get('eligible') is True and r['availability'].get('state')=='released' and r.get('catalog') and r.get('evidence'),'Direct member response drops availability/provenance.')
    scenario('S04','Retrieve an exact call contract with its evidence','Public member signature; missing target contract/scope/runtime evidence',s04)

    def s05():
        r=call('yula_search',{'domain':'configuration','query':'100274','release':'2608','country':'TR'})
        require(any(x['activityId']=='100274' for x in r['results']),'Global activity (Global/XX) excluded by country applicability filter.')
        p=altered('ambiguous')
        with connect(p,readonly=False) as db:
            row=dict(db.execute("select * from cfg_activities where activity_id='100274'").fetchone())
            row['source_row']=999999;row['activity_name']='Second contextual variant';row['specialized_countries']='DE';row['locality_type']='Local'
            db.execute('insert into cfg_activities values ('+','.join('?' for _ in row)+')',tuple(row.values()))
            r=query.activity_context(db,'100274','2608')
            require(r.get('signal')=='AMBIGUOUS_ACTIVITY','Multiple contextual variants silently reduced to the first row.')
            chosen=query.activity_context(db,'100274','2608',source_row=999999)
            require(chosen.get('contextStatus')=='VARIANT_DOSSIER_UNVERIFIED','Unbound dossier is treated as verified for a different selected variant.')
    scenario('S05','Resolve global/local configuration and contextual ambiguity','SSCUI 100274 is Global/XX; duplicate-ID fixture requires explicit variant selection',s05)

    def s06():
        r=call('yula_get',{'kind':'activity','key':'100274','release':'2608','section':'sources','limit':20})
        expected={'src-learning-cbc-config-transport','src-wn-2608-100274-bp-change','src-wn-2608-100274-product'}
        ids={x.get('source_id',x.get('id')) for x in r['records']}
        require(ids==expected,'Unrelated release-registry sources are presented as activity evidence: '+','.join(sorted(ids-expected)))
    scenario('S06','Retrieve only evidence linked to the selected activity','100274 profile and local source records link exactly three source IDs',s06)

    def s07():
        troot=work/'paging-root';sha=file_hash(small);snapshots.publish_file(troot,small,sha)
        atomic_json(troot/'current.json',{'sha256':sha,'generation':1,'previous':None})
        request={'kind':'object','objectType':'CLAS','key':'CL_PRINT_QUEUE_UTILS','section':'declaration','maxChars':100}
        first=mcp.call(troot,'yula_get',request)
        require(first.get('snapshot')==sha,'No snapshot reference is returned for continuation.')
        changed=altered('paging-next')
        with connect(changed,readonly=False) as db:db.execute("update objects set description='New snapshot'")
        newsha=file_hash(changed);snapshots.publish_file(troot,changed,newsha)
        atomic_json(troot/'current.json',{'sha256':newsha,'generation':2,'previous':sha})
        second=mcp.call(troot,'yula_get',{**request,'offset':first['nextOffset'],'snapshot':sha})
        require(second['snapshot']==sha and second['sha256']==first['sha256'],'Continuation switched to a different snapshot.')
    scenario('S07','Continue a paged contract while the active corpus changes','Immutable content-addressed snapshots must bind all pages of one response',s07)

    def s08():
        p=altered('help');text='a'*6000+'BC'
        with connect(p,readonly=False) as db:
            d=dict(db.execute('select * from doc_documents limit 1').fetchone());old_language=d['language']
            payload={'mode':'topic','document':{k:v for k,v in d.items() if k!='topics'},'build':'test',
                     'topics':[{'topic_id':'joined-test','topic_title':'Text integrity','url':'https://help.sap.com/docs/a/b/c','breadcrumb':'','text':text}]}
            adapters.apply_help(db,payload)
            r=query.get(db,'topic',d['document_id']+':joined-test',maxChars=12000)
            require(r['text']==text,'Inserted separators corrupt a newly fetched non-overlapping topic.')
            payload['document']['language']='de-DE' if old_language!='de-DE' else 'fr-FR'
            adapters.apply_help(db,payload)
            require(db.execute('select language from doc_documents where document_id=?',(d['document_id'],)).fetchone()[0]==old_language,'A new language relabels untouched old-language topics.')
    scenario('S08','Preserve documentation text and edition/language partitions','A 6002-character source must reassemble exactly; original language metadata stays immutable',s08)

    def s09():
        r={'kind':'lesson','id':'invalid-proof','release':'2608','revision':1,'title':'Bad proof','status':'validated',
           'sources':[{'id':'source','url':'https://help.sap.com/docs/SAP_S4HANA_CLOUD','checkedAt':now(),'claim':'Test claim'}],
           'verification':[123],'successfulCases':'x','applicability':'test','rootCause':'test','resolution':'test','rollback':'test'}
        rejected(lambda:records.validate_record(r),'Numeric verification and string-valued cases promoted to validated.')
        r={'kind':'research','id':'future','release':'2608','revision':1,'title':'Future check','status':'researched','activityId':'100274',
           'sources':[{'id':'source','url':'https://help.sap.com/docs/SAP_S4HANA_CLOUD','checkedAt':'2099-01-01T00:00:00Z','claim':'Test claim'}]}
        rejected(lambda:records.validate_record(r),'A future checkedAt timestamp is accepted as source evidence.')
    scenario('S09','Keep malformed/future evidence out of verified knowledge','Typed verification/case IDs and non-future checked timestamps are required evidence invariants',s09)

    def s10():
        p=altered('withdrawal');legacy=work/'config-source.sqlite';source_tree=work/'canonical'
        (source_tree/'data/releases/2608/catalog').mkdir(parents=True)
        with connect(small) as src:
            out=sqlite3.connect(legacy)
            for table in adapters.CONFIG_TABLES:
                sql=src.execute('select sql from sqlite_master where name=?',('cfg_'+table,)).fetchone()[0]
                out.execute(sql.replace('cfg_'+table,table,1))
                for row in src.execute('select * from cfg_'+table):out.execute('insert into '+table+' values ('+','.join('?' for _ in row)+')',tuple(row))
            out.commit();out.close()
        with connect(p,readonly=False) as db:
            adapters.apply_configuration(db,{'path':str(legacy),'root':str(source_tree)},'configuration-root')
            require(db.execute('select count(*) from cfg_profiles').fetchone()[0]==0,'Withdrawn canonical dossiers survive the replacement snapshot.')
    scenario('S10','Withdraw an old dossier while preserving immutable history','A complete configuration-root import no longer contains the old profile/source files',s10)

    def s11():
        p=altered('missing-fts')
        with connect(p,readonly=False) as db:db.execute('delete from object_knowledge_fts where rowid=(select min(rowid) from object_knowledge_fts)')
        rejected(lambda:validate_database(p),'Logical object/FTS mismatch passes database validation.')
    scenario('S11','Detect a logically incomplete retrieval index','SQLite structural integrity alone does not prove one-to-one object/FTS coverage',s11)

    def s12():
        troot=work/'replay-root';sha=file_hash(small);snapshots.publish_file(troot,small,sha)
        plan={'format':'yula-update-plan/1','createdAt':now(),'baseSha256':sha,'baseGeneration':1,'candidateSha256':sha,'changed':True,'sources':[]}
        plan_path=work/'replayed-plan.json';atomic_json(plan_path,plan);ph=digest(plan)
        atomic_json(troot/'current.json',{'sha256':sha,'generation':2,'previous':sha,'planSha256':ph})
        with (troot/'snapshots'/(sha+'.sqlite')).open('ab') as f:f.write(b'corruption')
        rejected(lambda:snapshots.apply(troot,plan_path,ph),'Successful-plan replay skips the active snapshot hash check.')
    scenario('S12','Reject corruption on an idempotent apply replay','The active file must match its content-addressed hash even for an already-applied plan',s12)

    report={'pluginVersion':json.loads((plugin/'.codex-plugin/plugin.json').read_text())['version'],
            'scenarioCount':len(results),'passed':sum(r['status']=='PASS' for r in results),'scenarios':results,
            'measurement':'UTF-8 serialized response bytes; single-run diagnostic latency, not a benchmark',
            'modelExecution':'not run','tokens':'not measured: no verified model-specific tokenizer/counter available'}
    Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Scenarios',report['passed'],'/',len(results),flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
