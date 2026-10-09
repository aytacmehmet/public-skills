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
    path = workspace_lock.checked_path(value)
    if path == Path(source).resolve() or path.is_relative_to(b.ROOT) or path.suffix != '.json':
        raise b.Invalid('Coordinator must be a separate explicit JSON file outside the plugin')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _load(path):
    if not path.exists():return {'kind':KIND,'rows':[],'participants':[]}
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
        if 'concurrency_limit' in row and (type(row['concurrency_limit']) is not int or not 1<=row['concurrency_limit']<=3):
            raise b.Invalid('Malformed shared profile concurrency')
    data.setdefault('participants',[])
    participants=set()
    for row in data['participants']:
        if not isinstance(row,dict) or not all(isinstance(row.get(key),str) and row[key] for key in ('workspace','episode_id','profile')) or row.get('status') not in ('ACTIVE','FINISHED') or type(row.get('concurrency_limit')) is not int or not 0<=row['concurrency_limit']<=3:
            raise b.Invalid('Malformed shared profile participant')
        identity=(row['workspace'],row['episode_id'])
        if identity in participants:raise b.Invalid('Duplicate shared profile participant')
        participants.add(identity)
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
    import work_profiles as w
    return {**identity, 'key': b.digest(b.canonical(identity)),
            'task_id': attempt['task_id'], 'status': attempt['status'],
            'concurrency_limit':w.status(doc)['limits']['concurrent_children']}


def _participant(doc,source):
    import work_profiles as w
    state=doc['delivery']['control']['work_profile']
    return {'workspace':str(Path(source).resolve()),'episode_id':state['episode']['id'],
            'profile':state['selected'],'concurrency_limit':w.status(doc)['limits']['concurrent_children'],
            'status':'ACTIVE'}


def _register(data,participant):
    prior=next((row for row in data['participants'] if row['workspace']==participant['workspace'] and row['episode_id']==participant['episode_id']),None)
    if prior is None:data['participants'].append(participant)
    else:prior.update(participant)


def _scope_limit(data):
    limits=[row['concurrency_limit'] for row in data['participants'] if row['status']=='ACTIVE']
    for row in data['rows']:
        if row['status']=='RUNNING':
            if 'concurrency_limit' not in row:
                raise b.Invalid('Legacy running reservation needs owner recovery before current dispatch')
            limits.append(row['concurrency_limit'])
    return min([3]+limits)


def register_selection(doc,source):
    """Bind selected profiles to one coordinated scope without launching children."""
    path=_path(doc,source)
    with workspace_lock.held(path,require_file=False):
        data=_load(path)
        _register(data,_participant(doc,source))
        if sum(row['status']=='RUNNING' for row in data['rows'])>_scope_limit(data):
            raise b.Invalid('Shared scope is busy above the selected lower profile; wait before selecting')
        _save(path,data)


def finish_selection(doc,source):
    """Close scope participation after saved successful handoff; retain history."""
    path=_path(doc,source)
    participant=_participant(doc,source)
    with workspace_lock.held(path,require_file=False):
        data=_load(path)
        matches=lambda row:row['workspace']==participant['workspace'] and row['episode_id']==participant['episode_id']
        if any(matches(row) and row['status']=='RUNNING' for row in data['rows']):
            raise b.Invalid('Cannot finish a scope with running children')
        for row in data['participants']:
            if matches(row):row['status']='FINISHED'
        _save(path,data)


def assert_reserved(doc,source,attempt):
    """Read only: native leaf dispatch cannot invent a private reservation."""
    raw=doc['delivery']['control']['work_profile']['capabilities'].get('coordinator_file')
    if not isinstance(raw,str) or not raw:
        raise b.Invalid('Native dispatch requires its explicit shared coordinator file')
    path=workspace_lock.checked_path(raw)
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
        _register(data,_participant(doc,source))
        limit = _scope_limit(data)
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
