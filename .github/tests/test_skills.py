"""Exercise release preservation with isolated, real Git histories."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

import yaml


spec = importlib.util.spec_from_file_location("skill_tools", Path(__file__).parents[1] / "scripts/skills.py")
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="public-skills-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_dir())
        tools.git(self.root, "init", "-q", "-b", "main")
        tools.git(self.root, "config", "user.name", "Skill Tests")
        tools.git(self.root, "config", "user.email", "skill-tests@example.invalid")
        tools.git(self.root, "config", "core.autocrlf", "false")
        (self.root / "LICENSE").write_text("Fixture license\n", encoding="utf-8")
        self.paths = ("en/prompter", "tr/yordamla")
        for relative, counterpart in zip(self.paths, reversed(self.paths)):
            folder = self.root / relative
            (folder / "agents").mkdir(parents=True)
            (folder / "archived").mkdir()
            (folder.parent / "README.md").write_text("# Catalog\n", encoding="utf-8")
            meta = {
                "name": folder.name,
                "description": "Fixture skill for release preservation tests.",
                "metadata": {
                    "version": "1.0.0", "language": relative.split("/")[0],
                    "family": "fixture", "counterpart": counterpart,
                },
            }
            self.write_skill(relative, meta)
            for name, content in {
                "README.md": "# Introduction\n",
                "CHANGELOG.md": "# Changelog\n\n## 1.0.0\n",
                "LICENSE": "Fixture license\n",
                "archived/README.md": "# Archives\n",
            }.items():
                (folder / name).write_text(content, encoding="utf-8")
            ui = {"interface": {
                "display_name": folder.name.title(),
                "short_description": "A fixture for testing release preservation",
                "default_prompt": f"${folder.name} Draft this fixture request.",
            }}
            (folder / "agents/openai.yaml").write_text(yaml.safe_dump(ui), encoding="utf-8")
        self.commit()

    def commit(self):
        tools.git(self.root, "add", "--all")
        tools.git(self.root, "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture release")
        return tools.resolve_ref(self.root, "HEAD")

    def write_skill(self, relative, meta):
        text = "---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n\n# Fixture instructions\n"
        (self.root / relative / "SKILL.md").write_text(text, encoding="utf-8")

    def bump(self, version, paths=None):
        for relative in paths or self.paths:
            folder = self.root / relative
            meta = tools.frontmatter((folder / "SKILL.md").read_bytes())
            meta["metadata"]["version"] = version
            self.write_skill(relative, meta)
            log = folder / "CHANGELOG.md"
            log.write_text(log.read_text(encoding="utf-8") + f"\n## {version}\n", encoding="utf-8")

    def archive_both(self):
        return [tools.archive(self.root, relative) for relative in self.paths]

    def test_first_release_has_two_active_packages_and_no_fake_archives(self):
        self.assertEqual(tools.validate(self.root, "HEAD"), 2)
        self.assertEqual(list(self.root.rglob("*.zip")), [])

    def test_archive_uses_committed_content_and_refuses_overwrite(self):
        relative = self.paths[0]
        before = tools.committed_payload(self.root, relative, tools.resolve_ref(self.root, "HEAD"))
        (self.root / relative / "README.md").write_text("Uncommitted revision\n", encoding="utf-8")
        snapshot = tools.archive(self.root, relative)
        manifest, payload = tools.read_archive(snapshot)
        self.assertEqual(payload, before)
        self.assertEqual(manifest["version"], "1.0.0")
        with self.assertRaisesRegex(ValueError, "immutable"):
            tools.archive(self.root, relative)

    def test_changed_package_requires_version_bump(self):
        (self.root / self.paths[0] / "README.md").write_text("Changed\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "version bump"):
            tools.validate(self.root, "HEAD")

    def test_version_bump_requires_previous_archive(self):
        self.bump("1.0.1")
        with self.assertRaisesRegex(ValueError, "Archive previous version"):
            tools.validate(self.root, "HEAD")

    def test_complete_bilingual_update_preserves_previous_payload(self):
        self.archive_both()
        self.bump("1.0.1")
        self.assertEqual(tools.validate(self.root, "HEAD"), 2)

    def test_next_snapshot_does_not_nest_older_archives(self):
        self.archive_both()
        self.bump("1.0.1")
        self.commit()
        snapshots = self.archive_both()
        self.bump("1.0.2")
        self.assertEqual(tools.validate(self.root, "HEAD"), 2)
        for snapshot in snapshots:
            _, payload = tools.read_archive(snapshot)
            self.assertFalse(any(name.startswith("archived/") for name in payload))
        self.assertEqual(len(list(self.root.rglob("*.zip"))), 4)

    def test_published_archive_bytes_are_immutable(self):
        snapshots = self.archive_both()
        self.bump("1.0.1")
        self.commit()
        with zipfile.ZipFile(snapshots[0], "a") as target:
            target.comment = b"A metadata-only change still changes published bytes"
        with self.assertRaisesRegex(ValueError, "Published archive changed"):
            tools.validate(self.root, "HEAD")

    def test_published_archive_cannot_be_removed(self):
        snapshots = self.archive_both()
        self.bump("1.0.1")
        self.commit()
        snapshots[0].unlink()
        with self.assertRaisesRegex(ValueError, "Published archive changed or was removed"):
            tools.validate(self.root, "HEAD")

    def test_language_versions_must_match(self):
        self.bump("1.0.1", [self.paths[0]])
        with self.assertRaisesRegex(ValueError, "Translation version mismatch"):
            tools.validate(self.root)

    def test_broken_local_link_is_rejected(self):
        (self.root / self.paths[0] / "README.md").write_text("[Missing](missing.md)\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Broken local link"):
            tools.validate(self.root)

    def test_unpacked_archived_skill_is_rejected(self):
        nested = self.root / self.paths[0] / "archived/v1.0.0"
        nested.mkdir()
        (nested / "SKILL.md").write_text("Old instructions\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Only ZIP snapshots"):
            tools.validate(self.root)

    def test_snapshot_content_tampering_is_detected(self):
        snapshot = tools.archive(self.root, self.paths[0])
        with zipfile.ZipFile(snapshot) as source:
            entries = {name: source.read(name) for name in source.namelist()}
        entries["README.md"] = b"Tampered content\n"
        # This is an isolated test artifact, never a published archive.
        with zipfile.ZipFile(snapshot, "w") as target:
            for name, data in entries.items():
                target.writestr(name, data)
        with self.assertRaisesRegex(ValueError, "hashes do not match"):
            tools.read_archive(snapshot)

    def test_archive_path_cannot_leave_language_roots(self):
        with self.assertRaisesRegex(ValueError, "Invalid skill path"):
            tools.archive(self.root, "../prompter")


if __name__ == "__main__":
    unittest.main()
