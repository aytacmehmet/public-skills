# SPDX-License-Identifier: GPL-3.0-only
"""Private work planning and admission; no provider, model or filesystem mutation.

The CLI owns locking and atomic persistence. A receipt records caller evidence; it
does not authenticate a provider run. Existing A-F release gates remain separate.
"""
import copy
import itertools
import json
import re
import uuid
from datetime import datetime, timezone

import bv2 as b


VERSION = 1
FACTORS = ('size', 'complexity', 'dependencies', 'uncertainty', 'impact', 'evidence_gap')
WEIGHTS = (1, 2, 2, 2, 3, 2)
PROFILE_NAMES = ('lite', 'plus', 'pro', 'max', 'ultra')
LABELS = ('Yalın', 'Gelişmiş', 'Yetkin', 'Doruk', 'Üstün')
PREP_LIMITS = (0, 1, 2, 4, 6)
CHILD_LIMITS = (1, 1, 2, 3, 3)
SHA = re.compile(r'^[a-f0-9]{64}$')
TERMINAL = {'PASS', 'FAIL', 'CANCELLED', 'UNKNOWN'}
OPERATIONS = {'prepare', 'write', 'review', 'release'}


def _error(code, message, **details):
    raise b.Invalid(json.dumps({'code': 'WORK_PROFILE_' + code, 'message': message,
                                **details}, ensure_ascii=False, sort_keys=True))


def _now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')


def _sha(value, field):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        _error('HASH', 'A lowercase SHA-256 binding is required', field=field)
    return value


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        _error('TEXT', 'A nonempty string is required', field=field)
    return value


def catalog():
    """Return a fresh profile catalog. Suggestions never change a host setting."""
    codex = [('gpt-6.1-sol', 'medium'), ('gpt-6.1-sol', 'medium'),
             ('gpt-6.1-sol', 'high'), ('gpt-6.1-sol', 'xhigh'),
             ('gpt-6-astra', 'high')]
    claude = [('claude-sonnet-5-5', 'medium'), ('claude-sonnet-5-5', 'high'),
              ('claude-sonnet-5-5', 'high'), ('claude-opus-5-5', 'high'),
              ('claude-opus-5-5', 'xhigh')]
    profiles = []
    for index, name in enumerate(PROFILE_NAMES):
        profiles.append({'id': name, 'name': name.title(), 'label_tr': LABELS[index],
          'limits': {'preparation_attempts': PREP_LIMITS[index], 'review_attempts': 12,
                     'total_attempts': PREP_LIMITS[index] + 12,
                     'concurrent_children': CHILD_LIMITS[index]},
          'model_suggestions': {host: {'model': pair[0], 'reasoning': pair[1],
                                      'availability': 'UNKNOWN', 'applied': False}
                                for host, pair in [('codex', codex[index]),
                                                   ('claude', claude[index])]},
          'quality': {'full_readers_per_round': 3, 'consecutive_clean_rounds': 2,
                      'round_limit': 4, 'nested_children_allowed': False,
                      'single_writer': True, 'quality_reduction_allowed': False}})
    return {'version': VERSION, 'profiles': profiles, 'global_child_limit': 3,
            'thresholds_calibrated': False, 'model_application': 'RECOMMENDATION_ONLY',
            'provider_benchmark': 'NOT_RUN'}


