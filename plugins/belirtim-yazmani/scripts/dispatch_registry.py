# SPDX-License-Identifier: GPL-3.0-only
"""Bound concurrent dispatches across an explicitly shared coordination scope."""
import json
import os
import tempfile
from pathlib import Path

import bv2 as b
import workspace_lock

KIND = 'BYW_DISPATCH_REGISTRY'


def _path(doc, source):
    value = doc['delivery']['control']['work_profile']['capabilities'].get('coordinator_file')
    if not value:
        raise b.Invalid('Managed CLI dispatch requires its selected coordinator file')
    path = Path(value).absolute()
    if any(part.is_symlink() or getattr(part,'is_junction',lambda:False)() for part in (path,*path.parents)):
        raise b.Invalid('Coordinator cannot traverse links or junctions')
    path=path.resolve()
    if path == Path(source).resolve() or path.is_relative_to(b.ROOT) or path.suffix != '.json':
        raise b.Invalid('Coordinator must be a separate explicit JSON file outside the plugin')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _load(path):
    if not path.exists():return {'kind':KIND,'rows':[]}
    data = b.strict_json(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('kind') != KIND or not isinstance(data.get('rows'), list):
        raise b.Invalid('Coordinator is not a work-profile dispatch registry')
    keys = set()
    for row in data['rows']:
        if not isinstance(row, dict) or not all(isinstance(row.get(key), str) and row[key]
            for key in ('key', 'workspace', 'episode_id', 'attempt_id', 'task_id')):
            raise b.Invalid('Malformed shared dispatch identity')
        if row.get('status') not in ('RUNNING', 'PASS', 'FAIL', 'UNKNOWN', 'CANCELLED') or row['key'] in keys:
            raise b.Invalid('Malformed or duplicated shared dispatch result')
        keys.add(row['key'])
    return data


def _save(path, value):
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='\n',
                                      dir=path.parent, delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, sort_keys=True)
        temp = Path(stream.name)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _identity(doc, source, attempt):
    identity = {'workspace': str(Path(source).resolve()),
                'episode_id': doc['delivery']['control']['work_profile']['episode']['id'],
                'attempt_id': attempt['attempt_id']}
    return {**identity, 'key': b.digest(b.canonical(identity)),
            'task_id': attempt['task_id'], 'status': attempt['status']}


def assert_reserved(doc,source,attempt):
    """Read only: native leaf dispatch cannot invent a private reservation."""
    raw=doc['delivery']['control']['work_profile']['capabilities'].get('coordinator_file')
    if not isinstance(raw,str) or not raw:
        raise b.Invalid('Native dispatch requires its explicit shared coordinator file')
    path=Path(raw).absolute()
    if any(part.is_symlink() or getattr(part,'is_junction',lambda:False)() for part in (path,*path.parents)):
        raise b.Invalid('Coordinator cannot traverse links or junctions')
    path=path.resolve()
    if path==Path(source).resolve() or path.is_relative_to(b.ROOT) or path.suffix!='.json':
        raise b.Invalid('Coordinator must be a separate explicit JSON file outside the plugin')
    row=_identity(doc,source,attempt)
    if row['status']!='RUNNING' or not any(all(prior.get(k)==v for k,v in row.items()) for prior in _load(path)['rows']):
        raise b.Invalid('Native dispatch has no matching shared RUNNING reservation')
    return {'status':'RESERVED','attempt_id':row['attempt_id']}


def claim_native_dispatch(doc,source,attempt,host,tool_use_id):
    """Bind one charged reservation to one native call, idempotent per event ID."""
    assert_reserved(doc,source,attempt)
    if host not in ('codex','claude') or not isinstance(tool_use_id,str) or not tool_use_id.strip() or len(tool_use_id)>256:
        raise b.Invalid('Native dispatch requires a bounded host tool_use_id')
    path=Path(doc['delivery']['control']['work_profile']['capabilities']['coordinator_file']).resolve()
    expected=_identity(doc,source,attempt)
    with workspace_lock.held(path):
        data=_load(path)
        row=next((r for r in data['rows'] if all(r.get(k)==v for k,v in expected.items())),None)
        if row is None:raise b.Invalid('Shared dispatch changed before native admission')
        binding={'host':host,'tool_use_id':tool_use_id}
        if row.get('native_dispatch') is not None and row['native_dispatch']!=binding:
            raise b.Invalid('A different native call cannot reuse this reservation; begin a new charged attempt')
        if row.get('native_dispatch') is None:
            row['native_dispatch']=binding
            _save(path,data)
        return {'status':'NATIVE_CALL_BOUND','tool_use_id':tool_use_id,'attempt_id':attempt['attempt_id']}


def reserve(doc, source, attempt):
    """Reserve before saving workspace; crashes retain a conservative charged slot."""
    path = _path(doc, source)
    row = _identity(doc, source, attempt)
    if row['status'] != 'RUNNING':
        raise b.Invalid('Only a real running dispatch can reserve a shared slot')
    with workspace_lock.held(path,require_file=False):
        data = _load(path)
        prior = next((r for r in data['rows'] if r['key'] == row['key']), None)
        if prior:
            if not all(prior.get(k)==v for k,v in row.items()):
                raise b.Invalid('Shared reservation identity is already bound to another outcome')
            return
        limit = min(3, doc['delivery']['control']['work_profile']['capabilities']['child_limit'])
        if sum(r['status'] == 'RUNNING' for r in data['rows']) >= limit:
            raise b.Invalid('Shared coordination scope has no free child slot')
        data['rows'].append(row)
        _save(path, data)


def finish(doc, source, attempt):
    """Free the shared slot only after bound terminal workspace evidence is saved."""
    path = _path(doc, source)
    row = _identity(doc, source, attempt)
    if row['status'] == 'RUNNING':
        raise b.Invalid('Shared dispatch completion requires a terminal result')
    with workspace_lock.held(path,require_file=False):
        data = _load(path)
        prior = next((r for r in data['rows'] if r['key'] == row['key']), None)
        if prior is None:
            raise b.Invalid('Shared dispatch reservation is missing; inspect crash recovery evidence')
        if prior['status'] != 'RUNNING' and not all(prior.get(k)==v for k,v in row.items()):
            raise b.Invalid('Shared terminal result cannot be replaced')
        prior.update(row)
        _save(path, data)
