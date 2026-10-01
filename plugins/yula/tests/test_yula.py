"""Behavioral contracts; isolated reduced fixtures derive from the shipped real corpus."""
from pathlib import Path
import copy
import gzip
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(PLUGIN / "runtime"))
from yula import adapters, mcp, query, snapshots, updates
from yula.common import APPLICATION_ID, YulaError, atomic_json, connect, digest, encode, file_hash, load_json, now, validate_database, writer_lock
from yula.records import apply_records, validate_record
from yula.seed import unpack_seed


def fixture(target):
    with unpack_seed(target.parent) as seed, connect(seed) as source:
        db = sqlite3.connect(target)
        db.row_factory = sqlite3.Row
        shadow = {r[1] for r in source.execute("pragma table_list") if r[2] == "shadow"}
        for name, sql in source.execute("select name,sql from sqlite_master where type='table' and sql is not null order by rowid"):
            if name not in shadow and not name.startswith("sqlite_"):
                db.execute(sql)
        def copy_table(table, clause="1=1", args=()):
            for row in source.execute(f'select * from "{table}" where {clause}', args):
                db.execute('insert into "' + table + '" values (' + ','.join('?' for _ in row) + ')', tuple(row))
        copy_table("objects", "object_name in ('CL_PRINT_QUEUE_UTILS','CL_ABAP_CONTEXT_INFO') and object_type='CLAS'")
        ids = [r[0] for r in db.execute("select id from objects")]
        placeholders = ','.join('?' for _ in ids)
        for table in ("evidence", "members", "object_capabilities", "recipes", "object_content"):
            copy_table(table, f"object_id in ({placeholders})", ids)
        for table in ("capabilities", "capability_aliases", "yula_aliases", "corpus_snapshots", "yula_sources", "yula_migrations"):
            copy_table(table)
        for table in ("released_catalog", "corpus_ingestion"):
            copy_table(table, "object_name in ('CL_PRINT_QUEUE_UTILS','CL_ABAP_CONTEXT_INFO') and object_type='CLAS'")
        copy_table("object_knowledge_fts", "object_name in ('CL_PRINT_QUEUE_UTILS','CL_ABAP_CONTEXT_INFO')")
        for table in ("cfg_activities", "cfg_profiles"):
            copy_table(table, "activity_id='100274'")
        copy_table("cfg_sources", "activity_id in ('','100274')")
        for table in ("cfg_documents", "cfg_documents_fts"):
            copy_table(table, "entity_id='100274'")
        topic = source.execute("select document_id,topic_id from doc_chunks limit 1").fetchone()
        copy_table("doc_documents", "document_id=?", (topic[0],))
        copy_table("doc_chunks", "document_id=? and topic_id=?", topic)
        if source.execute("select 1 from sqlite_master where name='doc_topic_evidence'").fetchone():
            copy_table('doc_topic_evidence','document_id=? and topic_id=?',topic)
        # This is a reduced fixture, not the full catalog/topic population.
        db.execute("""update corpus_snapshots set entry_count=(select count(*) from released_catalog c where c.edition=corpus_snapshots.edition and c.release_state!='notListed'),
            released_count=(select count(*) from released_catalog c where c.edition=corpus_snapshots.edition and c.release_state='released')""")
        db.execute('update doc_documents set topics=(select count(distinct topic_id) from doc_chunks c where c.document_id=doc_documents.document_id)')
        db.execute(f"pragma application_id={APPLICATION_ID}");db.execute("pragma user_version=1")
        db.commit(); db.close()


class CatalogFetcher:
    def __init__(self, names=None, failure=False):
        self.failure = failure
        self.payload = {"formatVersion": "1", "objectReleaseInfo": [
            {"tadirObject": "CLAS", "tadirObjName": name, "objectType": "CLAS", "objectKey": name,
             "softwareComponent": "SAP_BASIS", "applicationComponent": "BC", "state": "released"}
            for name in (names or ["CL_PRINT_QUEUE_UTILS", "CL_ABAP_CONTEXT_INFO", "CL_YULA_NEW_OFFICIAL_FIXTURE"])]}
    def get(self, url, **options):
        if self.failure:
            raise YulaError("SOURCE_UNREACHABLE", "Fixture network outage")
        raw = encode(self.payload)
        return raw, {"fetchedAt": now(), "sha256": digest(raw)}
    def json(self, url, **options):
        raise YulaError("SOURCE_UNREACHABLE", "Fixture help failure after catalog staging")


class YulaContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base = Path(os.environ.get("YULA_TEST_ROOT", tempfile.gettempdir())).resolve()
        base.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="yula-tests-", dir=base)
        cls.base = Path(cls.temp.name).resolve()
        assert cls.base.is_relative_to(base)
        cls.fixture = cls.base / "fixture.sqlite"
        fixture(cls.fixture)
        validate_database(cls.fixture)
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def setUp(self):
        self.root = self.base / self._testMethodName
        self.root.mkdir()
        sha = file_hash(self.fixture)
        snapshots.publish_file(self.root, self.fixture, sha)
        atomic_json(self.root / "current.json", {"sha256": sha, "generation": 1, "previous": None})
        self.sha = sha
        self.config = self.root / "sources.json"
        atomic_json(self.config, {"version": 1, "sources": [{"id": "sap-released", "kind": "released-catalog", "enabled": True}]})
    def call(self, name, args):
        return mcp.call(self.root, name, args)
    def plan(self, fetcher=None):
        return updates.check(self.root, self.config, fetcher=fetcher or CatalogFetcher())
    def assertCode(self, code, operation):
        with self.assertRaises(YulaError) as context:
            operation()
        self.assertEqual(code, context.exception.code)

    def test_exact_release_gate_and_no_target_pass(self):
        result = self.call("yula_check", {"objects": [
            {"objectType": "CLAS", "objectName": "CL_PRINT_QUEUE_UTILS"},
            {"objectType": "CLAS", "objectName": "Z_NOT_A_RELEASED_OBJECT"}]})
        self.assertEqual([True, False], [x["eligible"] for x in result["results"]])
        self.assertEqual("REVIEW_REQUIRED", result["results"][0]["decision"])
        self.assertEqual("unverified", result["targetTenant"])

    def test_turkish_capability_retrieval(self):
        result = self.call("yula_search", {"domain": "objects", "query": "PDF yazdırmak"})
        self.assertEqual("CL_PRINT_QUEUE_UTILS", result["results"][0]["objectName"])
        self.assertEqual("curated_mapping", result["results"][0]["matchEvidence"])

    def test_member_signature_and_gap(self):
        result = self.call("yula_get", {"kind": "object", "key": "CL_PRINT_QUEUE_UTILS", "objectType": "CLAS", "section": "members", "member": "CREATE_QUEUE_ITEM_BY_DATA"})
        self.assertTrue(result["members"])
        self.assertIn("CREATE_QUEUE_ITEM_BY_DATA", result["members"][0]["signature"].upper())
        missing = self.call("yula_get", {"kind": "object", "key": "CL_PRINT_QUEUE_UTILS", "objectType": "CLAS", "section": "members", "member": "NO_SUCH_MEMBER"})
        self.assertEqual("MEMBER_MISSING", missing["signal"])

    def test_hash_verified_public_content_paging(self):
        args = {"kind": "object", "key": "CL_PRINT_QUEUE_UTILS", "objectType": "CLAS", "section": "declaration", "maxChars": 100}
        first = self.call("yula_get", args)
        second = self.call("yula_get", {**args, "offset": first["nextOffset"]})
        self.assertEqual(100, first["nextOffset"])
        self.assertEqual(100, second["offset"])
        self.assertEqual(first["sha256"], second["sha256"])

    def test_missing_signature_never_invented(self):
        path = self.root / "modified.sqlite";snapshots.clone_database(self.fixture, path)
        with connect(path, readonly=False) as db:
            db.execute("update members set signature=null where name='CREATE_QUEUE_ITEM_BY_DATA'")
            result = query.object_context(db, "CLAS", "CL_PRINT_QUEUE_UTILS", "members", "CREATE_QUEUE_ITEM_BY_DATA")
            self.assertEqual("missing", result["members"][0]["signatureStatus"])

    def test_configuration_identity_and_dossier(self):
        result = self.call("yula_get", {"kind": "activity", "key": "100274", "release": "2608"})
        self.assertEqual("Configure Matching and Duplicate Check", result["name"])
        self.assertEqual("Obsolete", result["lifecycle"])
        result = self.call("yula_get", {"kind": "activity", "key": "100274", "release": "2608", "section": "sources", "limit": 1})
        self.assertTrue(result["records"])
        self.assertCode("RELEASE_MISSING", lambda: self.call("yula_get", {"kind": "activity", "key": "100274", "release": "9999"}))

    def test_search_sql_fts_punctuation_and_empty(self):
        result = self.call("yula_search", {"domain": "objects", "query": 'print:queue ("PDF") - x'})
        self.assertTrue(result["results"])
        result = self.call("yula_search", {"domain": "objects", "query": "unfindable_yula_987654321"})
        self.assertEqual("NO_MATCH", result["signal"])

    def test_docs_search_and_page(self):
        _, path = snapshots.active(self.root)
        with connect(path) as db:
            item = db.execute("select document_id,topic_id,topic_title from doc_chunks limit 1").fetchone()
        result = self.call("yula_get", {"kind": "topic", "key": item[0] + ":" + item[1], "maxChars": 80})
        self.assertLessEqual(len(result["text"]), 80)
        result = self.call("yula_search", {"domain": "docs", "query": item[2], "includeOtherEditions": True})
        self.assertTrue(result["results"])

    def test_argument_bounds(self):
        self.assertCode("INVALID_ARGUMENT", lambda: self.call("yula_search", {"domain": "objects", "query": "print", "limit": 500}))
        self.assertCode("INVALID_ARGUMENT", lambda: self.call("yula_status", {"verify": "true"}))
        self.assertCode("INVALID_ARGUMENT", lambda: self.call("yula_get", {"kind": "object", "key": "X", "unrecognized": True}))

    def test_check_is_nonmutating_apply_and_rollback(self):
        plan = self.plan()
        self.assertEqual(self.sha, snapshots.active(self.root)[0]["sha256"])
        result = snapshots.apply(self.root, plan["plan"], plan["planSha256"])
        self.assertNotEqual(self.sha, result["sha256"])
        self.assertEqual(self.sha, result["backup"])
        gap = self.call("yula_get", {"kind": "object", "objectType": "CLAS", "key": "CL_YULA_NEW_OFFICIAL_FIXTURE"})
        self.assertEqual("ENRICHMENT_MISSING", gap["signal"])
        restored = snapshots.rollback(self.root, result["sha256"])
        self.assertEqual(self.sha, restored["sha256"])

    def test_second_update_is_content_idempotent(self):
        first = self.plan(); snapshots.apply(self.root, first["plan"], first["planSha256"])
        active_before = snapshots.active(self.root)[0]
        second = self.plan()
        self.assertFalse(second["changed"])
        result = snapshots.apply(self.root, second["plan"], second["planSha256"])
        self.assertFalse(result["applied"])
        self.assertEqual(active_before, snapshots.active(self.root)[0])

    def test_missing_source_preserves_active(self):
        self.assertCode("SOURCE_UNREACHABLE", lambda: self.plan(CatalogFetcher(failure=True)))
        self.assertEqual(self.sha, snapshots.active(self.root)[0]["sha256"])

    def test_later_source_failure_discards_partial_stage(self):
        data=load_json(self.config)
        data["sources"].append({"id":"help", "kind":"sap-help", "enabled":True, "url":"https://help.sap.com/docs/abap-cloud/abap-cloud/why-abap-cloud"})
        atomic_json(self.config,data)
        self.assertCode("SOURCE_UNREACHABLE", self.plan)
        self.assertEqual(self.sha, snapshots.active(self.root)[0]["sha256"])
        self.assertFalse(list((self.root/"plans").glob("*/plan.json")))

    def test_plan_and_candidate_hash_binding(self):
        plan=self.plan()
        self.assertCode("PLAN_HASH_MISMATCH",lambda:snapshots.apply(self.root,plan["plan"],"0"*64))
        candidate=Path(plan["plan"]).parent/"candidate.sqlite"
        with candidate.open('ab') as f:f.write(b'corrupted')
        self.assertCode("CANDIDATE_CHANGED",lambda:snapshots.apply(self.root,plan["plan"],plan["planSha256"]))
        self.assertEqual(self.sha,snapshots.active(self.root)[0]["sha256"])

    def test_stale_plan_rejected(self):
        a=self.plan();b=self.plan(CatalogFetcher(["CL_PRINT_QUEUE_UTILS", "CL_ABAP_CONTEXT_INFO", "CL_YULA_DIFFERENT_FIXTURE"]))
        snapshots.apply(self.root,a["plan"],a["planSha256"])
        self.assertCode("STALE_PLAN",lambda:snapshots.apply(self.root,b["plan"],b["planSha256"]))

    def test_replaying_successful_apply_is_idempotent(self):
        a=self.plan();first=snapshots.apply(self.root,a["plan"],a["planSha256"])
        again=snapshots.apply(self.root,a["plan"],a["planSha256"])
        self.assertEqual("already_applied",again["status"])
        self.assertEqual(first["sha256"],again["sha256"])

    def test_writer_lock_prevents_competing_publish(self):
        plan=self.plan()
        with writer_lock(self.root):
            self.assertCode("WRITER_BUSY",lambda:snapshots.apply(self.root,plan["plan"],plan["planSha256"]))

    def test_interrupted_publication_preserves_reader_and_retries(self):
        from unittest.mock import patch
        plan=self.plan()
        old_path=snapshots.active(self.root)[1]
        with connect(old_path) as reader:
            old_count=reader.execute('select count(*) from released_catalog').fetchone()[0]
            with patch('yula.snapshots.atomic_json',side_effect=OSError('simulated pointer commit failure')):
                with self.assertRaises(OSError):snapshots.apply(self.root,plan['plan'],plan['planSha256'])
            self.assertEqual(self.sha,snapshots.active(self.root)[0]['sha256'])
            snapshots.apply(self.root,plan['plan'],plan['planSha256'])
            self.assertEqual(old_count,reader.execute('select count(*) from released_catalog').fetchone()[0])
        self.assertNotEqual(self.sha,snapshots.active(self.root)[0]['sha256'])

    def test_topic_update_never_relabels_an_older_release(self):
        path=self.root/'help-version.sqlite';snapshots.clone_database(self.fixture,path)
        with connect(path,readonly=False) as db:
            original=db.execute('select * from doc_documents limit 1').fetchone()
            old_id,old_version=original['document_id'],original['version']
            payload={'mode':'topic','document':{'document_id':old_id,'version':'test-new-release','title':'New version','root_url':'https://help.sap.com/docs/test/manual/topic','scope':'Public Edition','language':'en-US'},
                     'topics':[{'topic_id':'versioned-topic','topic_title':'New topic','url':'https://help.sap.com/docs/test/manual/topic','breadcrumb':'','text':'New release content.'}]}
            adapters.apply_help(db,payload)
            self.assertEqual(old_version,db.execute('select version from doc_documents where document_id=?',(old_id,)).fetchone()[0])
            self.assertEqual(2,db.execute('select count(*) from doc_documents').fetchone()[0])

    def test_unsupported_schema_does_not_reseed(self):
        bad=self.root/'unsupported.sqlite';snapshots.clone_database(self.fixture,bad)
        with connect(bad,readonly=False) as db:db.execute('pragma user_version=999')
        self.assertCode("SCHEMA_UNSUPPORTED",lambda:validate_database(bad))
        self.assertEqual(self.sha,snapshots.init(self.root)["sha256"])

    def test_empty_missing_and_corrupt_corpus(self):
        self.assertCode("CORPUS_MISSING",lambda:connect(self.root/'absent.sqlite'))
        bad=self.root/'empty.sqlite';snapshots.clone_database(self.fixture,bad)
        c=sqlite3.connect(bad);c.execute('pragma foreign_keys=off');c.execute('delete from objects');c.commit();c.close()
        self.assertCode("CORPUS_CORRUPT",lambda:validate_database(bad))

    def test_lesson_requires_verified_cases(self):
        r={"kind":"lesson","id":"lesson-test","release":"2608","revision":1,"title":"Test lesson","status":"validated",
           "sources":[{"id":"source","url":"https://help.sap.com/docs/SAP_S4HANA_CLOUD","checkedAt":now(),"claim":"Fixture claim"}],
           "verification":["fixture"],"applicability":"fixture","rootCause":"fixture","resolution":"fixture","rollback":"fixture"}
        self.assertCode("LESSON_GATE",lambda:validate_record(r))
        r["successfulCases"]=["case-1"]
        self.assertEqual("validated",validate_record(r)["status"])

    def test_local_record_revision_is_immutable(self):
        records=self.root/'records.json'
        r={"kind":"incident","id":"incident-test","release":"2608","revision":1,"title":"Test incident","status":"observed","activityIds":["100274"],"summary":"Sanitized reproduction"}
        atomic_json(records,[r]);atomic_json(self.config,{"version":1,"sources":[{"id":"records","kind":"knowledge-records","enabled":True,"path":str(records)}]})
        first=self.plan();snapshots.apply(self.root,first["plan"],first["planSha256"])
        r["title"]="Changed immutable revision";atomic_json(records,[r])
        self.assertCode("IMMUTABLE_REVISION",self.plan)

    def test_native_metadata_is_read_only_and_identity_bound(self):
        class ADT:
            def get(s,url,**options):
                self.assertNotIn('/source/',url);self.assertIn('/sap/bc/adt/oo/classes/',url)
                return b'<class xmlns:adtcore="http://www.sap.com/adt/core" adtcore:name="CL_PRINT_QUEUE_UTILS" adtcore:description="Print API"/>',{}
        spec={"origin":"https://example.sap.invalid","objects":[{"objectType":"CLAS","objectName":"CL_PRINT_QUEUE_UTILS"}]}
        with connect(self.fixture) as db:
            payload,_,_=adapters.adt_metadata(ADT(),spec,db)
            self.assertFalse(payload[0]["signatureRefresh"])
            spec["objects"][0]["objectName"]="Z_NOT_RELEASED"
            self.assertCode("OBJECT_NOT_RELEASED",lambda:adapters.adt_metadata(ADT(),spec,db))

    def test_legacy_objects_import_and_noop(self):
        atomic_json(self.config,{"version":1,"sources":[{"id":"local-objects","kind":"legacy-objects","enabled":True,"path":str(self.fixture)}]})
        plan=self.plan();snapshots.apply(self.root,plan['plan'],plan['planSha256'])
        self.assertFalse(self.plan()['changed'])
        self.assertTrue(self.call('yula_get',{'kind':'object','objectType':'CLAS','key':'CL_PRINT_QUEUE_UTILS','section':'members','member':'CREATE_QUEUE_ITEM_BY_DATA'})['members'])

    def test_legacy_import_rejects_bad_content_hash(self):
        bad=self.root/'bad-source.sqlite';snapshots.clone_database(self.fixture,bad)
        with connect(bad,readonly=False) as db:db.execute("update object_content set source_sha256=?",('0'*64,))
        atomic_json(self.config,{"version":1,"sources":[{"id":"bad-objects","kind":"legacy-objects","enabled":True,"path":str(bad)}]})
        self.assertCode('CONTENT_CORRUPT',self.plan)
        self.assertEqual(self.sha,snapshots.active(self.root)[0]['sha256'])

    def test_configuration_database_import_preserves_local_records(self):
        legacy=self.root/'config.sqlite'
        with connect(self.fixture) as source:
            out=sqlite3.connect(legacy)
            for table in adapters.CONFIG_TABLES:
                original='cfg_'+table
                sql=source.execute('select sql from sqlite_master where name=?',(original,)).fetchone()[0]
                out.execute(sql.replace(original,table,1))
                for row in source.execute('select * from '+original):
                    out.execute('insert into '+table+' values ('+','.join('?' for _ in row)+')',tuple(row))
            out.commit();out.close()
        records=self.root/'records.json'
        record={"kind":"incident","id":"persist-me","release":"2608","revision":1,"title":"Preserved incident","status":"observed","activityIds":["100274"],"summary":"Preserve this independently curated record"}
        atomic_json(records,[record])
        atomic_json(self.config,{"version":1,"sources":[{"id":"records","kind":"knowledge-records","enabled":True,"path":str(records)}]})
        plan=self.plan();snapshots.apply(self.root,plan['plan'],plan['planSha256'])
        atomic_json(self.config,{"version":1,"sources":[{"id":"local-config","kind":"configuration-db","enabled":True,"path":str(legacy)}]})
        plan=self.plan();snapshots.apply(self.root,plan['plan'],plan['planSha256'])
        result=self.call('yula_get',{'kind':'record','key':'record:incident:2608:persist-me'})
        self.assertIn('Preserved incident',result['text'])

    def test_confirmed_dependency_requires_existing_endpoints(self):
        path=self.root/'dependency.sqlite';snapshots.clone_database(self.fixture,path)
        record={'kind':'dependency','id':'missing-endpoint','release':'2608','revision':1,'title':'Missing target','status':'candidate',
                'sourceActivityId':'100274','targetActivityId':'does-not-exist','relation':'recommended_before','evidenceLevel':'hypothesis'}
        with connect(path,readonly=False) as db:
            self.assertCode('ACTIVITY_MISSING',lambda:apply_records(db,[validate_record(record)]))

    def test_mcp_stdio_protocol_and_tools(self):
        requests=[{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"contract-test","version":"1"}}},
                  {"jsonrpc":"2.0","method":"notifications/initialized"},
                  {"jsonrpc":"2.0","id":2,"method":"tools/list"},
                  {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"yula_get","arguments":{"kind":"activity","key":"100274","release":"2608"}}},
                  {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"yula_check","arguments":{"objects":[]}}}]
        result=subprocess.run([sys.executable,'-X','utf8','-B',str(PLUGIN/'scripts/yula.py'),'--data-root',str(self.root),'mcp'],
            input=b'\n'.join(encode(r) for r in requests)+b'\n',capture_output=True,timeout=30)
        self.assertEqual(0,result.returncode,result.stderr.decode())
        messages=[json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(4,len(messages))
        self.assertEqual('yula',messages[0]['result']['serverInfo']['name'])
        self.assertEqual(4,len(messages[1]['result']['tools']))
        self.assertFalse(messages[2]['result'].get('isError',False))
        self.assertTrue(messages[3]['result']['isError'])


if __name__=='__main__':
    unittest.main()
