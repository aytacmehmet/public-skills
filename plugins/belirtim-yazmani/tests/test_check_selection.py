# SPDX-License-Identifier: GPL-3.0-only
"""Impact selection must cover changed safety paths and default to full on unknowns."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import check


class CheckSelectionTests(unittest.TestCase):
    def test_shared_registry_change_covers_cross_workspace_and_native_admission(self):
        modules=check.selected(['scripts/dispatch_registry.py'])
        self.assertTrue({'test_coordination_limits','test_profile_hooks','test_profile_integration'}<=set(modules))
        self.assertNotIn('test_release',modules)

    def test_oracle_change_covers_packet_readers_and_release(self):
        self.assertTrue({'test_review_safety','test_source_pool','test_release','test_profile_integration'}<=set(check.selected(['scripts/review_contract.py'])))

    def test_unknown_schema_final_and_empty_scope_keep_complete_suite(self):
        full=check.selected([],True)
        self.assertEqual(check.selected(['schema/handoff.schema.json']),full)
        self.assertEqual(check.selected(['scripts/new_gate.py']),full)
        self.assertEqual(check.selected([]),full)
        self.assertEqual(check.selected(['scripts/dispatch_registry.py'],True),full)
        with self.assertRaises(ValueError):check.selected(['../other.py'])
        self.assertTrue(check.needs_package(['scripts/dispatch_registry.py'],True))
        self.assertTrue(check.needs_package(['skills/belirtim-yazmani/SKILL.md']))
        self.assertFalse(check.needs_package(['tests/test_work_profiles.py']))
