# SPDX-License-Identifier: GPL-3.0-only
"""Private review evidence; no provider authentication or automatic approval."""
import copy
import json
import re
from functools import lru_cache
import bv2 as b

SCENARIO_READERS = ('reader-1', 'reader-2')
READER_ROLES = {'reader-1': 'SCENARIO', 'reader-2': 'SCENARIO', 'reader-3': 'FULL_REVIEW'}
ORACLE_LABEL = re.compile(r'(?im)["\']?(?:expected(?:_results?)?|expected_results)["\']?\s*[:=]')


def valid_sha(value):
    return isinstance(value, str) and re.fullmatch('[a-f0-9]{64}', value) is not None


@lru_cache(maxsize=8)
def _case_pattern(identities):
    return re.compile(r'(?<![\w-])(?:' + '|'.join(re.escape(x) for x in identities) + r')(?![\w-])')


def assert_blind_content(value, case_ids, path='input'):
    """Reject explicit current-case oracles and peer replies; preserve source bytes."""
    if isinstance(value, dict):
        identities = [value.get(key) for key in ('id', 'test_case_id', 'case_id')]
        labels = {re.sub('[^a-z]', '', str(key).lower()): child for key, child in value.items()}
        if any(isinstance(identity, str) and identity in case_ids for identity in identities):
            if set(labels).intersection(('expected', 'expectedresult', 'expectedresults')):
                raise b.Invalid('BLOCKED: REVIEW_ORACLE_EXPOSURE at ' + path)
        if isinstance(labels.get('expectedresults'), dict) and case_ids.intersection(labels['expectedresults']):
            raise b.Invalid('BLOCKED: REVIEW_ORACLE_EXPOSURE peer/scenario results at ' + path)
        if {'reader_id', 'context_id', 'request_sha256'} <= set(value) or any(value.get(key) for key in ('eval_rounds', 'peer_verdicts', 'reader_results')):
            raise b.Invalid('BLOCKED: REVIEW_PEER_EXPOSURE at ' + path)
        for identity in case_ids.intersection(value):
            child=value[identity]
            if isinstance(child, dict) and any(re.sub('[^a-z]', '', key.lower()) in ('expected', 'expectedresult', 'expectedresults') for key in child):
                raise b.Invalid('BLOCKED: REVIEW_ORACLE_EXPOSURE case-keyed result at ' + path)
        for key, child in value.items():
            assert_blind_content(child, case_ids, path + '/' + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_blind_content(child, case_ids, path + '/' + str(index))
    elif isinstance(value, str):
        # Text sources can contain quoted JSON or TOON. Only explicit oracle labels
        # together with the current case identity are blocked, not business prose
        # saying that a functional outcome is expected.
        if value.lstrip().startswith(('{','[','"')):
            try:
                decoded=json.loads(value)
            except ValueError:
                decoded=value
            if decoded!=value:
                assert_blind_content(decoded,case_ids,path)
                return
        if case_ids and ORACLE_LABEL.search(value) and _case_pattern(tuple(sorted(case_ids))).search(value):
            raise b.Invalid('BLOCKED: REVIEW_ORACLE_EXPOSURE text at ' + path)
        if re.search(r'(?im)["\']?(?:eval_rounds|peer_verdicts|reader_results)["\']?\s*[:=]', value):
            raise b.Invalid('BLOCKED: REVIEW_PEER_EXPOSURE text at ' + path)


def blind_binding(spec, prepared):
    """Validate complete reader-visible sources once before issuing any packet."""
    case_ids = {row['id'] for row in spec['test_cases']}
    functional = review_spec(spec, True)
    assert_blind_content(functional, case_ids, 'spec')
    sources = prepared.get('source_pool', {'sources': []})
    assert_blind_content(sources, case_ids, 'source_pool')
    contracts = prepared.get('dependency_contracts', [])
    assert_blind_content(contracts, case_ids, 'dependency_contracts')
    for name, value in prepared.get('visible_text', {}).items():
        assert_blind_content(value, case_ids, 'asset/' + name)
    return b.digest(b.canonical({'functional': functional, 'source_pool': sources,
                                'contracts': contracts, 'assets': prepared.get('assets', [])}))


def assert_scenario_packet(packet):
    """Do not allow a self-declared SCENARIO packet to carry an exposed oracle."""
    if not isinstance(packet.get('reader_id'),str):
        raise b.Invalid('Reader identity must be a string')
    role = READER_ROLES.get(packet.get('reader_id'))
    if role is None or packet.get('review_role') != role or packet.get('scenario_reader') is not (role == 'SCENARIO'):
        raise b.Invalid('Reader role differs from issued identity')
    if not valid_sha(packet.get('blindness_sha256')):
        raise b.Invalid('Current packet needs its oracle-admission binding')
    if role == 'SCENARIO':
        case_ids = {row['id'] for row in packet['spec']['test_cases']}
        assert_blind_content(packet['spec'], case_ids, 'spec')
        assert_blind_content(packet.get('source_pool'), case_ids, 'source_pool')
        assert_blind_content(packet.get('dependency_contracts'), case_ids, 'dependency_contracts')


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