def _assessment(assessment):
    if assessment is None:
        assessment = {}
    if not isinstance(assessment, dict):
        _error('ASSESSMENT', 'Assessment must be an object')
    supplied = assessment.get('factors', assessment)
    if not isinstance(supplied, dict):
        _error('ASSESSMENT', 'Assessment factors must be an object')
    normalized = {}
    for name in FACTORS:
        raw = supplied.get(name)
        row = copy.deepcopy(raw) if isinstance(raw, dict) else {'score': raw}
        value = row.get('score')
        if value is not None and (isinstance(value, bool) or not isinstance(value, int)
                                  or not 0 <= value <= 4):
            _error('ASSESSMENT', 'Factor scores must be integers in 0..4 or null', factor=name)
        for field in ('rationale', 'source'):
            if field not in row:
                continue
            source = row[field]
            if field == 'source' and isinstance(source, list):
                if not all(isinstance(item, str) and item.strip() for item in source):
                    _error('ASSESSMENT', 'Factor source list must contain nonempty strings', factor=name)
            elif not isinstance(source, str):
                _error('ASSESSMENT', 'Factor rationale/source must be text', factor=name, field=field)
        normalized[name] = row
    counts = copy.deepcopy(assessment.get('counts', {}))
    if not isinstance(counts, dict) or set(counts) - {'requirements', 'objects', 'assets'}:
        _error('COUNTS', 'Counts must contain requirements, objects and/or assets')
    for name, value in counts.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            _error('COUNTS', 'Counts must be nonnegative integers', field=name)
    size_floor = 0
    for name, limits in {'requirements': (10, 25, 60, 120),
                         'objects': (3, 8, 20, 40), 'assets': (3, 8, 20, 40)}.items():
        if name in counts:
            size_floor = max(size_floor, sum(counts[name] > limit for limit in limits))
    if normalized['size']['score'] is not None:
        normalized['size']['score'] = max(normalized['size']['score'], size_floor)
    blockers = copy.deepcopy(assessment.get('preparation_blockers', []))
    if not isinstance(blockers, list) or not all(isinstance(item, str) and item.strip() for item in blockers):
        _error('ASSESSMENT', 'Preparation blockers must be a list of nonempty strings')
    return {'factors': normalized, 'counts': counts, 'size_floor': size_floor,
            'preparation_blockers': blockers}


def _rank(scores):
    score = sum(value * weight for value, weight in zip(scores, WEIGHTS))
    rank = sum(score > threshold for threshold in (8, 17, 28, 38))
    if scores[0] >= 3:
        rank = max(rank, 2)
    if scores[4] >= 3:
        rank = max(rank, 3)
    if scores[2] == 4 and scores[4] >= 3:
        rank = 4
    return score, rank


def recommend(assessment):
    """Enumerate unknowns with each risk/volume floor, never infer unknown=0."""
    normalized = _assessment(assessment)
    scores = [normalized['factors'][name]['score'] for name in FACTORS]
    candidates = [range(normalized['size_floor'], 5) if index == 0 and value is None
                  else range(5) if value is None else (value,)
                  for index, value in enumerate(scores)]
    outcomes = [_rank(values) for values in itertools.product(*candidates)]
    possible = sorted({rank for _, rank in outcomes})
    unknown = [name for name, value in zip(FACTORS, scores) if value is None]
    blockers = normalized['preparation_blockers']
    state = 'BLOCKED_PREPARATION' if blockers else 'PENDING' if unknown else 'PASS'
    return {'status': state, 'recommended': None if unknown else PROFILE_NAMES[possible[0]],
            'possible_profiles': [PROFILE_NAMES[index] for index in possible],
            'score_min': min(score for score, _ in outcomes),
            'score_max': max(score for score, _ in outcomes), 'unknown_factors': unknown,
            'assessment': normalized, 'confidence': 'INCOMPLETE' if unknown else 'DESIGN_UNCALIBRATED',
            'rules': {'impact_at_least_3': 'max', 'dependencies_4_and_impact_at_least_3': 'ultra',
                      'size_at_least_3': 'pro'}, 'thresholds_calibrated': False}


def _control(doc):
    try:
        control = doc['delivery']['control']
        spec = doc['delivery']['spec']
    except (KeyError, TypeError):
        _error('WORKSPACE', 'Use a delivery workspace with private delivery.control')
    if not isinstance(control, dict) or not isinstance(spec, dict):
        _error('WORKSPACE', 'Delivery specification and controls must be objects')
    if 'work_profile_required' in control and type(control['work_profile_required']) is not bool:
        _error('STATE', 'work_profile_required must be a boolean')
    return control, spec


def _state_hash(state):
    return b.digest(b.canonical({key: value for key, value in state.items() if key != 'state_sha256'}))


def _seal(state):
    state['state_sha256'] = _state_hash(state)


