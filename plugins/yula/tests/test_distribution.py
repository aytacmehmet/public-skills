"""Publication boundaries: ZIP integrity, bounded extraction and explicit storage."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "runtime"))
from yula import seed
from yula.common import YulaError, data_root, file_hash


class DistributionTests(unittest.TestCase):
    def setUp(self):
        base = Path(os.environ.get("YULA_TEST_ROOT", tempfile.gettempdir())).resolve()
        base.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=base, prefix="yula-distribution-")
        self.base = Path(self.temp.name)
        self.plugin = self.base / "plugin"
        (self.plugin / "data").mkdir(parents=True)
        self.staging = self.base / "staging"
        self.payload = b"SQLite format 3\x00" + b"fixture data" * 32
        self.bundle()

    def tearDown(self):
        self.temp.cleanup()

    def bundle(self, name="yula.sqlite", extra=False):
        archive = self.plugin / "data/yula.sqlite.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as out:
            out.writestr(name, self.payload)
            if extra:
                out.writestr("unexpected", b"extra data")
        self.manifest = {"bytes": len(self.payload), "sha256": hashlib.sha256(self.payload).hexdigest(),
                         "distribution": {"format": "zip", "path": "yula.sqlite.zip", "member": "yula.sqlite",
                                          "bytes": archive.stat().st_size, "sha256": file_hash(archive)}}
        self.save()
        return archive

    def save(self):
        (self.plugin / "data/manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def reject(self, code):
        with patch.object(seed, "PLUGIN", self.plugin), self.assertRaises(YulaError) as caught:
            with seed.unpack_seed(self.staging):
                self.fail("Invalid archive yielded a seed")
        self.assertEqual(code, caught.exception.code)
        self.assertFalse(list(self.staging.glob("seed-*.tmp")))
        self.assertFalse((self.staging / "current.json").exists())

    def test_valid_archive_is_lossless_and_temporary(self):
        with patch.object(seed, "PLUGIN", self.plugin):
            with seed.unpack_seed(self.staging) as path:
                self.assertEqual(self.payload, path.read_bytes())
                self.assertTrue(path.is_relative_to(self.staging))
            self.assertFalse(path.exists())

    def test_archive_hash_and_expanded_hash_are_separate_gates(self):
        self.manifest["distribution"]["sha256"] = "0" * 64
        self.save()
        self.reject("SEED_CORRUPT")
        self.bundle()
        self.manifest["sha256"] = "0" * 64
        self.save()
        self.reject("SEED_CORRUPT")

    def test_path_traversal_and_extra_entries_are_rejected(self):
        self.bundle("../escaped.sqlite")
        self.reject("SEED_FORMAT")
        self.assertFalse((self.base / "escaped.sqlite").exists())
        self.bundle(extra=True)
        self.reject("SEED_FORMAT")

    def test_size_claims_are_bounded_and_exact(self):
        self.manifest["bytes"] -= 1
        self.save()
        self.reject("SEED_SIZE")
        self.manifest["bytes"] = seed.MAX_SEED_BYTES + 1
        self.save()
        self.reject("SEED_SIZE")

    def test_corrupt_archive_with_updated_outer_hash_is_rejected(self):
        archive = self.plugin / "data/yula.sqlite.zip"
        archive.write_bytes(b"not a ZIP")
        self.manifest["distribution"].update(bytes=archive.stat().st_size, sha256=file_hash(archive))
        self.save()
        self.reject("SEED_CORRUPT")

    def test_staging_is_removed_after_caller_failure(self):
        with patch.object(seed, "PLUGIN", self.plugin), self.assertRaises(RuntimeError):
            with seed.unpack_seed(self.staging):
                raise RuntimeError("Interrupted SQLite validation")
        self.assertFalse(list(self.staging.glob("seed-*.tmp")))

    def test_explicit_selector_respects_external_environment_override(self):
        with patch.dict(os.environ, {"YULA_DATA_ROOT": str(self.staging)}):
            self.assertEqual(self.staging, data_root("@user/yula"))
            self.assertEqual(self.base / "explicit", data_root(str(self.base / "explicit")))
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(YulaError) as caught:
                data_root()
            self.assertEqual("DATA_ROOT_REQUIRED", caught.exception.code)
        with self.assertRaises(YulaError):
            data_root(str(ROOT / "data"))

    def test_cli_without_target_fails_before_writing(self):
        env = {k: v for k, v in os.environ.items() if k != "YULA_DATA_ROOT"}
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/yula.py"), "init"],
                                cwd=self.base, env=env, capture_output=True, timeout=15)
        self.assertEqual(2, result.returncode)
        self.assertEqual("DATA_ROOT_REQUIRED", json.loads(result.stdout)["error"])
        self.assertFalse((self.base / "current.json").exists())

    def test_delivery_manifest_and_zip_use_case_sensitive_posix_order(self):
        output = self.base / "delivery"
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/build_package.py"),
                                 "--output-dir", str(output)], cwd=self.base, capture_output=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stderr.decode("utf-8", errors="replace"))
        manifest = json.loads((output / "PACKAGE-MANIFEST.json").read_text(encoding="utf-8"))
        names = list(manifest["files"])
        self.assertEqual(sorted(names), names)
        report = json.loads(result.stdout)
        with zipfile.ZipFile(output / report["zip"]) as bundle:
            payload = [name.removeprefix("yula-marketplace/plugins/yula/") for name in bundle.namelist()[3:]]
            self.assertEqual(names, payload)
            self.assertEqual("aytacmehmet-public", json.loads(bundle.read("yula-marketplace/.agents/plugins/marketplace.json"))["name"])


if __name__ == "__main__":
    unittest.main()
