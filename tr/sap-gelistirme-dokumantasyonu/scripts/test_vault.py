#!/usr/bin/env python3
"""Behavior tests in disposable projects; no SAP connection or user Vault access."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

import vault


class VaultBehavior(unittest.TestCase):
    def setUp(self):
        scratch = Path.cwd() / "work"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="vault-test-", dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project"
        self.project.mkdir()
        self.root = self.project / "obsidian"

    def cli(self, *args, code=0):
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(Path(vault.__file__)), "--project", str(self.project), *args], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def init(self):
        return self.cli("init", "--key", "TEST-ERP")

    def add(self, key="DEV-001", kind="development", slug="sample"):
        return self.cli("add", "--id", key, "--kind", kind, "--slug", slug, "--title", key + " sample")

    def snapshot(self):
        return {p.relative_to(self.project).as_posix(): p.read_bytes() for p in self.project.rglob("*") if p.is_file()}

    def checkpoint(self, event="EVT-001", summary="Reviewed contract", status="active", code=0):
        return self.cli("checkpoint", "--id", "DEV-001", "--event-id", event, "--summary", summary, "--next", "Review the proposed design", "--status", status, code=code)

    def test_dry_run_writes_nothing(self):
        plan = self.cli("--dry-run", "init", "--key", "TEST-ERP", "--install-guidance")
        self.assertTrue(plan["changed"])
        self.assertEqual(self.snapshot(), {})

    def test_repeat_initialization_preserves_all_bytes(self):
        self.init()
        before = self.snapshot()
        self.assertEqual(self.init()["changed"], [])
        self.assertEqual(before, self.snapshot())

    def test_guidance_merge_preserves_effective_override_and_backup(self):
        original = b"# Team agreement\r\nKeep source ownership.\r\n"
        (self.project / "AGENTS.override.md").write_bytes(original)
        (self.project / "AGENTS.md").write_text("Other rules", encoding="utf-8")
        self.cli("init", "--key", "TEST-ERP", "--install-guidance")
        self.assertEqual((self.project / "AGENTS.md").read_text(), "Other rules")
        self.assertIn("Keep source ownership.", (self.project / "AGENTS.override.md").read_text())
        backups = list((self.root / "assets/guidance-backups").glob("*.txt"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        before = self.snapshot()
        self.cli("init", "--key", "TEST-ERP", "--install-guidance")
        self.assertEqual(before, self.snapshot())

    def test_unmanaged_vault_remains_untouched(self):
        self.root.mkdir()
        (self.root / "Existing.md").write_text("Canonical user document", encoding="utf-8")
        before = self.snapshot()
        self.cli("init", "--key", "TEST-ERP", code=2)
        self.assertEqual(before, self.snapshot())

    def test_two_developments_share_one_provider_and_impact(self):
        self.init()
        self.add()
        self.add("DEV-002")
        self.add("SHR-001", "shared")
        self.cli("relate", "--from-id", "DEV-001", "--to-id", "SHR-001")
        self.cli("relate", "--from-id", "DEV-002", "--to-id", "DEV-001")
        affected = self.cli("impact", "--id", "SHR-001")["affected_consumers"]
        self.assertEqual(affected["DEV-001"]["depth"], 1)
        self.assertEqual(affected["DEV-002"]["depth"], 2)
        self.assertEqual(self.cli("check")["errors"], 0)
        provider = (self.root / "shared/SHR-001-sample/Overview.md").read_text(encoding="utf-8")
        self.assertIn("developments/DEV-001-sample/Overview", provider)
        before = self.snapshot()
        self.cli("relate", "--from-id", "DEV-001", "--to-id", "SHR-001")
        self.assertEqual(before, self.snapshot())

    def test_cycles_do_not_loop_in_impact(self):
        self.init()
        self.add()
        self.add("DEV-002")
        self.cli("relate", "--from-id", "DEV-001", "--to-id", "DEV-002")
        self.cli("relate", "--from-id", "DEV-002", "--to-id", "DEV-001")
        self.assertEqual(set(self.cli("impact", "--id", "DEV-001")["affected_consumers"]), {"DEV-002"})

    def test_existing_authored_content_survives_repeated_add(self):
        self.init()
        self.add()
        path = self.root / "developments/DEV-001-sample/Overview.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nUser's reviewed design.\n", encoding="utf-8")
        before = self.snapshot()
        self.add()
        self.assertEqual(before, self.snapshot())
        self.cli("add", "--id", "DEV-001", "--kind", "development", "--slug", "different", "--title", "Changed", code=2)
        self.assertEqual(before, self.snapshot())

    def test_checkpoint_preserves_history_and_replay_does_not_rewind(self):
        self.init()
        self.add()
        self.checkpoint()
        self.checkpoint("EVT-002", "Blocked on business decision", "blocked")
        before = self.snapshot()
        self.checkpoint()
        self.assertEqual(before, self.snapshot())
        self.checkpoint(summary="Different historical claim", code=2)
        self.assertEqual(before, self.snapshot())
        history = (self.root / "developments/DEV-001-sample/History.md").read_text(encoding="utf-8")
        self.assertEqual(history.count("## EVT-001"), 1)
        self.assertIn("Occurred at: unknown", history)
        self.assertIn("Blocked on business decision", self.cli("context", "--id", "DEV-001")["current_state"])
        self.assertTrue(self.cli("check")["ok"])

    def test_source_drift_is_reported_without_silent_rebaseline(self):
        self.init()
        self.add()
        source = self.project / "contract.json"
        source.write_text('{"version":1}', encoding="utf-8")
        self.cli("source", "--id", "DEV-001", "--source", "contract.json")
        before = self.snapshot()
        source.write_text('{"version":2}', encoding="utf-8")
        result = self.cli("context", "--id", "DEV-001")
        self.assertEqual(result["changed_sources"], ["contract.json"])
        snap = "obsidian/developments/DEV-001-sample/source-snapshots.json"
        self.assertEqual(before[snap], self.snapshot()[snap])
        self.assertEqual(self.cli("check")["warnings"], 1)

    def test_path_escape_cannot_create_or_read_a_foreign_file(self):
        self.init()
        self.add()
        before = self.snapshot()
        self.cli("add", "--id", "DEV-003", "--kind", "development", "--slug", "../../escape", "--title", "Escape", code=2)
        self.cli("source", "--id", "DEV-001", "--source", "../outside.txt", code=2)
        self.assertEqual(before, self.snapshot())
        for bad in ("../escape.md", "C:/escape.md", "assets/CON", "assets/name.", "assets\\escape.md"):
            with self.assertRaises(vault.VaultError):
                vault.safe(self.root, bad)

    def test_consumer_resume_reports_changed_shared_evidence(self):
        self.init()
        self.add()
        self.add("SHR-001", "shared")
        self.cli("relate", "--from-id", "DEV-001", "--to-id", "SHR-001")
        source = self.project / "shared-contract.json"
        source.write_text('{"version":1}', encoding="utf-8")
        self.cli("source", "--id", "SHR-001", "--source", "shared-contract.json")
        source.write_text('{"version":2}', encoding="utf-8")
        result = self.cli("context", "--id", "DEV-001")
        self.assertEqual(result["dependency_changed_sources"], {"SHR-001": ["shared-contract.json"]})

    def test_linked_vault_is_refused(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        try:
            self.root.symlink_to(outside, target_is_directory=True)
            self.addCleanup(self.root.unlink)
        except OSError as exc:
            if sys.platform != "win32":
                self.skipTest(f"Host does not permit directory symlinks: {exc}")
            import _winapi
            _winapi.CreateJunction(str(outside.resolve()), str(self.root.absolute()))
            self.addCleanup(self.root.rmdir)
        self.cli("init", "--key", "TEST-ERP", code=2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_missing_managed_marker_does_not_partially_write(self):
        self.init()
        self.add()
        path = self.root / "developments/DEV-001-sample/Overview.md"
        path.write_text(path.read_text(encoding="utf-8").replace("<!-- pages:end -->", "removed"), encoding="utf-8")
        before = self.snapshot()
        self.cli("page", "--id", "DEV-001", "--template", "design", code=2)
        self.assertEqual(before, self.snapshot())

    def test_concurrent_human_edit_is_not_overwritten(self):
        self.init()
        v = vault.Vault(self.project)
        v.write("Home.md", v.read("Home.md") + "\nAgent addition\n")
        (self.root / "Home.md").write_text("Human edit", encoding="utf-8")
        with self.assertRaises(vault.VaultError):
            v.apply()
        self.assertEqual((self.root / "Home.md").read_text(), "Human edit")
        self.assertFalse((self.root / ".documentation.lock").exists())

    def test_broken_links_anchors_and_misplaced_notes_are_detected(self):
        self.init()
        self.add()
        path = self.root / "developments/DEV-001-sample/Open-Items.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[[missing/file]]\n[[Home#Missing heading]]\n", encoding="utf-8")
        (self.root / "Stray.md").write_text(vault.pack({"id": "stray", "kind": "guide", "updated": "2026-09-08"}, "Stray narrative"), encoding="utf-8")
        (self.project / "random-report.md").write_text("misplaced", encoding="utf-8")
        codes = {i["code"] for i in self.cli("check", "--audit-project", code=1)["issues"]}
        self.assertTrue({"broken_link", "broken_anchor", "misplaced_note", "outside_vault"}.issubset(codes))
        self.assertTrue((self.project / "random-report.md").exists())

    def test_context_marks_truncation(self):
        self.init()
        self.add()
        path = self.root / "developments/DEV-001-sample/Current-State.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n" + "Detail. " * 1000, encoding="utf-8")
        result = self.cli("context", "--id", "DEV-001", "--max-chars", "1000")
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["current_state"]), 1000)

    def test_optional_pages_have_working_navigation_and_unique_identity(self):
        self.init()
        self.add()
        for name in vault.DETAIL:
            self.cli("page", "--id", "DEV-001", "--template", name)
        self.cli("page", "--id", "DEV-001", "--template", "decision", "--record-id", "ADR-001", "--title", "A proposed decision")
        self.assertTrue(self.cli("check")["ok"])
        before = self.snapshot()
        self.cli("page", "--id", "DEV-001", "--template", "design")
        self.assertEqual(before, self.snapshot())

    def test_duplicate_yaml_properties_are_not_silently_accepted(self):
        self.init()
        path = self.root / "Home.md"
        path.write_text(path.read_text(encoding="utf-8").replace("kind: guide", "kind: guide\nkind: other"), encoding="utf-8")
        self.assertIn("invalid_note", {i["code"] for i in self.cli("check", code=1)["issues"]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
