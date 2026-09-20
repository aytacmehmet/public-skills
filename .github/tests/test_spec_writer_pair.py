"""Protect the shared runtime and instruction structure of the localized Spec Writer pair."""
from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
EN = ROOT / 'en/spec-writer'
TR = ROOT / 'tr/belirtim-yazmani'
SECTIONS = [
    'scope', 'modes', 'entry_points', 'flow', 'json', 'writing', 'markers',
    'references', 'checks', 'report', 'commands', 'shape',
]


def payload(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def shape_rows(package):
    text = (package / 'SKILL.md').read_text(encoding='utf-8')
    block = text[text.index('<!-- BEGIN:SEKIL'):text.index('<!-- END:SEKIL')]
    return re.findall(r'^(\d\.\d{1,2}) .*?\| (\d+ [KNB]) \| ([^|]+) \|', block, re.M)


class SpecWriterPair(unittest.TestCase):
    def test_localized_packages_share_identical_runtime_assets_and_references(self):
        for shared in ('scripts', 'assets', 'references'):
            self.assertEqual(payload(EN / shared), payload(TR / shared), shared)

    def test_instructions_use_the_same_sections_in_workflow_order(self):
        for package in (EN, TR):
            text = (package / 'SKILL.md').read_text(encoding='utf-8')
            self.assertEqual(re.findall(r'^<([a-z_]+)>$', text, re.M), SECTIONS, package.name)
            self.assertEqual(re.findall(r'^</([a-z_]+)>$', text, re.M), SECTIONS, package.name)

    def test_both_shape_blocks_describe_the_same_content_model(self):
        english, turkish = shape_rows(EN), shape_rows(TR)
        self.assertEqual(len(english), 32)
        self.assertEqual(english, turkish)

    def test_self_test_passes_in_both_packages(self):
        for package in (EN, TR):
            result = subprocess.run(
                [sys.executable, '-B', str(package / 'scripts/oz_test.py')],
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=False,
            )
            self.assertEqual(result.returncode, 0, package.name + '\n' + result.stdout[-2000:] + result.stderr[-2000:])


if __name__ == '__main__':
    unittest.main()
