"""Additional maintenance/provenance controls discovered by the 1.2.0 review."""
from pathlib import Path
import importlib.util
import json
import os
import sqlite3
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'runtime'))
from yula import adapters,migrations,mcp,query,snapshots,updates
from yula.common import connect,file_hash,atomic_json,now,YulaError


class ReviewControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_yula
        base=Path(os.environ.get('YULA_TEST_ROOT',tempfile.gettempdir())).resolve();base.mkdir(parents=True,exist_ok=True)
        cls.tmp=tempfile.TemporaryDirectory(prefix='yula-review-',dir=base);cls.base=Path(cls.tmp.name)
        cls.seed=cls.base/'seed.sqlite';test_yula.fixture(cls.seed)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):
        self.db=self.base/(self._testMethodName+'.sqlite');snapshots.clone_database(self.seed,self.db)
    def test_invalid_receipt_does_not_break_read(self):
        root=self.base/'bad-receipt';sha=file_hash(self.db);snapshots.publish_file(root,self.db,sha)
        atomic_json(root/'current.json',{'sha256':sha,'generation':1,'previous':None})
        (root/'checks').mkdir();(root/'checks/sap-released.json').write_text('{bad-json')
        result=mcp.call(root,'yula_get',{'kind':'object','objectType':'CLAS','key':'CL_PRINT_QUEUE_UTILS'})
        self.assertEqual('CL_PRINT_QUEUE_UTILS',result['objectName'])
    def test_failed_latest_ingestion_cannot_supply_a_signature(self):
        with connect(self.db,readonly=False) as db:
            db.execute("update corpus_ingestion set status='failed' where object_name='CL_PRINT_QUEUE_UTILS'")
            r=query.object_context(db,'CLAS','CL_PRINT_QUEUE_UTILS','members','CREATE_QUEUE_ITEM_BY_DATA')
            self.assertEqual('SIGNATURE_UNAVAILABLE',r['signal']);self.assertFalse(r['members'])
    def test_private_scope_is_not_a_public_default(self):
        with connect(self.db,readonly=False) as db:
            payload={'mode':'topic','document':{'document_id':'private-only','version':'2025','language':'en-US','title':'Private guide',
                     'root_url':'https://help.sap.com/docs/SAP_S4HANA_CLOUD_PRIVATE_EDITION/x/y','scope':'Private Edition'},
                     'topics':[{'topic_id':'private-topic','topic_title':'PrivateSentinel','url':'https://help.sap.com/docs/SAP_S4HANA_CLOUD_PRIVATE_EDITION/x/y','breadcrumb':'','text':'PrivateSentinel'}]}
            adapters.apply_help(db,payload)
            self.assertFalse(query.search(db,'docs','PrivateSentinel')['results'])
            self.assertTrue(query.search(db,'docs','PrivateSentinel',includeOtherEditions=True)['results'])
    def test_topic_provenance_detects_out_of_band_text_changes(self):
        with connect(self.db,readonly=False) as db:
            migrations.ensure_extensions(db)
            doc,topic=db.execute('select document_id,topic_id from doc_chunks limit 1').fetchone()
            db.execute('update doc_chunks set text=? where document_id=? and topic_id=?',('changed',doc,topic))
            with self.assertRaises(YulaError) as ctx:query.get(db,'topic',doc+':'+topic)
            self.assertEqual('TOPIC_EVIDENCE_STALE',ctx.exception.code)
    def test_unknown_adapter_fails_before_ingestion(self):
        root=self.base/'bad-source-kind';root.mkdir()
        config=root/'sources.json';atomic_json(config,{'version':1,'sources':[{'id':'broken','kind':'unrecognized','enabled':True}]})
        with self.assertRaises(YulaError):
            specs,base=updates.load_sources(config)
            with connect(self.db) as db:adapters.prepare(specs[0],base,root,None,db)

    def test_copy_preserves_public_signature_literals(self):
        source=self.base/'signature-source.sqlite';snapshots.clone_database(self.seed,source)
        signature="METHODS send IMPORTING endpoint TYPE string DEFAULT 'https://example.org/public'."
        with connect(source,readonly=False) as db:
            db.execute("update members set signature=? where name='CREATE_QUEUE_ITEM_BY_DATA'",(signature,))
        with connect(source) as src,connect(self.db,readonly=False) as dst:
            dst.execute('delete from members')
            adapters.copy_rows(src,dst,'members','members')
            self.assertEqual(signature,dst.execute("select signature from members where name='CREATE_QUEUE_ITEM_BY_DATA'").fetchone()[0])

    def test_member_selector_never_silently_becomes_class_only_summary(self):
        with connect(self.db) as db:
            r=query.object_context(db,'CLAS','CL_PRINT_QUEUE_UTILS',member='NO_SUCH_MEMBER')
            self.assertEqual('MEMBER_MISSING',r['signal'])
            self.assertTrue(r['availability']['eligible'])


if __name__=='__main__':unittest.main()
