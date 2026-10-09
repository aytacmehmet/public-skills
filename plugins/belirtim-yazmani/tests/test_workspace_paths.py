# SPDX-License-Identifier: GPL-3.0-only
"""Opaque native sandbox ancestors must not become unverified path admission."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import bv2 as b
import workspace_lock as locks


class WorkspacePathTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.source=self.root/'source.toon'
        self.source.write_text('synthetic',encoding='utf-8')
        self.original=Path.is_symlink

    def opaque(self,path):
        if path==self.root.parent:raise PermissionError('Opaque ancestor')
        return self.original(path)

    def test_accessible_physical_target_and_new_file_can_lock_with_opaque_ancestor(self):
        with patch.object(Path,'is_symlink',autospec=True,side_effect=self.opaque):
            self.assertEqual(locks.checked_path(self.source),self.source)
            self.assertEqual(locks.checked_path(self.root/'new.json'),self.root/'new.json')
            with locks.held(self.source):self.assertTrue(self.source.with_name('source.toon.byw.lock').exists())
        self.assertFalse(self.source.with_name('source.toon.byw.lock').exists())

    def test_unknown_or_different_physical_target_never_admits(self):
        with patch.object(Path,'is_symlink',autospec=True,side_effect=self.opaque):
            with patch.object(Path,'resolve',return_value=self.root/'different'):
                with self.assertRaisesRegex(b.Invalid,'links or junctions'):locks.checked_path(self.source)
            with patch.object(Path,'resolve',side_effect=PermissionError('No target proof')):
                with self.assertRaisesRegex(b.Invalid,'cannot be verified'):locks.checked_path(self.source)

    def test_observed_link_is_rejected_without_fallback(self):
        with patch.object(Path,'is_symlink',return_value=True):
            with self.assertRaisesRegex(b.Invalid,'links or junctions'):locks.checked_path(self.source)
