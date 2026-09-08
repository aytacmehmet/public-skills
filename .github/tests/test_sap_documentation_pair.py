"""Protect the shared runtime and English output contract of the localized pair."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
EN = ROOT / 'en/sap-development-documentation'
TR = ROOT / 'tr/sap-gelistirme-dokumantasyonu'


def payload(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


class DocumentationPair(unittest.TestCase):
    def test_localized_packages_share_identical_runtime_and_tests(self):
        self.assertEqual(payload(EN / 'scripts'), payload(TR / 'scripts'))

    def test_both_languages_generate_the_same_english_document_contract(self):
        english, turkish = payload(EN / 'assets'), payload(TR / 'assets')
        self.assertEqual(set(english), set(turkish))
        snippet = 'AGENTS-snippet.md'
        self.assertIn(b'$sap-gelistirme-dokumantasyonu', turkish[snippet])
        turkish[snippet] = turkish[snippet].replace(b'$sap-gelistirme-dokumantasyonu', b'$sap-development-documentation')
        self.assertEqual(english, turkish)


if __name__ == '__main__':
    unittest.main()
