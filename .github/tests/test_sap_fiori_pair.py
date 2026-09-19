"""Protect the shared runtime of the localized SAP Fiori pair and run its behavior tests."""
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
EN = ROOT / 'en/sap-fiori-design'
TR = ROOT / 'tr/sap-fiori-tasarim'


def payload(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


class FioriPair(unittest.TestCase):
    def test_localized_packages_share_identical_runtime_assets_and_tests(self):
        for shared in ('scripts', 'assets', 'tests'):
            self.assertEqual(payload(EN / shared), payload(TR / shared), shared)

    def test_localized_packages_carry_the_same_references(self):
        self.assertEqual(set(payload(EN / 'references')), set(payload(TR / 'references')))

    def test_skill_tools_pass_from_both_packages(self):
        for package in (EN, TR):
            result = subprocess.run(
                [sys.executable, '-B', str(package / 'tests/test_skill_tools.py')],
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr[-2000:])


if __name__ == '__main__':
    unittest.main()