def _validated(doc):
    control, _ = _control(doc)
    if 'work_profile' not in control:
        return None
    state = control['work_profile']
    if not isinstance(state, dict) or type(state.get('version')) is not int or state['version'] != VERSION:
        _error('STATE', 'Unsupported or malformed private work profile state')
    if state.get('selected') not in PROFILE_NAMES or not isinstance(state.get('attempts'), list):
        _error('STATE', 'Malformed profile selection or attempt ledger')
    if not isinstance(state.get('selection_history'), list) or not state['selection_history']:
        _error('STATE', 'Explicit selection history is required')
    if not isinstance(state.get('episode'), dict) or not isinstance(state['episode'].get('id'), str):
        _error('STATE', 'An episode identity is required')
    try:
        actual = _state_hash(state)
    except (TypeError, ValueError) as error:
        _error('STATE', 'State is not canonical JSON', reason=str(error))
    if state.get('state_sha256') != actual:
        _error('INTEGRITY', 'Private state digest differs; do not repair by discarding attempt history')
    for field in ('capabilities', 'capacity', 'assessment', 'recommendation'):
        if not isinstance(state.get(field), dict):
            _error('STATE', 'Required state object is missing', field=field)
    _capabilities(state['capabilities'])
    capacity = state['capacity']
    if capacity.get('status') not in ('PASS', 'PENDING', 'BLOCKED'):
        _error('STATE', 'Capacity status is missing or invalid')
    for field in ('spec_sha256', 'checker_sha256'):
        _sha(capacity.get(field), 'capacity.' + field)
    if capacity.get('input_sha256') is not None:
        _sha(capacity['input_sha256'], 'capacity.input_sha256')
    computed_recommendation = recommend(state['assessment'])
    if state['recommendation'] != computed_recommendation:
        _error('STATE', 'Recommendation must match the persisted assessment')
    for selection in state['selection_history']:
        if not isinstance(selection, dict) or selection.get('profile') not in PROFILE_NAMES:
            _error('STATE', 'Malformed selection history')
        receipt = selection.get('receipt')
        if not isinstance(receipt, dict) or receipt.get('confirmed') is not True:
            _error('STATE', 'Caller-confirmed selection receipt is missing')
        _text(receipt.get('receipt'), 'selection.receipt')
    seen = set()
    contexts = set()
    for row in state['attempts']:
        if not isinstance(row, dict) or row.get('role') not in ('prep', 'reviewer'):
            _error('STATE', 'Malformed attempt role')
        for field in ('task_id', 'attempt_id', 'started_at'):
            _text(row.get(field), field)
        if 'context_id' not in row or (row['context_id'] is not None
                                      and not isinstance(row['context_id'], str)):
            _error('STATE', 'Attempt context must be a string or null')
        _sha(row.get('input_sha256'), 'input_sha256')
        if row['attempt_id'] in seen or row.get('status') not in TERMINAL | {'RUNNING'}:
            _error('STATE', 'Duplicate attempt identity or invalid status')
        seen.add(row['attempt_id'])
        if row['role'] == 'reviewer':
            context = _text(row.get('context_id'), 'context_id')
            if context in contexts:
                _error('ISOLATION', 'Reader contexts must be unique across the entire episode')
            contexts.add(context)
        if row['status'] != 'RUNNING':
            _text(row.get('finished_at'), 'finished_at')
            evidence = row.get('evidence')
            if not isinstance(evidence, dict):
                _error('STATE', 'Terminal attempt requires evidence object')
            completion = {key: row[key] for key in ('status', 'input_sha256', 'context_id', 'evidence')}
            if row.get('completion_sha256') != b.digest(b.canonical(completion)):
                _error('EVIDENCE_BINDING', 'Terminal completion digest differs')
            if row['status'] == 'PASS':
                _sha(evidence.get('response_sha256'), 'evidence.response_sha256')
                _text(evidence.get('receipt'), 'evidence.receipt')
        for field in ('spec_sha256', 'checker_sha256'):
            _sha(row.get(field), 'attempt.' + field)
        if 'diagnosis' in row:
            _text(row['diagnosis'], 'attempt.diagnosis')
    limits, usage = _limits(state), _usage(state)
    if any(usage[key] > limits[key] for key in ('preparation_attempts', 'review_attempts', 'total_attempts')):
        _error('BUDGET', 'Persisted attempt ledger exceeds the selected episode budget')
    if usage['running_children'] > limits['concurrent_children']:
        _error('CONCURRENCY', 'Persisted running attempts exceed the child limit')
    return state


def _checker_sha():
    import preflight
    return preflight.checker_hash()


