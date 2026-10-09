# SPDX-License-Identifier: GPL-3.0-only
"""Read-only input closure before independent readers; no release approval."""
import json
from pathlib import Path
import bv2 as b


def asset_snapshot(doc, root):
    import handoff3 as h
    _, control = h.state(doc)
    files, sources = {}, {}
    for asset in control.get('assets', []):
        name, data = h.copy_asset(asset, root)
        if name in files:
            raise b.Invalid('Duplicate asset path: ' + name)
        files[name] = data
        physical = asset.get('source_path', name)
        sources[name] = str(Path(root).resolve().joinpath(*b.safe_name(physical).parts))
    return files, sources


def checker_hash():
    paths = sorted((b.ROOT / 'scripts').glob('*.py'))
    paths += [b.ROOT / 'scripts/codec.mjs', b.ROOT / 'schema/handoff.schema.json',
              b.ROOT / 'schema/handoff-v2.schema.json', b.ROOT / 'vendor/toon/index.mjs']
    return b.digest(b.canonical({str(path.relative_to(b.ROOT)): b.digest(path.read_bytes())
                                 for path in paths}))


def inspect(doc, assets_root):
    import delivery as d
    import handoff3 as h
    spec, control = d.get_state(doc)
    issues = d.shape_and_profile(spec)
    if issues:
        return {'status': 'BLOCKED', 'issues': issues, 'assets': [], 'references': []}
    report = d.evaluate(doc)
    # Snapshot approval and final readers remain separate gates. Business defaults
    # must already be approved before spending independent-reader resources.
    issues += [row for row in report['issues']
               if not row['code'].startswith('F') and row['code'] not in ('APPROVAL_CURRENT','WORK_PROFILE_GATE')]
    if assets_root is None:
        issues.append(d.issue('INPUT_ROOT_REQUIRED', '/assets', 'Supply the physical assets root'))
        return {'status': 'BLOCKED', 'issues': issues, 'assets': [], 'references': []}
    try:
        files, sources = asset_snapshot(doc, assets_root)
        roles = h.layout(spec)
        documents = h.public_documents(spec, report)
        files.update({roles[key]: text.encode('utf-8') for key, text in b.encode_many(documents).items()})
        files.update(h.public_text(spec))
        # Presence of generated optional projections is known without writing them.
        for role in ('readme', 'manifest', 'excel'):
            files.setdefault(roles[role], b'placeholder: true\n' if role == 'manifest' else b'')
        contracts = h.dependency_records(doc)
        if set(contracts) != {row['development_id'] for row in spec['dependencies']}:
            raise b.Invalid('Every dependency needs its local contract')
        for dep in spec['dependencies']:
            row = contracts[dep['development_id']]
            if row.get('version') != dep['version'] or row.get('contract') != dep['contract'] or not row.get('content'):
                raise b.Invalid('Dependency version/contract/content differs')
        files[roles['dependency_contracts']] = b.encode({'contracts': list(contracts.values())}).encode()
        for media in spec['media']:
            if media['path'] not in sources or b.digest(files[media['path']]) != media['sha256']:
                raise b.Invalid('PNG snapshot missing or changed: ' + media['path'])
        for path in spec['baseline']['evidence_paths']:
            if path not in files:
                raise b.Invalid('Baseline evidence missing: ' + path)
        if spec['meta']['mode'] == 'UPDATE':
            raw = control.get('baseline_reference_path')
            if not raw:
                raise b.Invalid('Exact baseline artifact required')
            root = Path(assets_root).resolve()
            path = root.joinpath(*b.safe_name(raw).parts)
            if path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file():
                raise b.Invalid('Baseline artifact missing or escaped')
            if b.digest(path.read_bytes()) != spec['baseline']['reference_sha256']:
                raise b.Invalid('Baseline artifact hash differs')
            if spec['baseline']['kind'] == 'FINAL_HANDOFF':
                verified = d.verify(path)
                if verified['specSha256'] != spec['baseline']['spec_sha256'] or path.name != spec['baseline']['reference_name']:
                    raise b.Invalid('Baseline identity differs')
            files[roles['baseline']] = b.encode(spec['baseline']).encode()
            files[roles['baseline_spec']] = b.encode(control['baseline_spec']).encode()
            files[roles['changes']] = b.encode(d.changes(control['baseline_spec'], spec)).encode()
        import source_pool
        decoded = source_pool.decode_documents(files)
        h.verify_references(spec, files, decoded=decoded)
        assets = [{'path': name, 'source_path': sources[name], 'sha256': b.digest(data)}
                  for name, data in files.items() if name in sources]
        references, pool = source_pool.collect(spec['references'], files, decoded=decoded)
        source_pool.size(pool, source_pool.limits(control)[0])
        result = {'status': 'PASS' if not issues else 'BLOCKED', 'issues': issues,
                  'assets': assets, 'references': references, 'source_pool': pool,
                  'dependency_contracts': list(contracts.values()), 'spec_sha256': d.revision(spec)}
        result['input_sha256'] = b.digest(b.canonical({'spec': d.revision(spec), 'assets': assets,
                                                      'contracts': list(contracts.values()),
                                                      'source_pool': source_pool.value_sha(pool),
                                                      'checker': checker_hash()}))
        return result
    except (b.Invalid, OSError, KeyError, ValueError, TypeError) as error:
        issues.append(d.issue('INPUT_CLOSURE', '/assets', str(error)))
        return {'status': 'BLOCKED', 'issues': issues, 'assets': [], 'references': []}


def status(doc, assets_root):
    import delivery as d
    report = d.evaluate(doc)
    inputs = inspect(doc, assets_root)
    if inputs['status'] != 'PASS':
        action = 'Resolve the listed profile, business and input issues; rerun preflight'
    elif any(row['code'] == 'APPROVAL_CURRENT' for row in report['issues']):
        action = 'Obtain genuine approval of this exact specification snapshot'
    elif any(row['code'].startswith('F') for row in report['issues']):
        action = 'Run fresh isolated eval-request readers, record actual answers, then confirm execution'
    else:
        action = 'Verify and publish the immutable handoff or coordinated batch'
    return {'decision': report['decision'], 'coding_readiness': report['coding_readiness'],
            'preflight': inputs['status'], 'issues': report['issues'] + inputs['issues'],
            'next_action': action, 'scope': 'Read-only guidance; no automatic decisions or approval'}
