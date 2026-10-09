# SPDX-License-Identifier: GPL-3.0-only
"""Private work-profile CLI contracts and physical snapshot binding."""
import copy
import json
import math
from pathlib import Path

import bv2 as b


def add_parsers(sub):
    sub.add_parser('work-profiles').add_argument('catalog',nargs='?',choices=['catalog'],default='catalog')
    for name in ('work-recommend', 'work-select', 'work-status', 'work-begin', 'work-finish', 'work-admit'):
        parser = sub.add_parser(name)
        parser.add_argument('source')
        parser.add_argument('--assets-root')
        if name in ('work-recommend', 'work-select'):
            parser.add_argument('--assessment', required=True)
        if name == 'work-select':
            parser.add_argument('--profile', required=True, choices=['lite', 'plus', 'pro', 'max', 'ultra'])
            parser.add_argument('--capabilities', required=True)
            parser.add_argument('--capacity', required=True)
            parser.add_argument('--receipt', required=True)
            parser.add_argument('--confirmed', action='store_true', required=True)
            parser.add_argument('--coordinator')
        if name == 'work-begin':
            parser.add_argument('--task-id', required=True)
            parser.add_argument('--role', required=True, choices=['prep', 'reviewer'])
            parser.add_argument('--input-sha256', required=True)
            parser.add_argument('--context-id',required=True)
            parser.add_argument('--diagnosis')
        if name == 'work-finish':
            parser.add_argument('--task-id', required=True)
            parser.add_argument('--attempt-id')
            parser.add_argument('--status', required=True, choices=['COMPLETED', 'FAIL', 'UNKNOWN', 'CANCELLED'])
            parser.add_argument('--response-sha256')
            parser.add_argument('--receipt', required=True)
            parser.add_argument('--input-sha256',required=True)
            parser.add_argument('--context-id',required=True)
        if name == 'work-admit':
            parser.add_argument('--operation', required=True, choices=['prepare', 'review', 'release', 'write'])