def _capabilities(value):
    if value is None:
        return {}
    if not isinstance(value, dict):
        _error('CAPABILITIES', 'Host capabilities must be an object')
    result = copy.deepcopy(value)
    for field in ('reader_isolation', 'vision'):
        if field in result and type(result[field]) is not bool:
            _error('CAPABILITIES', 'Capability flags must be booleans', field=field)
    limit = result.get('child_limit')
    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 3):
        _error('CAPABILITIES', 'Host child_limit must be an integer in 1..3')
    if 'host' in result and result['host'] not in ('codex', 'claude', 'manual'):
        _error('CAPABILITIES', 'Use codex, claude or manual host identification')
    return result


def _capacity(value, spec):
    if value is None:
        value = {'status': 'PENDING'}
    if not isinstance(value, dict) or value.get('status') not in ('PASS', 'PENDING', 'BLOCKED'):
        _error('CAPACITY', 'Capacity status must be PASS, PENDING or BLOCKED')
    result = copy.deepcopy(value)
    current_spec = b.digest(b.canonical(spec))
    current_checker = _checker_sha()
    for field, actual in [('spec_sha256', current_spec), ('checker_sha256', current_checker)]:
        if field in result and result[field] != actual:
            _error('CAPACITY_STALE', 'Capacity binding differs from current source', field=field)
        result[field] = actual
    if result.get('input_sha256') is not None:
        _sha(result['input_sha256'], 'capacity.input_sha256')
    result['evidence_scope'] = 'RECORDED_NOT_PROVIDER_AUTHENTICATED'
    return result


def _limits(state):
    index = PROFILE_NAMES.index(state['selected'])
    host_limit = state['capabilities'].get('child_limit')
    return {'preparation_attempts': PREP_LIMITS[index], 'review_attempts': 12,
            'total_attempts': 12 + PREP_LIMITS[index],
            'concurrent_children': min(CHILD_LIMITS[index], host_limit or 0, 3)}


def _usage(state):
    return {'preparation_attempts': sum(row['role'] == 'prep' for row in state['attempts']),
            'review_attempts': sum(row['role'] == 'reviewer' for row in state['attempts']),
            'total_attempts': len(state['attempts']),
            'running_children': sum(row['status'] == 'RUNNING' for row in state['attempts'])}


def _model_suggestion(state):
    host = state['capabilities'].get('host')
    profile = next(row for row in catalog()['profiles'] if row['id'] == state['selected'])
    suggestion = copy.deepcopy(profile['model_suggestions'].get(host))
    if suggestion is None:
        return None
    suggestion.update(host=host, recommendation_only=True, applied=False,
                      reasoning_availability='UNKNOWN', provider_execution='NOT_RUN')
    observed = state['capabilities'].get('model_catalog')
    if not isinstance(observed, dict) or observed.get('observed') is not True:
        return suggestion
    source = observed.get('source')
    rows = observed.get('models')
    if not isinstance(source, str) or not source.strip() or not isinstance(rows, list):
        return suggestion
    for row in rows:
        model_id = row.get('id') if isinstance(row, dict) else row
        if model_id != suggestion['model']:
            continue
        suggestion['availability'] = 'OBSERVED_CATALOG_MATCH'
        suggestion['catalog_source'] = source
        if isinstance(row, dict) and isinstance(row.get('reasoning'), list):
            if suggestion['reasoning'] in row['reasoning']:
                suggestion['reasoning_availability'] = 'OBSERVED_CATALOG_MATCH'
        break
    return suggestion


