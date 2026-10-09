# SPDX-License-Identifier: GPL-3.0-only
"""Regression probes for actual input closure, cache invalidation and review evidence."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bv2 as b
import delivery as d
import handoff3 as h
import preflight
import review_contract as review
from fixture_v4 import valid, seal


class EffectivenessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.doc = valid(self.root)
        self.spec, self.control = d.get_state(self.doc)

    def tearDown(self):
        self.temp.cleanup()

    def cache(self):
        initial = h.check_plan(self.doc, assets_root=self.root)
        for name, sha in initial['input_sha256'].items():
            h.record_check(self.doc, name, sha, 'PASS', self.root)

    def missing_reference(self):
        self.spec['references'] = [{'id': 'REF-DATA-01', 'kind': 'LIST',
          'path': 'fixture-talep-values.toon', 'pointer': '/values',
          'sha256': 'a' * 64, 'purpose': 'Approved business values'}]
        seal(self.doc)

    def test_renamed_asset_is_available_to_preflight_and_readers(self):
        old = self.spec['media'][0]['path']
        new = old.replace('screen-01', 'renamed-screen')
        self.spec['media'][0]['path'] = new
        self.control['assets'][0].update(path=new, source_path=old)
        seal(self.doc)
        packets = d.eval_request(self.doc, 3, self.root)
        self.assertTrue(Path(packets[0]['png_files'][0]['path']).samefile(self.root / old))
        self.assertTrue((self.root / old).exists())
        self.assertFalse((self.root / new).exists())

    def test_missing_reference_stops_before_issuing_requests(self):
        self.missing_reference()
        before = copy.deepcopy(self.control['eval_requests'])
        with self.assertRaisesRegex(b.Invalid, 'Preflight blocked'):
            d.eval_request(self.doc, 3, self.root)
        self.assertEqual(self.control['eval_requests'], before)

    def test_supplied_reference_content_and_blind_scenarios(self):
        self.missing_reference()
        data = b.encode({'values': ['approved']}).encode()
        path = self.spec['references'][0]['path']
        (self.root / path).write_bytes(data)
        self.spec['references'][0]['sha256'] = b.digest(data)
        self.control['assets'].append({'path': path, 'sha256': b.digest(data)})
        seal(self.doc)
        packets = d.eval_request(self.doc, 3, self.root)
        import source_pool
        self.assertEqual(source_pool.Reader(packets[0]).resolve(self.spec['references'][0]['id']), ['approved'])
        for packet in packets[:2]:
            self.assertTrue(all('expected' not in row for row in packet['spec']['test_cases']))
        self.assertEqual(packets[2]['spec']['test_cases'], self.spec['test_cases'])
        self.assertTrue(all('expected' in row for row in self.spec['test_cases']))

    def test_open_business_decision_stops_reader_spend(self):
        self.control['intake'] = [{'id': 'OPEN-01', 'status': 'OPEN', 'owner': 'CONSULTANT',
                                  'domain': 'BUSINESS', 'question': 'Who may approve?'}]
        with self.assertRaisesRegex(b.Invalid, 'D2_ZERO_OPEN'):
            d.eval_request(self.doc, 3, self.root)

    def test_no_physical_root_is_not_verified_input(self):
        with self.assertRaisesRegex(b.Invalid, 'INPUT_ROOT_REQUIRED'):
            d.eval_request(self.doc, 3)
        self.assertEqual(h.check_plan(self.doc)['physical_evidence'], 'NOT_RUN')

    def test_file_tampering_invalidates_cache_before_final_build(self):
        self.cache()
        path = self.root / self.spec['media'][0]['path']
        path.write_bytes(path.read_bytes() + b'changed')
        result = h.check_plan(self.doc, assets_root=self.root)
        self.assertIn('ui', result['run'])
        self.assertIn('references', result['run'])
        self.assertIn('core', result['reuse'])
        self.assertEqual(preflight.inspect(self.doc, self.root)['status'], 'BLOCKED')

    def test_ui_copy_change_reuses_unaffected_functional_and_object_checks(self):
        self.cache()
        self.spec['ui_elements'][0]['label'] = 'Quantity (KG)'
        self.spec['ui_callouts'][0]['label'] = 'Quantity (KG)'
        result = h.check_plan(self.doc, assets_root=self.root)
        for name in ('core', 'functional', 'objects', 'architecture'):
            self.assertIn(name, result['reuse'])
        self.assertIn('ui', result['run'])
        self.assertIn('record:ui_elements:EL-01', result['run'])
        self.assertIn('record:requirements:REQ-02', result['reuse'])

    def test_checker_byte_change_invalidates_old_pass(self):
        self.cache()
        candidate = self.root / 'checker-copy'
        shutil.copytree(ROOT, candidate)
        path = candidate / 'scripts/review_contract.py'
        path.write_bytes(path.read_bytes() + b'\n# checker revision\n')
        with patch.object(b, 'ROOT', candidate):
            result = h.check_plan(self.doc, assets_root=self.root)
        self.assertEqual(result['reuse'], [])

    def test_schema_problem_returns_blocked_with_pointer(self):
        self.spec['developer_decisions'] = [{'id': 'TECH-01'}]
        report = d.evaluate(self.doc)
        self.assertEqual(report['decision'], 'BLOCKED')
        self.assertTrue(any(row['pointer'].startswith('/developer_decisions/0') for row in report['issues']))
        self.assertTrue(all(row['status'] == 'NOT_RUN' for row in report['layers'][1:]))

    def test_superficial_question_and_empty_plan_cannot_pass(self):
        for rnd in self.control['eval_rounds']:
            for reader in rnd['readers']:
                reader['questions'] = [{'question': 'What schema?', 'pointer': '/schemaVersion', 'answer': '3.0'}]
                reader['plan_decisions'] = []
                reader['response_sha256'] = review.response_sha(reader)
        report = d.evaluate(self.doc)
        codes = {row['code'] for row in report['issues']}
        self.assertEqual(report['decision'], 'BLOCKED')
        self.assertIn('F2_FUNCTIONAL_COVERAGE', codes)
        self.assertIn('F5_PLAN_EVIDENCE', codes)

    def test_changed_response_and_wrong_reader_identity_rejected(self):
        reader = self.control['eval_rounds'][1]['readers'][0]
        reader['questions'][0]['question'] += ' changed'
        self.assertIn('F2_RESPONSE_HASH', {row['code'] for row in d.evaluate(self.doc)['issues']})
        reader['response_sha256'] = review.response_sha(reader)
        reader['reader_id'] = 'different-reader'
        self.assertIn('F2_REQUEST_BINDING', {row['code'] for row in d.evaluate(self.doc)['issues']})

    def test_legacy_review_protocol_needs_new_execution(self):
        for packet in self.control['eval_requests']:
            packet.pop('protocol')
        self.assertIn('F2_PROTOCOL', {row['code'] for row in d.evaluate(self.doc)['issues']})

    def test_string_false_is_not_visual_agreement(self):
        reader = self.control['eval_rounds'][1]['readers'][0]
        reader['visual_matches'][0]['label_match'] = 'false'
        reader['response_sha256'] = review.response_sha(reader)
        report = d.evaluate(self.doc)
        self.assertEqual(report['decision'], 'BLOCKED')
        self.assertIn('F2_RESPONSE_SHAPE', {row['code'] for row in report['issues']})

    def test_invalid_question_value_is_a_structured_failure(self):
        self.control['eval_rounds'][1]['readers'][0]['questions'][0]['question'] = 12
        report = d.evaluate(self.doc)
        self.assertEqual(report['decision'], 'BLOCKED')
        self.assertIn('F2_RESPONSE_SHAPE', {row['code'] for row in report['issues']})

    def test_batch_codec_preserves_values_and_rejects_invalid_input(self):
        values = {'first': {'id': '0001', 'quantity': '1.250', 'text': 'Çelik'},
                  'last': [True, False, None, []]}
        encoded = b.encode_many(values)
        self.assertEqual(b.decode_many(encoded), values)
        self.assertEqual(encoded['first'], b.encode(values['first']))
        with self.assertRaises(b.Invalid):
            b.decode_many({'valid': encoded['first'], 'invalid': 'rows[2]{x}:\n  1\n'})
        with self.assertRaises(b.Invalid):
            b.encode_many({'number': 9007199254740992})

    def test_question_prerequisites_order_and_cycle(self):
        first = {'id': 'OPEN-01', 'status': 'OPEN', 'owner': 'CONSULTANT', 'domain': 'BUSINESS',
                 'question': 'What is the scope?', 'options': [], 'options_reason': 'Need facts'}
        second = {**first, 'id': 'OPEN-02', 'question': 'Who owns approval?', 'depends_on': ['OPEN-01']}
        self.control['intake'] = [second, first]
        rows = h.consultant_questions(self.doc)
        self.assertEqual([row['id'] for row in rows], ['OPEN-01', 'OPEN-02'])
        self.assertEqual(rows[0]['unlocks'], ['OPEN-02'])
        first['depends_on'] = ['OPEN-02']
        with self.assertRaisesRegex(b.Invalid, 'Cyclic'):
            h.consultant_questions(self.doc)

    def test_status_has_an_executable_next_step(self):
        self.control['eval_rounds'] = []
        report = preflight.status(self.doc, self.root)
        self.assertEqual(report['preflight'], 'PASS')
        self.assertIn('eval-request', report['next_action'])


if __name__ == '__main__':
    unittest.main()