def read_json(path):
    path = Path(path)
    if path.stat().st_size > 1024 * 1024:
        raise b.Invalid('Private profile input exceeds 1 MiB')
    value = b.strict_json(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise b.Invalid('Private profile input must be an object')
    return value


def snapshot(doc, assets_root):
    import handoff3 as h
    import preflight
    units = h.fingerprints(doc, assets_root)
    return {'input_sha256': b.digest(b.canonical(units)),
            'checker_sha256': preflight.checker_hash()}


def volume(doc):
    spec,control=__import__('delivery').get_state(doc)
    paths={row['path'] for row in control.get('assets',[])} | {row['path'] for row in spec['media']}
    return {'requirements':len(spec['requirements']),'objects':len(spec['objects']),
            'assets':len(paths)+len(control.get('dependency_contracts',[]))}


def packet_byte_bound(doc,assets_root):
    import delivery as d
    import preflight
    import handoff3 as h
    files,sources=preflight.asset_snapshot(doc,assets_root)
    spec,control=d.get_state(doc)
    import source_pool
    references,pool=source_pool.collect(spec.get('references',[]),files)
    prepared={'assets':[{'path':name,'source_path':source,'sha256':b.digest(files[name])}
                         for name,source in sources.items()],
              'references':references,'source_pool':pool, 'dependency_contracts':list(h.dependency_records(doc).values()),
              'input_sha256':'0'*64}
    probe=copy.deepcopy(doc)
    # Force the same scheduling envelope that selection will add to final packets.
    probe['delivery']['control'].setdefault('work_profile',{})
    packets=d._issue_review_packets(probe,len(control.get('eval_rounds',[]))+1,prepared)
    return max(len(b.canonical(packet)) for packet in packets)


def bind_inputs(doc, assessment, capability, capacity, assets_root):
    import delivery as d
    spec, _ = d.get_state(doc)
    assessment = copy.deepcopy(assessment)
    # Total development volume, never the volume of one preparation chunk.
    assessment['counts'] = volume(doc)
    capability = copy.deepcopy(capability)
    capability['needs_vision'] = bool(spec['media'] or spec['ui_callouts'])
    capacity = copy.deepcopy(capacity)
    binding = snapshot(doc, assets_root)
    if capacity.get('status') == 'PASS':
        keys = ('context_limit', 'packet_tokens', 'output_reserve')
        if any(type(capacity.get(key)) is not int or capacity[key] <= 0 for key in keys):
            raise b.Invalid('Capacity PASS needs positive context_limit, packet_tokens and output_reserve')
        if not isinstance(capacity.get('evidence'), str) or not capacity['evidence'].strip():
            raise b.Invalid('Capacity PASS needs a scoped measurement or conservative estimate reference')
        # UTF-8 byte length is a deliberately conservative text-only token bound.
        # Vision token cost must be supplied separately; never infer it from PNG bytes.
        text_bytes = packet_byte_bound(doc,assets_root)
        if capability['needs_vision']:
            image = capacity.get('image_tokens')
            if type(image) is not int or image <= 0:
                raise b.Invalid('Vision capacity needs independently estimated image_tokens')
        else:
            image = 0
        if capacity['packet_tokens'] < text_bytes + image:
            raise b.Invalid('Capacity packet_tokens is below the conservative complete-packet bound')
        reserve_minimum = len(b.canonical(spec['requirements'])) + len(b.canonical(spec['test_cases'])) + 500
        if capacity['output_reserve'] < reserve_minimum:
            raise b.Invalid('Capacity output reserve cannot cover complete requirement/scenario responses')
        if capacity['packet_tokens'] + capacity['output_reserve'] > math.floor(capacity['context_limit'] * 0.8):
            capacity['status'] = 'BLOCKED'
            capacity['reason'] = 'Complete reader packet and output exceed context with 20 percent working margin'
        capacity['measurement_kind'] = 'ESTIMATED'
        capacity['text_byte_bound'] = text_bytes
    capacity.update(binding)
    capacity['spec_sha256'] = d.revision(spec)
    return assessment, capability, capacity


def managed(doc):
    control = doc.get('delivery', {}).get('control', {})
    return bool(control.get('work_profile_required') or 'work_profile' in control)


def physical_admit(doc, operation, assets_root):
    import work_profiles as w
    result = w.admit(doc, operation)
    if managed(doc) and operation in ('review', 'release'):
        control = doc['delivery']['control']['work_profile']
        stored = control.get('capacity', {})
        current = snapshot(doc, assets_root)
        if any(stored.get(key) != value for key, value in current.items()):
            raise b.Invalid('Work capacity input/checker snapshot changed; refresh the selected profile')
    return result


def run(args, doc):
    import work_profiles as w
    root = args.assets_root or Path(args.source).resolve().parent
    if args.cmd == 'work-recommend':
        assessment = read_json(args.assessment)
        assessment['counts'] = volume(doc)
        return w.recommend(assessment), False
    if args.cmd == 'work-select':
        assessment, capabilities, capacity = bind_inputs(doc, read_json(args.assessment),
            read_json(args.capabilities), read_json(args.capacity), root)
        capabilities['coordinator_file']=str(Path(args.coordinator).resolve() if args.coordinator
                                            else Path(args.source).resolve().parent/'.byw-dispatch.json')
        result = w.choose(doc, args.profile, assessment, capabilities, capacity,
                          {'confirmed': args.confirmed, 'receipt': args.receipt})
        import dispatch_registry
        dispatch_registry.register_selection(doc,args.source)
        return result, True
    if args.cmd == 'work-status':
        return w.status(doc), False
    if args.cmd == 'work-admit':
        return physical_admit(doc, args.operation, root), False
    if args.cmd == 'work-begin':
        if args.role=='prep' and args.task_id.startswith('review:'):
            raise b.Invalid('Preparation dispatch cannot use the reserved reviewer task namespace')
        physical_admit(doc, 'review' if args.role == 'reviewer' else 'prepare', root)
        if args.role == 'reviewer':
            requests = doc['delivery']['control'].get('eval_requests', [])
            matches = [row for row in requests if row['context_id'] == args.context_id
                       and row['request_sha256'] == args.input_sha256
                       and args.task_id == row.get('task_id','review:'+str(row['round'])+':'+row['reader_id'])]
            if len(matches) != 1:
                raise b.Invalid('Reviewer dispatch must match one issued context/request/task identity')
        result=w.begin(doc, args.task_id, args.role, args.input_sha256, args.context_id,diagnosis=args.diagnosis)
        import dispatch_registry
        dispatch_registry.reserve(doc,args.source,result)
        return result, True
    if args.cmd == 'work-finish':
        evidence = {'receipt': args.receipt, 'response_sha256': args.response_sha256}
        return w.finish(doc, args.task_id, args.status, args.input_sha256,
                        args.context_id, evidence, attempt_id=args.attempt_id), True
    raise b.Invalid('Unknown work-profile command')


def after_save(args,doc,result):
    if args.cmd=='work-finish':
        import dispatch_registry
        dispatch_registry.finish(doc,args.source,result)