def choose(doc, profile, assessment=None, capabilities=None, capacity=None, receipt=None):
    """Explicit opt-in/update, retaining the episode and every charged attempt."""
    if profile not in PROFILE_NAMES:
        _error('SELECTION', 'Choose lite, plus, pro, max or ultra')
    if not isinstance(receipt, dict) or receipt.get('confirmed') is not True:
        _error('CONFIRMATION', 'Explicit caller-confirmed user profile selection is required')
    _text(receipt.get('receipt'), 'receipt')
    control, spec = _control(doc)
    prior = _validated(doc)
    if prior and any(row['status'] == 'RUNNING' for row in prior['attempts']):
        _error('RUNNING', 'Finish or recover running attempts before refreshing the work plan')
    state = copy.deepcopy(prior) if prior else {
        'version': VERSION, 'episode': {'id': str(uuid.uuid4()), 'started_at': _now(),
                                      'parent_episode_id': None},
        'attempts': [], 'selection_history': []}
    state['selected'] = profile
    state['recommendation'] = recommend(assessment if assessment is not None
                                        else prior['assessment'] if prior else {})
    state['assessment'] = state['recommendation']['assessment']
    state['capabilities'] = _capabilities(capabilities if capabilities is not None
                                        else prior['capabilities'] if prior else None)
    state['capacity'] = _capacity(capacity if capacity is not None
                                 else prior['capacity'] if prior else None, spec)
    limits, usage = _limits(state), _usage(state)
    if any(usage[key] > limits[key] for key in ('preparation_attempts', 'review_attempts', 'total_attempts')):
        _error('BUDGET', 'Selected profile cannot erase or reduce already spent attempt history',
               limits=limits, usage=usage)
    state['selection_history'].append({'profile': profile, 'selected_at': _now(),
                                       'receipt': copy.deepcopy(receipt)})
    _seal(state)
    control['work_profile'] = state
    return status(doc)


def status(doc):
    """Read-only state/limit inspection; it never upgrades unknown capability."""
    control, spec = _control(doc)
    state = _validated(doc)
    required = control.get('work_profile_required', False)
    if state is None:
        return {'required': required, 'managed': False, 'selected': None,
                'readiness': 'PENDING' if required else 'LEGACY_EXEMPT',
                'issues': ['SELECTION_REQUIRED'] if required else [],
                'provider_execution': 'NOT_RUN'}
    issues = []
    capacity = state['capacity']
    if capacity['status'] != 'PASS':
        issues.append('CAPACITY_' + capacity['status'])
    if capacity.get('spec_sha256') != b.digest(b.canonical(spec)):
        issues.append('SPEC_NEEDS_REFRESH')
    if capacity.get('checker_sha256') != _checker_sha():
        issues.append('CHECKER_NEEDS_REFRESH')
    if state['recommendation']['unknown_factors']:
        issues.append('ASSESSMENT_PENDING')
    if state['assessment']['preparation_blockers']:
        issues.append('BLOCKED_PREPARATION')
    if state['capabilities'].get('child_limit') is None:
        issues.append('HOST_CHILD_LIMIT_PENDING')
    if state['capabilities'].get('reader_isolation') is not True:
        issues.append('READER_ISOLATION_UNAVAILABLE')
    needs_vision = bool(spec.get('media') or spec.get('ui_callouts'))
    if needs_vision and state['capabilities'].get('vision') is not True:
        issues.append('VISION_UNAVAILABLE')
    latest = {}
    for row in state['attempts']:
        latest[row['task_id']] = row
    incomplete = [row['attempt_id'] for row in latest.values() if row['status'] != 'PASS']
    return {'required': required, 'managed': True, 'selected': state['selected'],
            'recommendation': copy.deepcopy(state['recommendation']),
            'episode_id': state['episode']['id'], 'capacity_status': capacity['status'],
            'readiness': 'PENDING' if issues else 'PASS', 'needs_vision': needs_vision,
            'limits': _limits(state), 'usage': _usage(state), 'issues': issues,
            'active_attempts': [copy.deepcopy(row) for row in state['attempts'] if row['status'] == 'RUNNING'],
            'unresolved_attempts': incomplete,
            'execution_evidence': 'RECORDED_NOT_PROVIDER_AUTHENTICATED',
            'model_suggestion': _model_suggestion(state),
            'model_application': 'RECOMMENDATION_ONLY'}


