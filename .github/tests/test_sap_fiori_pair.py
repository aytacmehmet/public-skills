"""Protect the shared runtime and instruction structure of the localized SAP Fiori pair."""
from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
EN = ROOT / 'en/sap-fiori-design'
TR = ROOT / 'tr/sap-fiori-tasarim'
SECTIONS = [
    'invariants', 'references', 'scope', 'evidence', 'contract', 'architecture',
    'prototype', 'production', 'verification', 'self_check', 'delivery', 'resources',
]
MAINTENANCE = ('behavior-checks.md', 'source-notes.md')


def payload(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


class FioriPair(unittest.TestCase):
    def test_localized_packages_share_identical_runtime_assets_and_tests(self):
        for shared in ('scripts', 'assets', 'tests'):
            self.assertEqual(payload(EN / shared), payload(TR / shared), shared)

    def test_localized_packages_carry_the_same_references(self):
        self.assertEqual(set(payload(EN / 'references')), set(payload(TR / 'references')))

    def test_instructions_use_the_same_sections_in_workflow_order(self):
        for package in (EN, TR):
            text = (package / 'SKILL.md').read_text(encoding='utf-8')
            self.assertEqual(re.findall(r'^<([a-z_]+)>$', text, re.M), SECTIONS, package.name)
            self.assertEqual(re.findall(r'^</([a-z_]+)>$', text, re.M), SECTIONS, package.name)

    def test_maintenance_references_are_never_linked_from_the_instructions(self):
        for package in (EN, TR):
            text = (package / 'SKILL.md').read_text(encoding='utf-8')
            links = re.findall(r'\]\((references/[^)]+)\)', text)
            self.assertTrue(links, package.name)
            for name in MAINTENANCE:
                self.assertNotIn(f'references/{name}', links, package.name)
                self.assertTrue((package / 'references' / name).is_file(), name)
            scenarios = (package / 'references/behavior-checks.md').read_text(encoding='utf-8')
            self.assertEqual(re.findall(r'^\| (FD\d\d) ', scenarios, re.M), [f'FD{n:02d}' for n in range(1, 27)])

    def test_skill_tools_pass_from_both_packages(self):
        for package in (EN, TR):
            result = subprocess.run(
                [sys.executable, '-B', str(package / 'tests/test_skill_tools.py')],
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr[-2000:])


if __name__ == '__main__':
    unittest.main()
