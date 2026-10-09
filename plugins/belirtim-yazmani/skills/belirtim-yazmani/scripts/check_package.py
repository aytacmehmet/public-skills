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
                  ('metadata/agent-plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json')]
    assert all(x['name'] == 'belirtim-yazmani' and x['version'] == '3.2.2' for x in identities)
    assert not (ROOT/'plugin.json').exists(), 'Native Codex 0.160 hooks require the legacy manifest format'
    manifest = json.loads((ROOT / 'PACKAGE-MANIFEST.json').read_text(encoding='utf-8'))
    assert manifest['version'] == identities[0]['version']
    files = {p.relative_to(ROOT).as_posix():p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc' and p.name != 'PACKAGE-MANIFEST.json'}
    assert set(files) == set(manifest['files']), 'Unlisted or missing package file'
    for name,path in files.items():
        expected = manifest['files'][name]
        assert len(path.read_bytes()) == expected['bytes'] and hashlib.sha256(path.read_bytes()).hexdigest() == expected['sha256'],name
    text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    rules = re.findall(r'^- \*\*(R-BYW-\d{2})\*\* ', text, re.M)
    assert rules == [f'R-BYW-{number:02d}' for number in range(1, 23)]
    for path in ('references/workflow.md', 'references/format.md', 'references/eval.md',
                 'references/work-profiles.md'):
        assert (SKILL / path).is_file() and path in text
    assert (ROOT / 'scripts/bv2.py').is_file()
    assert (ROOT / 'scripts/delivery.py').is_file()
    assert (ROOT / 'scripts/preflight.py').is_file()
    assert (ROOT / 'scripts/review_contract.py').is_file()
    for path in ('scripts/work_profiles.py', 'scripts/profile_runtime.py',
                 'scripts/profile_hooks.py', 'scripts/workspace_lock.py',
                 'scripts/dispatch_registry.py', 'scripts/source_pool.py',
                 'hooks/hooks.json', 'hooks/codex.json'):
        assert (ROOT / path).is_file(), f'Missing work-profile component: {path}'
    assert identities[0]['extensions']['com.openai']['hooks'] == './hooks/codex.json'
    assert identities[2]['hooks'] == './hooks/codex.json'
    for path in ('hooks/hooks.json', 'hooks/codex.json'):
        assert isinstance(json.loads((ROOT / path).read_text(encoding='utf-8'))['hooks'], dict)
    digest = hashlib.sha256((ROOT / 'vendor/toon/index.mjs').read_bytes()).hexdigest()
    assert digest in (ROOT / 'vendor/toon/NOTICE.md').read_text(encoding='utf-8')
    for path in ROOT.rglob('*'):
        assert not path.is_symlink()
    print('PASS: canonical skill, 22 rules, dual manifests, profile/hook components, runtime and codec pin')


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, OSError, ValueError) as error:
        print(f'FAIL: {error}')
        sys.exit(1)
