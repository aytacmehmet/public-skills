# SPDX-License-Identifier: GPL-3.0-only
"""Selected coordinated-profile limits and preparation admission boundaries."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bv2 as b
import work_profiles as w
import profile_runtime as runtime
import dispatch_registry as registry
from fixture_v4 import valid


class CoordinationLimitTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.coordinator=self.root/'shared.json'

    def selected(self,index,profile='lite',blockers=None):
        root=self.root/str(index)
        doc=valid(root)
        assessment={key:0 for key in w.FACTORS}
        if blockers:assessment['preparation_blockers']=blockers
        caps={'host':'manual','reader_isolation':True,'vision':True,'child_limit':3,
              'coordinator_file':str(self.coordinator)}
        capacity={'status':'PASS','context_limit':1000000,'packet_tokens':200000,'output_reserve':50000,
                  'image_tokens':4096,'evidence':'SYNTHETIC_CONSERVATIVE_ESTIMATE'}
        assessment,caps,capacity=runtime.bind_inputs(doc,assessment,caps,capacity,root)
        w.choose(doc,profile,assessment,caps,capacity,{'confirmed':True,'receipt':'SYNTHETIC_SELECTION'})
        return doc,root/'workspace.toon'

    def test_business_blocker_allows_writer_but_never_reserves_preparation(self):
        doc,source=self.selected(0,'plus',['Contradictory business source'])
        before=copy.deepcopy(doc)
        w.admit(doc,'write')
        for operation in ('prepare','review','release'):
            with self.assertRaisesRegex(b.Invalid,'BLOCKED_PREPARATION'):w.admit(doc,operation)
        with self.assertRaisesRegex(b.Invalid,'BLOCKED_PREPARATION'):
            w.begin(doc,'prep','prep','a'*64,'context')
        self.assertEqual(doc,before)
        self.assertFalse(self.coordinator.exists())

    def test_three_lite_workspaces_share_one_slot_and_preserve_spent_attempts(self):
        pairs=[self.selected(index) for index in range(3)]
        for doc,source in pairs:registry.register_selection(doc,source)
        first,source=pairs[0]
        attempt=w.begin(first,'review:1:reader-1','reviewer','a'*64,'context-0')
        registry.reserve(first,source,attempt)
        before=self.coordinator.read_bytes()
        second,second_source=pairs[1]
        pending=w.begin(second,'review:1:reader-1','reviewer','b'*64,'context-1')
        with self.assertRaisesRegex(b.Invalid,'no free child'):registry.reserve(second,second_source,pending)
        self.assertEqual(self.coordinator.read_bytes(),before)
        terminal=w.finish(first,attempt['task_id'],'FAIL',attempt['input_sha256'],attempt['context_id'],
                          {'receipt':'SYNTHETIC_FAIL'},attempt_id=attempt['attempt_id'])
        registry.finish(first,source,terminal)
        registry.reserve(second,second_source,pending)
        self.assertEqual(w.status(first)['usage']['total_attempts'],1)
        self.assertEqual(sum(row['status']=='RUNNING' for row in json.loads(self.coordinator.read_text())['rows']),1)

    def test_mixed_profiles_are_bound_at_selection_and_finished_scope_releases_limit(self):
        lite,lite_source=self.selected(0,'lite')
        ultra,ultra_source=self.selected(1,'ultra')
        registry.register_selection(lite,lite_source)
        registry.register_selection(ultra,ultra_source)
        first=w.begin(ultra,'prep:1','prep','a'*64,'context-1')
        registry.reserve(ultra,ultra_source,first)
        second=w.begin(ultra,'prep:2','prep','b'*64,'context-2')
        with self.assertRaisesRegex(b.Invalid,'no free child'):registry.reserve(ultra,ultra_source,second)
        registry.finish_selection(lite,lite_source)
        registry.reserve(ultra,ultra_source,second)
        with self.assertRaisesRegex(b.Invalid,'running children'):registry.finish_selection(ultra,ultra_source)

    def test_legacy_unknown_running_profile_is_not_silently_assumed_three(self):
        doc,source=self.selected(0,'ultra')
        self.coordinator.write_text(json.dumps({'kind':registry.KIND,'rows':[{
            'key':'old','workspace':'legacy','episode_id':'old','attempt_id':'old','task_id':'old','status':'RUNNING'}]}),encoding='utf-8')
        before=self.coordinator.read_bytes()
        attempt=w.begin(doc,'prep:new','prep','a'*64,'new-context')
        with self.assertRaisesRegex(b.Invalid,'Legacy running reservation'):registry.reserve(doc,source,attempt)
        self.assertEqual(self.coordinator.read_bytes(),before)