def admit(doc, operation):
    """Fail closed at the requested phase; discovery/write can close unknowns."""
    if operation not in OPERATIONS:
        _error('OPERATION', 'Use prepare, write, review or release admission')
    report = status(doc)
    if not report['managed']:
        if report['required']:
            _error('SELECTION_REQUIRED', 'This workspace requires explicit profile selection')
        return report
    ignored = set()
    if operation in ('prepare', 'write'):
        ignored.update({'ASSESSMENT_PENDING', 'BLOCKED_PREPARATION', 'READER_ISOLATION_UNAVAILABLE',
                        'VISION_UNAVAILABLE', 'SPEC_NEEDS_REFRESH', 'CHECKER_NEEDS_REFRESH'})
    if operation == 'write':
        # A selected draft can be authored to close the missing inputs that
        # prevent measured capacity. This does not authorize any child dispatch.
        ignored.update({'HOST_CHILD_LIMIT_PENDING', 'CAPACITY_PENDING', 'CAPACITY_BLOCKED'})
    blocked = [issue for issue in report['issues'] if issue not in ignored]
    if blocked:
        _error('ADMISSION', 'Work profile admission is blocked', operation=operation, issues=blocked)
    if operation == 'write' and any(row['role'] == 'reviewer' for row in report['active_attempts']):
        _error('READER_RUNNING', 'Do not modify specification while independent readers are running')
    return report


def _commit(doc, state):
    _seal(state)
    doc['delivery']['control']['work_profile'] = state


def begin(doc, task_id, role, input_sha256, context_id=None, diagnosis=None):
    """Charge exactly one actual dispatch before launch, within all hard quotas."""
    if role not in ('prep', 'reviewer'):
        _error('ROLE', 'Only bounded prep and leaf reviewer tasks may be dispatched')
    _text(task_id, 'task_id')
    _sha(input_sha256, 'input_sha256')
    if diagnosis is not None:
        _text(diagnosis, 'diagnosis')
    report = admit(doc, 'review' if role == 'reviewer' else 'prepare')
    if not report['managed']:
        _error('SELECTION_REQUIRED', 'Opt in explicitly before using managed dispatch accounting')
    state = copy.deepcopy(_validated(doc))
    limits, usage = _limits(state), _usage(state)
    role_budget = 'review_attempts' if role == 'reviewer' else 'preparation_attempts'
    if usage[role_budget] >= limits[role_budget] or usage['total_attempts'] >= limits['total_attempts']:
        _error('BUDGET', 'Episode dispatch budget is exhausted; quality gates cannot be reduced',
               role=role, limits=limits, usage=usage)
    if usage['running_children'] >= limits['concurrent_children']:
        _error('CONCURRENCY', 'Wait for a child to finish before another dispatch', limits=limits, usage=usage)
    if any(row['task_id'] == task_id and row['status'] == 'RUNNING' for row in state['attempts']):
        _error('TASK_RUNNING', 'This logical task already has a running attempt')
    history = [row for row in state['attempts'] if row['task_id'] == task_id]
    if len(history) >= 2 and all(row['status'] in ('FAIL', 'UNKNOWN') for row in history[-2:]):
        if diagnosis is None:
            _error('DIAGNOSIS_REQUIRED', 'Two failed executions of the same task require a recorded diagnosis before another attempt',
                   task_id=task_id, prior_attempt_ids=[row['attempt_id'] for row in history[-2:]])
    if role == 'reviewer':
        _text(context_id, 'context_id')
        if any(row.get('context_id') == context_id for row in state['attempts'] if row['role'] == 'reviewer'):
            _error('ISOLATION', 'A fresh reader context is required for every attempt, including retries')
    elif context_id is not None:
        _text(context_id, 'context_id')
    row = {'task_id': task_id, 'attempt_id': str(uuid.uuid4()), 'role': role,
           'input_sha256': input_sha256, 'context_id': context_id, 'status': 'RUNNING',
           'started_at': _now(), 'spec_sha256': state['capacity']['spec_sha256'],
           'checker_sha256': state['capacity']['checker_sha256']}
    if diagnosis is not None:
        row['diagnosis'] = diagnosis
    state['attempts'].append(row)
    _commit(doc, state)
    return copy.deepcopy(row)


def _attempt(state, task_id, attempt_id):
    rows = [row for row in state['attempts'] if row['task_id'] == task_id
            and (attempt_id is None or row['attempt_id'] == attempt_id)]
    if not rows:
        _error('TASK_UNKNOWN', 'No issued attempt matches this task/attempt identity', task_id=task_id)
    if len(rows) != 1:
        _error('ATTEMPT_REQUIRED', 'Supply attempt_id when a logical task has been retried', task_id=task_id)
    return rows[0]


