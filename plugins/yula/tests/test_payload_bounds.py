"""Regression contracts for typed summaries and bounded activity record reads."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(PLUGIN / "runtime"))
from yula import mcp, query, snapshots
from yula.common import YulaError, atomic_json, connect, encode, file_hash


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class PayloadBoundsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_yula
        base = Path(os.environ.get("YULA_TEST_ROOT", tempfile.gettempdir())).resolve()
        base.mkdir(parents=True, exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="yula-payload-", dir=base)
        cls.base = Path(cls.temp.name).resolve()
        assert cls.base.is_relative_to(base)
        cls.fixture = cls.base / "fixture.sqlite"
        test_yula.fixture(cls.fixture)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.root = self.base / self._testMethodName
        self.root.mkdir()
        self.db = self.root / "fixture.sqlite"
        snapshots.clone_database(self.fixture, self.db)

    def profile(self, **changes):
        with connect(self.db, readonly=False) as db:
            row = db.execute("select json from cfg_profiles where release='2608' and activity_id='100274'").fetchone()
            profile = json.loads(row[0])
            profile.update(changes)
            db.execute("update cfg_profiles set json=? where release='2608' and activity_id='100274'", (compact(profile),))
        return profile

    def publish(self, generation=1):
        sha = file_hash(self.db)
        snapshots.publish_file(self.root, self.db, sha)
        atomic_json(self.root / "current.json", {"sha256": sha, "generation": generation, "previous": None})
        return sha

    def call(self, **arguments):
        return mcp.call(self.root, "yula_get", {"kind": "activity", "key": "100274", "release": "2608", **arguments})

    def assertCode(self, code, operation):
        with self.assertRaises(YulaError) as context:
            operation()
        self.assertEqual(code, context.exception.code)

    def test_all_json_summary_types_preserve_their_representation(self):
        values = ["A plain summary", {"purpose": "雪", "count": 2}, ["one", {"two": True}], 17, 1.25, True, None]
        for value in values:
            with self.subTest(value=value):
                self.profile(summary=value)
                with connect(self.db) as db:
                    result = query.get(db, "activity", "100274", release="2608")
                self.assertEqual(value if isinstance(value, str) else compact(value), result["summary"])
                if isinstance(value, str):
                    self.assertNotIn("summaryRepresentation", result)
                else:
                    self.assertEqual("json", result["summaryRepresentation"])
                    self.assertEqual(value, json.loads(result["summary"]))
                self.assertNotIn("summaryTruncated", result)

    def test_structured_summary_truncation_keeps_complete_dossier_route(self):
        value = {"purpose": "Quoted \"text\" and 雪 " * 200, "steps": [1, 2, 3]}
        profile = self.profile(summary=value)
        self.publish()
        summary = self.call(maxChars=37)
        self.assertEqual(compact(value)[:37], summary["summary"])
        self.assertTrue(summary["summaryTruncated"])
        self.assertEqual("dossier", summary["readComplete"])
        self.assertEqual("json", summary["summaryRepresentation"])
        chunks = []
        offset = 0
        while True:
            page = self.call(section="dossier", offset=offset, maxChars=503, snapshot=summary["snapshot"])
            chunks.append(page["text"])
            if page["nextOffset"] is None:
                break
            self.assertGreater(page["nextOffset"], offset)
            offset = page["nextOffset"]
        self.assertEqual(profile, json.loads("".join(chunks)))

    def test_record_batch_bounds_preserve_order_and_record_offsets(self):
        records = [{"id": i, "body": "a" * 22000} for i in range(5)]
        self.profile(fixtureRecords=records)
        sha = self.publish()
        reconstructed = []
        offset = 0
        while True:
            page = self.call(section="fixtureRecords", offset=offset, limit=20, snapshot=sha)
            self.assertNotIn("representation", page)
            self.assertLessEqual(len(compact(page)), 48000)
            self.assertEqual(5, page["total"])
            reconstructed.extend(page["records"])
            if page["nextOffset"] is None:
                break
            self.assertEqual(offset + len(page["records"]), page["nextOffset"])
            offset = page["nextOffset"]
        self.assertEqual(records, reconstructed)

    def test_escaped_atomic_record_pages_are_lossless_and_snapshot_pinned(self):
        record = {"body": '"\\\n\t\r\x01雪🙂' * 9000, "nested": {"values": [None, True, 0, {"quote": '"'}]}}
        records = [{"id": "before"}, record, {"id": "after"}]
        self.profile(fixtureRecords=records)
        with connect(self.db, readonly=False) as db:
            db.execute("insert or replace into yula_review_flags values (?,?,?,?)", ("2608", "100274", "fixture-review", "2026-09-30T00:00:00Z"))
        sha = self.publish()
        leading = self.call(section="fixtureRecords", limit=20)
        self.assertEqual([records[0]], leading["records"])
        self.assertEqual(1, leading["nextOffset"])
        first = self.call(section="fixtureRecords", offset=1, limit=20, maxChars=12000, snapshot=sha)
        self.assertEqual("json_record_page", first["representation"])
        # Change the active pointer between pages; the selected snapshot must stay fixed.
        self.profile(fixtureRecords=[{"id": "changed-active"}])
        with connect(self.db, readonly=False) as db:
            db.execute("delete from yula_review_flags")
        self.assertNotEqual(sha, self.publish(generation=2))
        chunks = []
        page = first
        expected_offset = 0
        while True:
            self.assertEqual(sha, page["snapshot"])
            self.assertEqual(first["reviewFlags"], page["reviewFlags"])
            self.assertIn("fixture-review", [flag["reason"] for flag in page["reviewFlags"]])
            self.assertEqual(1, page["recordIndex"])
            self.assertEqual(expected_offset, page["textOffset"])
            self.assertEqual(len(compact(record)), page["totalChars"])
            self.assertEqual(3, page["total"])
            self.assertLessEqual(len(page["text"]), 12000)
            self.assertLessEqual(len(compact(page)), 48000)
            chunks.append(page["text"])
            if page["nextTextOffset"] is None:
                self.assertEqual(2, page["nextOffset"])
                break
            self.assertIsNone(page["nextOffset"])
            self.assertGreater(page["nextTextOffset"], expected_offset)
            expected_offset = page["nextTextOffset"]
            page = self.call(section="fixtureRecords", offset=1, limit=20, maxChars=12000, textOffset=expected_offset, snapshot=sha)
        self.assertEqual(compact(record), "".join(chunks))
        self.assertEqual(record, json.loads("".join(chunks)))
        trailing = self.call(section="fixtureRecords", offset=page["nextOffset"], snapshot=sha)
        self.assertEqual([records[2]], trailing["records"])
        self.assertIsNone(trailing["nextOffset"])

    def test_text_offset_rejects_invalid_types_ranges_and_sections(self):
        self.profile(fixtureRecords=[{"body": "a" * 60000}], shortRecords=[{"body": "short"}])
        self.publish()
        for value in (-1, "0", True, 1.5, None, 10**18 + 1):
            with self.subTest(value=value):
                self.assertCode("INVALID_ARGUMENT", lambda: self.call(section="fixtureRecords", textOffset=value))
        self.assertCode("OFFSET_RANGE", lambda: self.call(section="fixtureRecords", textOffset=10**18))
        for section in ("summary", "dossier", "shortRecords"):
            with self.subTest(section=section):
                self.assertCode("UNSUPPORTED_FILTER", lambda: self.call(section=section, textOffset=0))
        self.assertCode("UNSUPPORTED_FILTER", lambda: mcp.call(self.root, "yula_get", {"kind": "object", "objectType": "CLAS", "key": "CL_PRINT_QUEUE_UTILS", "textOffset": 0}))

    def test_variant_context_and_review_flags_survive_atomic_pages(self):
        self.profile(fixtureRecords=[{"body": "a" * 60000}])
        with connect(self.db, readonly=False) as db:
            row = dict(db.execute("select * from cfg_activities where release='2608' and activity_id='100274' limit 1").fetchone())
            row["source_row"] = 7777701
            columns = list(row)
            db.execute("insert into cfg_activities (" + ",".join(columns) + ") values (" + ",".join("?" for _ in columns) + ")", [row[key] for key in columns])
            db.execute("insert or replace into yula_review_flags values (?,?,?,?)", ("2608", "100274", "variant-fixture", "2026-09-30T00:00:00Z"))
        sha = self.publish()
        self.assertCode("UNSUPPORTED_FILTER", lambda: self.call(section="fixtureRecords", textOffset=0))
        first = self.call(section="fixtureRecords", sourceRow=7777701, snapshot=sha)
        self.assertEqual("VARIANT_DOSSIER_UNVERIFIED", first["contextStatus"])
        continuation = self.call(section="fixtureRecords", sourceRow=7777701, snapshot=sha, textOffset=first["nextTextOffset"])
        self.assertEqual(first["contextStatus"], continuation["contextStatus"])
        self.assertEqual(first["reviewFlags"], continuation["reviewFlags"])
        self.assertEqual(sha, continuation["snapshot"])

    def test_mcp_oversized_record_is_a_bounded_success_and_invalid_cursor_is_error(self):
        self.profile(fixtureRecords=[{"body": '"\\\n雪' * 20000}])
        self.publish()
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "yula_get", "arguments": {"kind": "activity", "key": "100274", "release": "2608", "section": "fixtureRecords", "maxChars": 12000}}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "yula_get", "arguments": {"kind": "activity", "key": "100274", "release": "2608", "section": "fixtureRecords", "textOffset": -1}}},
            {"jsonrpc": "2.0", "id": 4, "method": "resources/list"},
        ]
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(PLUGIN / "scripts/yula.py"), "--data-root", str(self.root), "mcp"], input=b"\n".join(encode(r) for r in requests) + b"\n", capture_output=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stderr.decode())
        messages = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertNotIn("resources", messages[0]["result"]["capabilities"])
        self.assertFalse(messages[1]["result"].get("isError", False))
        text = messages[1]["result"]["content"][0]["text"]
        self.assertLessEqual(len(text), 48000)
        self.assertEqual("json_record_page", json.loads(text)["representation"])
        self.assertTrue(messages[2]["result"]["isError"])
        self.assertEqual("INVALID_ARGUMENT", json.loads(messages[2]["result"]["content"][0]["text"])["error"])
        self.assertEqual(-32601, messages[3]["error"]["code"])


if __name__ == "__main__":
    unittest.main()
