# SPDX-License-Identifier: GPL-3.0-only
"""Pooled source regression; synthetic readers, never a real review round."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bv2 as b
import delivery as d
import preflight
import source_pool as pool
from fixture_v4 import valid, seal


def references(data, count=86, path='fixture-talep-source.toon'):
    return [{'id': 'REF-DATA-' + str(i), 'kind': 'LIST', 'path': path,
             'sha256': b.digest(data), 'pointer': '/tables/' + str(i) + '/values',
             'purpose': 'Complete approved source table'} for i in range(count)]


class SourcePoolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.doc = valid(self.root)
        self.spec, self.control = d.get_state(self.doc)
        self.content = {'source_marker': 'COMPLETE_SOURCE_CONTENT_SINGLE_OCCURRENCE',
                        'tables': [{'values': [i, 'value-' + str(i)]} for i in range(86)]}
        self.data = b.encode(self.content).encode()
        self.refs = references(self.data)
        self.path = self.refs[0]['path']

    def prepared(self):
        refs, sources = pool.collect(self.refs, {self.path: self.data})
        return {'assets': [], 'references': refs, 'source_pool': sources,
                'input_sha256': 'a' * 64}

    def test_86_bindings_three_packets_decode_once_and_correct_values(self):
        with patch.object(b, 'decode_many', wraps=b.decode_many) as decode:
            prepared = self.prepared()
            self.assertEqual(decode.call_count, 1)
            self.assertEqual(len(decode.call_args.args[0]), 1)
        packets = d._issue_review_packets(self.doc, 3, prepared)
        for packet in packets:
            self.assertEqual(len(packet['source_pool']['sources']), 1)
            self.assertFalse(any('content' in row for row in packet['references']))
            reader = pool.Reader(packet)
            self.assertFalse(reader.legacy_read_only)
            for i, row in enumerate(self.refs):
                self.assertEqual(reader.resolve(row['id']), [i, 'value-' + str(i)])
            self.assertEqual(json.dumps(packet).count(self.content['source_marker']), 1)
        self.assertEqual(sum(json.dumps(p).count(self.content['source_marker']) for p in packets), 3)
        packets[0]['source_pool']['sources'][0]['content']['tables'][0]['values'][0] = -1
        self.assertEqual(packets[1]['source_pool']['sources'][0]['content']['tables'][0]['values'][0], 0)

    def test_multiple_files_aliases_full_document_and_text(self):
        other = b.encode({'other': ['second document']}).encode()
        rows = [self.refs[0], {**self.refs[1], 'path': 'fixture-talep-alias.toon'},
                {**self.refs[2], 'path': 'fixture-talep-other.toon', 'sha256': b.digest(other), 'pointer': None},
                {**self.refs[3], 'path': 'fixture-talep-note.txt', 'sha256': b.digest(b'whole text'), 'pointer': None}]
        files = {self.path: self.data, 'fixture-talep-alias.toon': self.data,
                 'fixture-talep-other.toon': other, 'fixture-talep-note.txt': b'whole text'}
        with patch.object(b, 'decode_many', wraps=b.decode_many) as decode:
            refs, sources = pool.collect(rows, files)
            self.assertEqual(len(decode.call_args.args[0]), 2)
        self.assertEqual(len(sources['sources']), 3)
        packet = d._issue_review_packets(self.doc, 3, {'assets': [], 'references': refs,
            'source_pool': sources, 'input_sha256': 'a' * 64})[0]
        reader = pool.Reader(packet)
        self.assertEqual(reader.resolve(rows[2]['id']), {'other': ['second document']})
        self.assertEqual(reader.resolve(rows[3]['id']), 'whole text')

    def test_missing_hash_pointer_and_conflicting_source_are_blocked(self):
        for rows, files in [(self.refs[:1], {}), ([{**self.refs[0], 'sha256': '0' * 64}], {self.path: self.data}),
                            ([{**self.refs[0], 'pointer': '/absent'}], {self.path: self.data}),
                            ([self.refs[0], self.refs[0]], {self.path: self.data})]:
            with self.subTest(rows=rows), self.assertRaises(b.Invalid):
                pool.collect(rows, files)
        packet = d._issue_review_packets(self.doc, 3, self.prepared())[0]
        corrupted = copy.deepcopy(packet)
        corrupted['source_pool']['sources'][0]['content']['source_marker'] = 'tampered'
        with self.assertRaisesRegex(b.Invalid, 'content hash'):
            pool.Reader(corrupted)

    def test_volume_limits_block_before_issue_or_save_without_truncation(self):
        before = copy.deepcopy(self.control['eval_requests'])
        self.control['review_packet_limits'] = {'max_packet_bytes': 100}
        with self.assertRaisesRegex(b.Invalid, 'BLOCKED.*VOLUME'):
            d._issue_review_packets(self.doc, 3, self.prepared())
        self.assertEqual(self.control['eval_requests'], before)
        self.control.pop('review_packet_limits')
        packets = d._issue_review_packets(self.doc, 3, self.prepared())
        target = self.root / 'no-partial-output'
        with self.assertRaisesRegex(b.Invalid, 'BLOCKED.*VOLUME'):
            pool.save_packets(packets, target, {'review_packet_limits': {'max_total_bytes': 100}})
        self.assertFalse(target.exists())

    def test_preflight_decode_cached_and_small_generate_save_consume_flow(self):
        self.spec['references'] = self.refs
        (self.root / self.path).write_bytes(self.data)
        self.control['assets'].append({'path': self.path, 'sha256': b.digest(self.data)})
        seal(self.doc)
        with patch.object(pool, 'decode_documents', wraps=pool.decode_documents) as decode:
            result = preflight.inspect(self.doc, self.root)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(decode.call_count, 1)
        packets = d.eval_request(self.doc, 3, self.root)
        target = self.root / 'saved'
        pool.save_packets(packets, target, self.control)
        for packet in packets:
            loaded = b.load(target / ('3-' + packet['reader_id'] + '.toon'))
            reader = pool.Reader(loaded)
            self.assertEqual(reader.resolve('REF-DATA-85'), [85, 'value-85'])
            self.assertTrue('expected' not in loaded['spec']['test_cases'][0] if packet['scenario_reader']
                            else 'expected' in loaded['spec']['test_cases'][0])
        self.assertEqual(len(list(target.iterdir())), 3)

    def test_legacy_read_only_and_old_review_credit_rejected(self):
        legacy = {'protocol': '3.1', 'references': [{**self.refs[0], 'content': self.content}]}
        legacy['request_sha256'] = pool.value_sha(legacy)
        reader = pool.Reader(legacy, allow_legacy=True)
        self.assertTrue(reader.legacy_read_only)
        self.assertEqual(reader.resolve('REF-DATA-0'), [0, 'value-0'])
        with self.assertRaisesRegex(b.Invalid, 'stale'):
            pool.Reader(legacy)
        for request in self.control['eval_requests']:
            request['protocol'] = '3.1'
            request.pop('source_pool_sha256')
        self.control.pop('review_confirmation_protocol')
        report = d.evaluate(self.doc)
        codes = {row['code'] for row in report['issues']}
        self.assertIn('F2_PROTOCOL', codes)
        self.assertIn('F2_EXECUTION_CONFIRMATION', codes)

    @unittest.skipUnless(os.environ.get('BYW_REFERENCE_SOURCE') and os.environ.get('BYW_REFERENCE_WORKSPACE'),
                         'Real source fixture requires explicit read-only external inputs')
    def test_real_86_pointer_source_three_saved_packets(self):
        source = Path(os.environ['BYW_REFERENCE_SOURCE'])
        workspace = Path(os.environ['BYW_REFERENCE_WORKSPACE'])
        original = source.read_bytes()
        original_sha = b.digest(original)
        contract = b.load(workspace)
        actual = [row for row in contract['delivery']['spec']['references']
                  if row['path'].endswith('rmp-legacy-source-contract.toon')]
        self.assertEqual(len(actual), 86)
        self.assertTrue(all(row['sha256'] == original_sha for row in actual))
        path = actual[0]['path']
        oracle = json.loads(b.codec('decode', original.decode('utf-8')))
        with patch.object(b, 'decode_many', wraps=b.decode_many) as decode:
            refs, sources = pool.collect(actual, {path: original})
            self.assertEqual(decode.call_count, 1)
            self.assertEqual(len(decode.call_args.args[0]), 1)
        prepared = {'assets': [], 'references': refs, 'source_pool': sources, 'input_sha256': 'a' * 64}
        packets = d._issue_review_packets(self.doc, 3, prepared)
        target = self.root / 'real-source-three-packets'
        pool.save_packets(packets, target)
        for packet in packets:
            loaded = b.load(target / ('3-' + packet['reader_id'] + '.toon'))
            self.assertEqual(len(loaded['source_pool']['sources']), 1)
            reader = pool.Reader(loaded)
            for ref in actual:
                expected = oracle if ref['pointer'] is None else d.resolve(oracle, ref['pointer'])
                self.assertEqual(reader.resolve(ref['id']), expected)
        self.assertEqual(source.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
