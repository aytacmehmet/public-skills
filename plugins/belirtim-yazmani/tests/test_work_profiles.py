# SPDX-License-Identifier: GPL-3.0-only
"""Synthetic admission/quota tests; no provider execution or cost measurement."""
import copy
import itertools
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bv2 as b
import work_profiles as w


CHECKER = 'c' * 64
INPUT = 'a' * 64
RESPONSE = 'b' * 64


def assessment(values=(0, 0, 0, 0, 0, 0), **extra):
    return {**dict(zip(w.FACTORS, values)), **extra}


class WorkProfileTests(unittest.TestCase):
    def setUp(self):
        self.checker = patch.object(w, '_checker_sha', return_value=CHECKER)
        self.checker.start()
        self.addCleanup(self.checker.stop)
        self.doc = {'delivery': {'spec': {'requirements': [], 'media': [], 'ui_callouts': []},
                                 'control': {'other_control': {'keep': True}}},
                    'content': {'profil': 'standart'}}

    def select(self, profile='pro', **kwargs):
        return w.choose(self.doc, profile, assessment=kwargs.pop('assessment', assessment()),
                        capabilities=kwargs.pop('capabilities',
                          {'host': 'manual', 'reader_isolation': True, 'vision': True, 'child_limit': 3}),
                        capacity=kwargs.pop('capacity', {'status': 'PASS', 'input_sha256': INPUT}),
                        receipt=kwargs.pop('receipt', {'confirmed': True,
                                                     'receipt': 'SYNTHETIC_SELECTION_NOT_REAL_HOST_PROOF'}),
                        **kwargs)

    def complete(self, attempt, outcome='PASS'):
        return w.finish(self.doc, attempt['task_id'], outcome,
                        attempt['input_sha256'], attempt['context_id'],
                        {'response_sha256': RESPONSE,
                         'receipt': 'SYNTHETIC_RESPONSE_NOT_REAL_PROVIDER_EXECUTION'},
                        attempt_id=attempt['attempt_id'])

    def error(self, code, callback):
        with self.assertRaises(b.Invalid) as caught:
            callback()
        self.assertEqual(json.loads(str(caught.exception))['code'], 'WORK_PROFILE_' + code)

    def test_approved_scenarios_and_unknown_floor(self):
        examples = [((1, 0, 0, 0, 1, 0), 'lite'), ((2, 1, 1, 1, 1, 0), 'plus'),
                    ((2, 2, 2, 1, 2, 1), 'pro'), ((3, 3, 3, 2, 3, 1), 'max'),
                    ((4, 4, 4, 3, 4, 2), 'ultra'), ((0, 1, 0, 0, 4, 0), 'max'),
                    ((4, 0, 0, 0, 0, 0), 'pro')]
        for vector, expected in examples:
            with self.subTest(vector=vector):
                result = w.recommend(assessment(vector))
                self.assertEqual(result['recommended'], expected)
                self.assertEqual(result['status'], 'PASS')
        result = w.recommend(assessment((0, 0, 4, 0, None, 0)))
        self.assertIsNone(result['recommended'])
        self.assertEqual(result['possible_profiles'], ['lite', 'plus', 'ultra'])
        self.assertEqual((result['score_min'], result['score_max']), (8, 20))
        blocked = w.recommend(assessment((1, 2, 2, 4, 2, 3),
                             preparation_blockers=['Essential source is missing']))
        self.assertEqual(blocked['recommended'], 'max')
        self.assertEqual(blocked['status'], 'BLOCKED_PREPARATION')

    def test_all_complete_score_vectors_are_monotone(self):
        tested = 0
        for vector in itertools.product(range(5), repeat=6):
            _, rank = w._rank(vector)
            tested += 1
            for index, value in enumerate(vector):
                if value < 4:
                    changed = list(vector)
                    changed[index] += 1
                    self.assertGreaterEqual(w._rank(changed)[1], rank)
        self.assertEqual(tested, 15625)

    def test_volume_boundaries_and_counts_never_lower_size(self):
        for value, size in [(10, 0), (11, 1), (25, 1), (26, 2), (60, 2),
                            (61, 3), (120, 3), (121, 4)]:
            result = w.recommend(assessment(counts={'requirements': value}))
            self.assertEqual(result['assessment']['factors']['size']['score'], size)
        self.assertEqual(w.recommend(assessment(counts={'assets': 21}))['recommended'], 'pro')
        self.assertEqual(w.recommend(assessment((4, 0, 0, 0, 0, 0),
                         counts={'requirements': 0}))['assessment']['factors']['size']['score'], 4)
        unknown = w.recommend(assessment((None, 0, 0, 0, 0, 0), counts={'objects': 41}))
        self.assertEqual(unknown['possible_profiles'], ['pro'])
        self.assertIsNone(unknown['recommended'])

    def test_invalid_assessment_counts_and_source_are_structured(self):
        for bad in (True, -1, 5, 1.5, '1'):
            self.error('ASSESSMENT', lambda bad=bad: w.recommend(assessment((bad, 0, 0, 0, 0, 0))))
        self.error('COUNTS', lambda: w.recommend(assessment(counts={'objects': True})))
        self.error('COUNTS', lambda: w.recommend(assessment(counts={'objects': -1})))
        row = assessment()
        row['impact'] = {'score': 2, 'source': ['']}
        self.error('ASSESSMENT', lambda: w.recommend(row))

    def test_catalog_has_shared_quality_and_does_not_apply_models(self):
        catalog = w.catalog()
        self.assertEqual([row['id'] for row in catalog['profiles']], list(w.PROFILE_NAMES))
        self.assertEqual([row['limits']['preparation_attempts'] for row in catalog['profiles']], [0, 1, 2, 4, 6])
        self.assertEqual([row['limits']['concurrent_children'] for row in catalog['profiles']], [1, 1, 2, 3, 3])
        for row in catalog['profiles']:
            self.assertEqual(row['quality']['full_readers_per_round'], 3)
            self.assertEqual(row['quality']['consecutive_clean_rounds'], 2)
            self.assertFalse(row['quality']['nested_children_allowed'])
            self.assertFalse(row['model_suggestions']['codex']['applied'])
        catalog['profiles'][0]['limits']['review_attempts'] = 0
        self.assertEqual(w.catalog()['profiles'][0]['limits']['review_attempts'], 12)

    def test_selected_model_suggestion_needs_explicit_observed_catalog_match(self):
        base = {'host': 'codex', 'reader_isolation': True, 'vision': True, 'child_limit': 3}
        result = self.select('pro', capabilities=base)
        self.assertEqual(result['model_suggestion']['model'], 'gpt-6.1-sol')
        self.assertEqual(result['model_suggestion']['reasoning'], 'high')
        self.assertEqual(result['model_suggestion']['availability'], 'UNKNOWN')
        self.assertTrue(result['model_suggestion']['recommendation_only'])
        self.assertFalse(result['model_suggestion']['applied'])
        unobserved = {**base, 'model_catalog': {'models': ['gpt-6.1-sol']}}
        self.assertEqual(self.select('pro', capabilities=unobserved)[
          'model_suggestion']['availability'], 'UNKNOWN')
        observed = {**base, 'model_catalog': {'observed': True, 'source': 'SYNTHETIC_CATALOG_ONLY',
                     'models': [{'id': 'gpt-6.1-sol', 'reasoning': ['medium', 'high']}]}}
        result = self.select('pro', capabilities=observed)
        self.assertEqual(result['model_suggestion']['availability'], 'OBSERVED_CATALOG_MATCH')
        self.assertEqual(result['model_suggestion']['reasoning_availability'], 'OBSERVED_CATALOG_MATCH')
        self.assertEqual(result['model_suggestion']['provider_execution'], 'NOT_RUN')
        self.assertIsNone(self.select('pro', capabilities={**base, 'host': 'manual'})['model_suggestion'])
        self.assertEqual(self.select('max', capabilities={**base, 'host': 'claude'})[
                         'model_suggestion']['model'], 'claude-opus-5-5')

    def test_legacy_compatibility_and_required_selection(self):
        self.assertEqual(w.assert_release(self.doc)['readiness'], 'LEGACY_EXEMPT')
        self.doc['delivery']['control']['work_profile_required'] = True
        self.error('SELECTION_REQUIRED', lambda: w.admit(self.doc, 'release'))
        before = copy.deepcopy(self.doc)
        self.error('CONFIRMATION', lambda: self.select(receipt={'confirmed': 'true', 'receipt': 'x'}))
        self.assertEqual(self.doc, before)

    def test_selection_changes_only_private_work_profile_and_respects_override(self):
        before = copy.deepcopy(self.doc)
        report = self.select('lite', assessment=assessment((0, 1, 0, 0, 4, 0)))
        self.assertEqual(report['selected'], 'lite')
        self.assertEqual(report['recommendation']['recommended'], 'max')
        after = copy.deepcopy(self.doc)
        after['delivery']['control'].pop('work_profile')
        self.assertEqual(after, before)
        self.assertEqual(self.doc['content']['profil'], 'standart')

    def test_capacity_pending_blocked_and_stale_bindings_do_not_pass(self):
        for state in ('PENDING', 'BLOCKED'):
            self.select(capacity={'status': state})
            self.error('ADMISSION', lambda: w.admit(self.doc, 'prepare'))
            w.admit(self.doc, 'write')
            self.error('ADMISSION', lambda: w.admit(self.doc, 'review'))
        before = copy.deepcopy(self.doc)
        self.error('CAPACITY_STALE', lambda: self.select(capacity={'status': 'PASS', 'spec_sha256': '0' * 64}))
        self.assertEqual(self.doc, before)
        self.error('CAPACITY_STALE', lambda: self.select(capacity={'status': 'PASS', 'checker_sha256': '0' * 64}))

    def test_discovery_closes_unknowns_without_waiving_review_requirements(self):
        self.select('plus', assessment=assessment((0, None, 0, 0, 0, 0),
                    preparation_blockers=['Missing source']),
                    capabilities={'child_limit': 1, 'reader_isolation': False, 'vision': False})
        self.error('ADMISSION', lambda: w.admit(self.doc, 'prepare'))
        w.admit(self.doc, 'write')
        self.assertEqual(w.status(self.doc)['usage']['preparation_attempts'], 0)
        # Uncertainty without an explicit stop condition can use bounded discovery.
        self.select('plus', assessment=assessment((0, None, 0, 0, 0, 0)),
                    capabilities={'child_limit': 1, 'reader_isolation': False, 'vision': False})
        w.admit(self.doc, 'prepare')
        attempt = w.begin(self.doc, 'source-research', 'prep', INPUT, 'source-context')
        self.complete(attempt)
        self.error('ADMISSION', lambda: w.admit(self.doc, 'review'))
        self.select('plus')
        w.admit(self.doc, 'review')
        self.assertEqual(w.status(self.doc)['usage']['preparation_attempts'], 1)

    def test_vision_only_required_when_actual_media_or_callouts_exist(self):
        self.select(capabilities={'child_limit': 3, 'reader_isolation': True, 'vision': False})
        w.admit(self.doc, 'review')
        self.doc['delivery']['spec']['media'] = [{'id': 'MEDIA-01'}]
        self.select(capabilities={'child_limit': 3, 'reader_isolation': True, 'vision': False})
        w.admit(self.doc, 'prepare')
        self.error('ADMISSION', lambda: w.admit(self.doc, 'review'))
        self.select(capabilities={'child_limit': 3, 'reader_isolation': True, 'vision': True})
        w.admit(self.doc, 'review')

    def test_concurrency_uses_the_lower_host_and_profile_limits(self):
        for profile in w.PROFILE_NAMES:
            self.doc['delivery']['control'].pop('work_profile', None)
            result = self.select(profile)
            limit = result['limits']['concurrent_children']
            tasks = [w.begin(self.doc, 'task-' + str(i), 'reviewer', INPUT, 'ctx-' + str(i))
                     for i in range(limit)]
            before = copy.deepcopy(self.doc)
            self.error('CONCURRENCY', lambda: w.begin(self.doc, 'overflow', 'reviewer', INPUT, 'ctx-overflow'))
            self.assertEqual(self.doc, before)
            for task in tasks:
                self.complete(task)
        self.doc['delivery']['control'].pop('work_profile')
        self.assertEqual(self.select('ultra', capabilities={
          'reader_isolation': True, 'vision': True, 'child_limit': 1})['limits']['concurrent_children'], 1)

    def test_preparation_and_review_attempt_budgets_are_independent(self):
        self.select('plus')
        prep = w.begin(self.doc, 'prep', 'prep', INPUT)
        self.complete(prep, 'FAIL')
        self.error('BUDGET', lambda: w.begin(self.doc, 'prep-retry', 'prep', INPUT))
        for index in range(12):
            review = w.begin(self.doc, 'reader-' + str(index), 'reviewer', INPUT, 'ctx-' + str(index))
            w.recover(self.doc, review['task_id'], attempt_id=review['attempt_id'])
        self.error('BUDGET', lambda: w.begin(self.doc, 'reader-13', 'reviewer', INPUT, 'ctx-13'))
        self.assertEqual(w.status(self.doc)['usage']['total_attempts'], 13)

    def test_lite_no_preparation_child_but_keeps_twelve_reader_attempts(self):
        self.select('lite')
        self.error('BUDGET', lambda: w.begin(self.doc, 'prep', 'prep', INPUT))
        for index in range(12):
            self.complete(w.begin(self.doc, 'reader-' + str(index), 'reviewer', INPUT, 'ctx-' + str(index)))
        self.error('BUDGET', lambda: w.begin(self.doc, 'last', 'reviewer', INPUT, 'ctx-last'))

    def test_cancel_recover_retry_and_idempotent_finish_never_refund(self):
        self.select('pro')
        first = w.begin(self.doc, 'same-logical-task', 'reviewer', INPUT, 'ctx-1')
        recovered = w.recover(self.doc, first['task_id'], attempt_id=first['attempt_id'])
        self.assertEqual(recovered['status'], 'UNKNOWN')
        self.error('INCOMPLETE', lambda: w.assert_release(self.doc))
        second = w.begin(self.doc, first['task_id'], 'reviewer', INPUT, 'ctx-2')
        self.error('ATTEMPT_REQUIRED', lambda: w.finish(self.doc, first['task_id'], 'PASS', INPUT, 'ctx-2',
                          {'response_sha256': RESPONSE, 'receipt': 'synthetic'}))
        finished = self.complete(second)
        self.assertEqual(self.complete(second), finished)
        self.assertEqual(w.status(self.doc)['usage']['review_attempts'], 2)
        w.assert_release(self.doc)
        third = w.begin(self.doc, 'cancel-me', 'reviewer', INPUT, 'ctx-3')
        w.cancel(self.doc, third['task_id'], attempt_id=third['attempt_id'])
        self.assertEqual(w.status(self.doc)['usage']['review_attempts'], 3)
        self.error('INCOMPLETE', lambda: w.assert_release(self.doc))
        self.error('TERMINAL', lambda: self.complete(first))

    def test_reader_context_never_reused_after_failure_or_revision(self):
        self.select('pro')
        task = w.begin(self.doc, 'read', 'reviewer', INPUT, 'fresh-context')
        self.complete(task, 'FAIL')
        self.error('ISOLATION', lambda: w.begin(self.doc, 'other', 'reviewer', INPUT, 'fresh-context'))
        self.doc['delivery']['spec']['requirements'].append({'id': 'REQ-1'})
        self.select('pro')
        self.error('ISOLATION', lambda: w.begin(self.doc, 'other', 'reviewer', INPUT, 'fresh-context'))
        self.assertEqual(w.status(self.doc)['usage']['review_attempts'], 1)

    def test_two_failed_task_attempts_need_diagnosis_without_refunding_budget(self):
        self.select('pro')
        first = w.begin(self.doc, 'same-task', 'reviewer', INPUT, 'ctx-1')
        self.complete(first, 'FAIL')
        second = w.begin(self.doc, 'same-task', 'reviewer', INPUT, 'ctx-2')
        w.recover(self.doc, second['task_id'], attempt_id=second['attempt_id'])
        before = copy.deepcopy(self.doc)
        self.error('DIAGNOSIS_REQUIRED', lambda: w.begin(self.doc, 'same-task', 'reviewer', INPUT, 'ctx-3'))
        self.assertEqual(self.doc, before)
        self.error('TEXT', lambda: w.begin(self.doc, 'same-task', 'reviewer', INPUT, 'ctx-3', diagnosis=''))
        third = w.begin(self.doc, 'same-task', 'reviewer', INPUT, 'ctx-3',
                        diagnosis='SYNTHETIC: unavailable evidence was replaced by a verified reference.')
        self.assertIn('verified reference', third['diagnosis'])
        self.complete(third)
        self.assertEqual(w.status(self.doc)['usage']['review_attempts'], 3)
        w.assert_release(self.doc)

    def test_completion_requires_exact_bound_input_context_and_receipt(self):
        self.select('pro')
        task = w.begin(self.doc, 'read', 'reviewer', INPUT, 'ctx')
        before = copy.deepcopy(self.doc)
        self.error('INPUT_BINDING', lambda: w.finish(self.doc, 'read', 'PASS', 'd' * 64, 'ctx'))
        self.error('CONTEXT_BINDING', lambda: w.finish(self.doc, 'read', 'PASS', INPUT, 'other'))
        self.error('HASH', lambda: w.finish(self.doc, 'read', 'PASS', INPUT, 'ctx'))
        self.error('TEXT', lambda: w.finish(self.doc, 'read', 'PASS', INPUT, 'ctx', {'response_sha256': RESPONSE}))
        self.error('EVIDENCE_BINDING', lambda: w.finish(self.doc, 'read', 'PASS', INPUT, 'ctx',
                    {'response_sha256': RESPONSE, 'receipt': 'synthetic', 'input_sha256': 'd' * 64}))
        self.assertEqual(self.doc, before)
        self.complete(task)

    def test_revision_checker_and_model_plan_updates_preserve_spend(self):
        self.select('pro')
        episode = w.status(self.doc)['episode_id']
        self.complete(w.begin(self.doc, 'old-snapshot', 'reviewer', INPUT, 'old-ctx'))
        self.doc['delivery']['spec']['requirements'].append({'id': 'REQ-1'})
        self.assertIn('SPEC_NEEDS_REFRESH', w.status(self.doc)['issues'])
        self.error('ADMISSION', lambda: w.admit(self.doc, 'review'))
        w.admit(self.doc, 'write')
        self.select('max', capabilities={'reader_isolation': True, 'vision': True, 'child_limit': 3,
                    'model_catalog': {'requested': 'example-model', 'effective': 'UNKNOWN'}})
        self.assertEqual(w.status(self.doc)['episode_id'], episode)
        self.assertEqual(w.status(self.doc)['usage']['review_attempts'], 1)
        self.complete(w.begin(self.doc, 'current-snapshot', 'reviewer', INPUT, 'new-ctx'))
        w.assert_release(self.doc)
        with patch.object(w, '_checker_sha', return_value='d' * 64):
            self.error('ADMISSION', lambda: w.admit(self.doc, 'release'))

    def test_state_tamper_or_malformed_state_fails_closed(self):
        self.select('pro')
        self.doc['delivery']['control']['work_profile']['selected'] = 'ultra'
        self.error('INTEGRITY', lambda: w.status(self.doc))
        state = self.doc['delivery']['control']['work_profile']
        state['capacity'].pop('status')
        w._seal(state)
        self.error('STATE', lambda: w.status(self.doc))

    def test_refresh_running_downgrade_and_writer_guard_are_atomic(self):
        self.select('pro')
        task = w.begin(self.doc, 'read', 'reviewer', INPUT, 'ctx')
        before = copy.deepcopy(self.doc)
        self.error('RUNNING', lambda: self.select('max'))
        self.error('READER_RUNNING', lambda: w.admit(self.doc, 'write'))
        self.assertEqual(self.doc, before)
        self.complete(task)
        prep = w.begin(self.doc, 'prep', 'prep', INPUT)
        self.complete(prep)
        before = copy.deepcopy(self.doc)
        self.error('BUDGET', lambda: self.select('lite'))
        self.assertEqual(self.doc, before)
        self.error('ROLE', lambda: w.begin(self.doc, 'nested-writer', 'writer', INPUT))


if __name__ == '__main__':
    unittest.main()
