# SPDX-License-Identifier: GPL-3.0-only
"""Private review evidence; no provider authentication or automatic approval."""
import copy
import re
import bv2 as b


def response_payload(reader):
    """Hash the actual parsed answer, excluding controller-supplied attestations."""
    return {key: value for key, value in reader.items()
            if key not in {'response_sha256', 'execution_evidence'}}


def response_sha(reader):
    return b.digest(b.canonical(response_payload(reader)))


def shape_errors(reader, pointer):
    import delivery as d
    errors = []
    if not isinstance(reader, dict):
        return [d.issue('F2_RESPONSE_SHAPE', pointer, 'Reader reply must be an object')]
    for key in ('isolated', 'saw_other_results', 'plan_completed'):
        if type(reader.get(key)) is not bool:
            errors.append(d.issue('F2_RESPONSE_SHAPE', pointer + '/' + key, 'Use a JSON boolean'))
    for key in ('reader_id', 'context_id', 'request_sha256', 'status', 'execution_evidence', 'response_sha256'):
        if not isinstance(reader.get(key), str):
            errors.append(d.issue('F2_RESPONSE_SHAPE', pointer + '/' + key, 'Use a string'))
    for key in ('questions', 'visual_matches', 'plan_decisions'):
        rows = reader.get(key)
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            errors.append(d.issue('F2_RESPONSE_SHAPE', pointer + '/' + key, 'Use an array of objects'))
    if not isinstance(reader.get('expected_results'), dict):
        errors.append(d.issue('F2_RESPONSE_SHAPE', pointer + '/expected_results', 'Use a result object'))
    if not isinstance(reader.get('covered_requirements'), list) or any(not isinstance(value, str) for value in reader.get('covered_requirements', [])):
        errors.append(d.issue('F2_RESPONSE_SHAPE', pointer + '/covered_requirements', 'Use an array of IDs'))
    if not isinstance(reader.get('findings'), list) or any(not isinstance(value, str) for value in reader.get('findings', [])):
        errors.append(d.issue('F2_RESPONSE_SHAPE', pointer + '/findings', 'Use an array of findings'))
    for key, fields in [('questions', ('question',)), ('plan_decisions', ('decision',)),
                        ('visual_matches', ('media_ref', 'ui_element_ref', 'method'))]:
        for row in reader.get(key, []) if isinstance(reader.get(key), list) else []:
            if isinstance(row, dict) and any(not isinstance(row.get(field), str) for field in fields):
                errors.append(d.issue('F2_RESPONSE_SHAPE', pointer + '/' + key, 'Use string evidence fields'))
            if isinstance(row, dict) and key in ('questions', 'plan_decisions') and row.get('pointer') is not None and not isinstance(row.get('pointer'), str):
                errors.append(d.issue('F2_RESPONSE_SHAPE', pointer + '/' + key, 'Pointer must be a string or an explicit missing value'))
    for row in reader.get('visual_matches', []) if isinstance(reader.get('visual_matches'), list) else []:
        if isinstance(row, dict) and any(type(row.get(key)) is not bool for key in ('label_match', 'layout_match')):
            errors.append(d.issue('F2_RESPONSE_SHAPE', pointer + '/visual_matches', 'Visual agreement uses JSON booleans'))
    return errors


def findings(spec, reader, pointer):
    import delivery as d
    errors = []
    covered = set()
    for question in reader.get('questions', []):
        ref = question.get('requirement_ref')
        match = re.fullmatch(r'/requirements/(0|[1-9][0-9]*)/statement',
                             question.get('pointer') or '')
        if match and int(match[1]) < len(spec['requirements']):
            row = spec['requirements'][int(match[1])]
            if ref == row['id'] and question.get('question', '').strip():
                covered.add(ref)
    if covered != {row['id'] for row in spec['requirements']}:
        errors.append(d.issue('F2_FUNCTIONAL_COVERAGE', pointer,
                              'Each requirement needs its own functional question and statement pointer'))
    if reader.get('response_sha256') != response_sha(reader):
        errors.append(d.issue('F2_RESPONSE_HASH', pointer,
                              'Response hash must bind to the actual parsed answer'))
    if reader.get('plan_completed') is True:
        plans = reader.get('plan_decisions', [])
        if not plans:
            errors.append(d.issue('F5_PLAN_EVIDENCE', pointer, 'Completed plan needs concrete decisions'))
        required = {'objects'}
        if spec.get('architecture', {}).get('constraints'):
            required.add('architecture')
        if spec.get('dependencies'):
            required.add('dependencies')
        if any(row['status'] == 'OPEN' for row in spec.get('developer_decisions', [])):
            required.add('developer_decisions')
        observed = set()
        for plan in plans:
            path = plan.get('pointer') or ''
            if plan.get('decision', '').strip() and path.startswith('/'):
                observed.add(path.split('/')[1])
        if not required <= observed:
            errors.append(d.issue('F5_PLAN_COVERAGE', pointer,
                                  'Plan must cover objects, constraints, dependencies and delegated decisions that exist'))
    return errors


def review_spec(spec, scenario_reader):
    value = copy.deepcopy(spec)
    if scenario_reader:
        for case in value['test_cases']:
            case.pop('expected', None)
    return value
