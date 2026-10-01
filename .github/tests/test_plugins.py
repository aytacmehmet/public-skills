"""Exercise rejection controls for complete-plugin publication and Git history."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("plugin_tools", Path(__file__).parents[1] / "scripts/plugins.py")
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


class PluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="public-plugin-tests-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plugin = self.root / "plugins/demo"
        tools.git(self.root, "init", "-q", "-b", "main")
        tools.git(self.root, "config", "user.name", "Plugin Tests")
        tools.git(self.root, "config", "user.email", "plugin-tests@example.invalid")
        tools.git(self.root, "config", "core.autocrlf", "false")
        self.write(self.root / "LICENSE", "Fixture license\n")
        for catalog in ("README.md", "en/README.md", "tr/README.md"):
            self.write(self.root / catalog, "[Demo](plugins/demo/README.md)\n")
        for name in tools.REQUIRED:
            if name.endswith(".md"):
                self.write(self.plugin / name, "# Demo 1.0.0\n")
        self.write(self.plugin / "LICENSE", "Fixture license\n")
        for host in ("claude", "codex"):
            self.save(self.plugin / f".{host}-plugin/plugin.json", {"name": "demo", "version": "1.0.0"})
        for host, path in (("claude", ".claude-plugin/marketplace.json"), ("codex", ".agents/plugins/marketplace.json")):
            entry = {"name": "demo", "source": "./plugins/demo", "version": "1.0.0"}
            if host == "codex":
                entry = {"name": "demo", "source": {"source": "local", "path": "./plugins/demo"}, "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}}
            self.save(self.root / path, {"name": "aytacmehmet-public", "plugins": [entry]})
        self.skill = self.plugin / "skills/demo-skill"
        self.write(self.skill / "SKILL.md", '---\nname: demo-skill\ndescription: A complete plugin fixture.\nmetadata:\n  version: "1.0.0"\n---\n\n# Demo\n')
        for name in ("README.md", "README.tr.md"):
            self.write(self.skill / name, "# Demo skill\n")
        self.write(self.skill / "agents/openai.yaml", 'interface:\n  short_description: "A fixture for complete plugin testing"\n  default_prompt: "$demo-skill Run the fixture."\n')
        self.manifest()

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def save(self, path, value):
        self.write(path, json.dumps(value) + "\n")

    def manifest(self, version="1.0.0"):
        self.save(self.plugin / "PACKAGE-MANIFEST.json", {"version": version, "files": {
            path.relative_to(self.plugin).as_posix(): {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in self.plugin.rglob("*") if path.is_file() and path.name != "PACKAGE-MANIFEST.json"
        }})

    def commit(self):
        tools.git(self.root, "add", "--all")
        tools.git(self.root, "-c", "commit.gpgsign=false", "commit", "-qm", "Fixture release")
        return tools.git(self.root, "rev-parse", "HEAD").decode().strip()

    def test_complete_plugin_registers_only_its_verified_skill(self):
        self.assertEqual({str((self.skill / "SKILL.md").resolve())}, tools.validate_plugins(self.root))

    def test_missing_marketplace_and_wrong_source_are_rejected(self):
        path = self.root / ".agents/plugins/marketplace.json"
        original = tools.read(path)
        original["plugins"][0]["source"]["path"] = "../outside"
        self.save(path, original)
        with self.assertRaisesRegex(ValueError, "source differs"):
            tools.validate_plugins(self.root)
        path.unlink()
        with self.assertRaisesRegex(ValueError, "Missing marketplace"):
            tools.validate_plugins(self.root)

    def test_unlisted_payload_and_tampered_file_are_rejected(self):
        self.write(self.plugin / "unexpected.txt", "unexpected")
        with self.assertRaisesRegex(ValueError, "inventory differs"):
            tools.validate_plugins(self.root)
        self.manifest()
        self.write(self.plugin / "unexpected.txt", "altered")
        with self.assertRaisesRegex(ValueError, "hash/size mismatch"):
            tools.validate_plugins(self.root)

    def test_nested_skill_cannot_bypass_discovery(self):
        self.write(self.skill / "old/SKILL.md", "# Stale skill\n")
        self.manifest()
        with self.assertRaisesRegex(ValueError, "nested plugin skill"):
            tools.validate_plugins(self.root)

    def test_license_and_skill_version_are_independent_gates(self):
        self.write(self.plugin / "LICENSE", "Wrong license\n")
        self.manifest()
        with self.assertRaisesRegex(ValueError, "license differs"):
            tools.validate_plugins(self.root)
        self.write(self.plugin / "LICENSE", "Fixture license\n")
        self.write(self.skill / "SKILL.md", (self.skill / "SKILL.md").read_text().replace("1.0.0", "1.0.1"))
        self.manifest()
        with self.assertRaisesRegex(ValueError, "version/name differs"):
            tools.validate_plugins(self.root)

    def test_documentation_change_requires_release_bump(self):
        base = self.commit()
        self.write(self.plugin / "README.md", "# Changed Demo 1.0.0\n")
        self.manifest()
        with self.assertRaisesRegex(ValueError, "needs a version bump"):
            tools.validate_plugins(self.root, base)
        for path in self.plugin.rglob("*"):
            if path.is_file() and path.name != "PACKAGE-MANIFEST.json":
                self.write(path, path.read_text().replace("1.0.0", "1.0.1"))
        path = self.root / ".claude-plugin/marketplace.json"
        self.write(path, path.read_text().replace("1.0.0", "1.0.1"))
        self.manifest("1.0.1")
        tools.validate_plugins(self.root, base)

    def test_removing_all_plugins_and_marketplaces_cannot_bypass_history(self):
        base = self.commit()
        for relative in ("plugins", ".agents", ".claude-plugin"):
            path = (self.root / relative).resolve()
            self.assertTrue(path.is_relative_to(self.root.resolve()))
            shutil.rmtree(path)
        with self.assertRaisesRegex(ValueError, "published plugin removed"):
            tools.validate_plugins(self.root, base)


if __name__ == "__main__":
    unittest.main()
