"""Protect the shared runtime and instruction structure of the localized SAP Fiori pair."""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
EN = ROOT / 'en/sap-fiori-design'
TR = ROOT / 'tr/sap-fiori-tasarim'
SKILLS = ROOT / '.github/scripts/skills.py'
SECTIONS = [
    'invariants', 'references', 'scope', 'evidence', 'contract', 'architecture', 'prototype',
    'production', 'verification', 'review', 'self_check', 'delivery', 'resources',
]
MAINTENANCE = ('behavior-checks.md', 'source-notes.md')


def payload(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def run(*arguments):
    return subprocess.run(
        [sys.executable, '-B', *map(str, arguments)],
        capture_output=True, text=True, encoding='utf-8', errors='replace', check=False,
    )


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
        numbering = []
        for package in (EN, TR):
            text = (package / 'SKILL.md').read_text(encoding='utf-8')
            links = re.findall(r'\]\((references/[^)]+)\)', text)
            self.assertTrue(links, package.name)
            for name in MAINTENANCE:
                self.assertNotIn(f'references/{name}', links, package.name)
                self.assertTrue((package / 'references' / name).is_file(), name)
            scenarios = (package / 'references/behavior-checks.md').read_text(encoding='utf-8')
            numbering.append(re.findall(r'^\| (FD\d\d) ', scenarios, re.M))
        self.assertEqual(numbering[0], numbering[1])
        self.assertEqual(numbering[0], [f'FD{n:02d}' for n in range(1, len(numbering[0]) + 1)])
        self.assertGreaterEqual(len(numbering[0]), 32)

    def test_every_validator_finding_a_designer_must_act_on_is_documented(self):
        source = (EN / 'scripts/validate_fiori_delivery.py').read_text(encoding='utf-8')
        codes = set(re.findall(r'"((?:CONTRACT|SEMANTIC)_[A-Z0-9_]+|PNG_NAME)"', source))
        explained = {'CONTRACT_PLACEHOLDER', 'CONTRACT_STATE_RECOMMENDED', 'SEMANTIC_STATES', 'SEMANTIC_I18N_KEY', 'SEMANTIC_ACTION_ID',
                     'CONTRACT_A11Y_EVIDENCE', 'CONTRACT_DATA_BUDGET', 'CONTRACT_COMMANDS', 'CONTRACT_RELEASED_UNVERIFIED',
                     'SEMANTIC_FLP_INBOUND', 'SEMANTIC_SEARCH_UNVERIFIED', 'PNG_NAME'}
        self.assertTrue(explained <= codes, explained - codes)
        for package in (EN, TR):
            guide = (package / 'references/delivery-and-quality.md').read_text(encoding='utf-8')
            for code in sorted(explained):
                self.assertIn(f'`{code}`', guide, f'{package.name}: {code}')

    def test_skill_tools_pass_from_both_packages(self):
        for package in (EN, TR):
            result = run(package / 'tests/test_skill_tools.py')
            self.assertEqual(result.returncode, 0, result.stderr[-2000:])

    def test_export_produces_a_renamed_copy_with_a_host_overlay(self):
        with tempfile.TemporaryDirectory() as directory:
            overlay = Path(directory) / 'host.md'
            overlay.write_text('## Host rules\n\nThe host owns routing and write permission.\n', encoding='utf-8')
            destination = Path(directory) / 'exported'
            result = run(SKILLS, 'export', 'tr/sap-fiori-tasarim', '--dest', destination, '--name', 'sap-fiori-design', '--overlay', overlay)
            self.assertEqual(result.returncode, 0, result.stderr)
            skill = (destination / 'SKILL.md').read_text(encoding='utf-8')
            self.assertIn('\nname: sap-fiori-design\n', skill)
            self.assertTrue(skill.rstrip().endswith('The host owns routing and write permission.'))
            self.assertIn('$sap-fiori-design', (destination / 'agents/openai.yaml').read_text(encoding='utf-8'))
            manifest = json.loads((destination / 'EXPORT-MANIFEST.json').read_text(encoding='utf-8'))
            self.assertEqual((manifest['source'], manifest['name'], manifest['overlay']), ('tr/sap-fiori-tasarim', 'sap-fiori-design', 'host.md'))
            self.assertFalse((destination / 'archived').exists())
            self.assertEqual(payload(destination / 'scripts'), payload(TR / 'scripts'))
            self.assertIn('\nname: sap-fiori-tasarim\n', (TR / 'SKILL.md').read_text(encoding='utf-8'))
            again = run(SKILLS, 'export', 'tr/sap-fiori-tasarim', '--dest', destination)
            self.assertEqual(again.returncode, 1)
            self.assertIn('not empty', again.stderr)
        inside = run(SKILLS, 'export', 'tr/sap-fiori-tasarim', '--dest', ROOT / 'tr' / 'copy')
        self.assertEqual(inside.returncode, 1)
        self.assertFalse((ROOT / 'tr' / 'copy').exists())


if __name__ == '__main__':
    unittest.main()