def finish(doc, task_id, outcome, input_sha256=None, context_id=None, evidence=None, attempt_id=None):
    """Record a bound outcome idempotently; all dispatches remain charged."""
    _text(task_id, 'task_id')
    if attempt_id is not None:
        _text(attempt_id, 'attempt_id')
    if not isinstance(outcome, str):
        _error('OUTCOME', 'Completion outcome must be a string')
    aliases = {'COMPLETED': 'PASS', 'FAILED': 'FAIL', 'CANCELED': 'CANCELLED'}
    outcome = aliases.get(outcome, outcome)
    if outcome not in TERMINAL:
        _error('OUTCOME', 'Use PASS/COMPLETED, FAIL/FAILED, CANCELLED or UNKNOWN')
    state = copy.deepcopy(_validated(doc))
    if state is None:
        _error('SELECTION_REQUIRED', 'No managed episode exists')
    row = _attempt(state, task_id, attempt_id)
    if input_sha256 is None or input_sha256 != row['input_sha256']:
        _error('INPUT_BINDING', 'Completion must bind the exact dispatched input SHA-256')
    if context_id != row['context_id']:
        _error('CONTEXT_BINDING', 'Completion reader context differs from the dispatched context')
    if evidence is not None and not isinstance(evidence, dict):
        _error('EVIDENCE', 'Completion evidence must be an object')
    evidence = copy.deepcopy(evidence or {})
    if outcome == 'PASS':
        _sha(evidence.get('response_sha256'), 'evidence.response_sha256')
        _text(evidence.get('receipt'), 'evidence.receipt')
    for field in ('input_sha256', 'context_id'):
        if field in evidence and evidence[field] != row[field]:
            _error('EVIDENCE_BINDING', 'Evidence binding differs from the issued attempt', field=field)
    completion = {'status': outcome, 'input_sha256': input_sha256, 'context_id': context_id,
                  'evidence': evidence}
    completion_hash = b.digest(b.canonical(completion))
    if row['status'] != 'RUNNING':
        if row.get('completion_sha256') == completion_hash:
            return copy.deepcopy(row)
        _error('TERMINAL', 'A terminal attempt cannot be replaced by a different outcome')
    row.update(status=outcome, evidence=evidence, completion_sha256=completion_hash, finished_at=_now())
    _commit(doc, state)
    return copy.deepcopy(row)


def cancel(doc, task_id, reason='Cancelled by caller', attempt_id=None):
    """Cancellation records cost and never refunds an attempt."""
    state = _validated(doc)
    if state is None:
        _error('SELECTION_REQUIRED', 'No managed episode exists')
    row = _attempt(state, task_id, attempt_id)
    return finish(doc, task_id, 'CANCELLED', row['input_sha256'], row['context_id'],
                  {'reason': _text(reason, 'reason')}, attempt_id=row['attempt_id'])


def recover(doc, task_id, reason='Execution interrupted; outcome unknown', attempt_id=None):
    """Crash recovery preserves UNKNOWN, charged quota, and immutable bindings."""
    state = _validated(doc)
    if state is None:
        _error('SELECTION_REQUIRED', 'No managed episode exists')
    row = _attempt(state, task_id, attempt_id)
    return finish(doc, task_id, 'UNKNOWN', row['input_sha256'], row['context_id'],
                  {'reason': _text(reason, 'reason')}, attempt_id=row['attempt_id'])


def assert_release(doc):
    """Additional managed admission; callers must still run every A-F core gate."""
    report = admit(doc, 'release')
    if not report['managed']:
        return report
    state = _validated(doc)
    if report['active_attempts'] or report['unresolved_attempts']:
        _error('INCOMPLETE', 'Running or unresolved task attempts prevent release',
               attempt_ids=report['unresolved_attempts'])
    latest = {}
    for row in state['attempts']:
        latest[row['task_id']] = row
    spec_sha = state['capacity']['spec_sha256']
    checker_sha = state['capacity']['checker_sha256']
    for row in latest.values():
        if row['role'] != 'reviewer':
            continue
        if row['spec_sha256'] != spec_sha or row['checker_sha256'] != checker_sha:
            # Earlier completed snapshots remain cost history. The caller's A-F
            # gate must bind every currently accepted reader to its current task.
            continue
        evidence = row.get('evidence', {})
        _sha(evidence.get('response_sha256'), 'evidence.response_sha256')
        _text(evidence.get('receipt'), 'evidence.receipt')
    return report
