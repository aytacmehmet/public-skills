"""Skill check: standard library only, no writes or model/SAP calls."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / 'skills/belirtim-yazmani'


def main():
    identities = [json.loads((ROOT / p).read_text(encoding='utf-8')) for p in
                  ('plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json')]
    assert all(x['name'] == 'belirtim-yazmani' and x['version'] == '2.0.2' for x in identities)
    manifest = json.loads((ROOT / 'PACKAGE-MANIFEST.json').read_text(encoding='utf-8'))
    assert manifest['version'] == identities[0]['version']
    files = {p.relative_to(ROOT).as_posix(): p for p in ROOT.rglob('*') if p.is_file() and p != ROOT / 'PACKAGE-MANIFEST.json'}
    assert set(manifest['files']) == set(files), 'Unlisted or missing package file'
    for name, path in files.items():
        expected = manifest['files'][name]
        assert path.stat().st_size == expected['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == expected['sha256'], name
    text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    rules = re.findall(r'^- \*\*(R-BYW-\d{2})\*\* ', text, re.M)
    assert len(rules) == 17 and len(rules) == len(set(rules))
    for path in ('references/workflow.md', 'references/format.md', 'references/eval.md'):
        assert (SKILL / path).is_file() and path in text
    assert (ROOT / 'scripts/bv2.py').is_file()
    assert (ROOT / 'scripts/delivery.py').is_file()
    digest = hashlib.sha256((ROOT / 'vendor/toon/index.mjs').read_bytes()).hexdigest()
    assert digest in (ROOT / 'vendor/toon/NOTICE.md').read_text(encoding='utf-8')
    for path in ROOT.rglob('*'):
        assert not path.is_symlink()
    print('PASS: package hashes, canonical skill, 17 rules, aligned manifests, runtime and codec pin')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, OSError, ValueError) as error:
        print(f'FAIL: {error}')
        sys.exit(1)
