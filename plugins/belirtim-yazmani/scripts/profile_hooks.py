# SPDX-License-Identifier: GPL-3.0-only
"""Scoped native command-hook adapters; core admission remains authoritative.

Hooks never approve a permission, edit a workspace, or authenticate a reader.
The native dispatch callback atomically claims its already charged reservation
only in the selected external coordinator file; other callbacks are read-only.
Only direct calls to this package's bv2.py and declared BYW leaf dispatches are
controlled. Shell wrappers, hosted/cloud interception, and native hook trust
are deliberately not claimed as supported execution evidence.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'scripts' / 'bv2.py'
MAX_INPUT = 1024 * 1024
EVENTS = {'SessionStart', 'PreToolUse', 'PostToolUse', 'SubagentStop',
          'PreCompact', 'PostCompact', 'Stop'}
LEAVES = {'byw-reader-a': 'review', 'byw-reader-b': 'review',
          'byw-reader-c': 'review', 'byw-preparation': 'prepare'}
OPERATIONS = {'patch': 'write', 'eval-request': 'review', 'handoff': 'release',
              'handoff-batch': 'release'}
SHELL_TOOLS = {'Bash', 'PowerShell', 'exec_command'}
AGENT_TOOLS = {'Agent', 'spawn_agent'}


class HookInvalid(ValueError):
    pass


def strict_json(raw):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise HookInvalid('Duplicate event JSON key')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              HookInvalid('Non-finite event JSON number')))
    except (json.JSONDecodeError, UnicodeError) as error:
        raise HookInvalid('Malformed native event JSON') from error


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def tokens(command):
    """Parse the documented direct argv subset without executing shell text.

    Backslashes remain path characters on Windows. Separators, substitutions,
    redirections, multiline commands and unclosed quotes are unsupported.
    """
    if not isinstance(command, str) or not command or len(command) > MAX_INPUT:
        raise HookInvalid('A bounded direct command string is required')
    parts, current, quote = [], [], None
    for char in command.strip():
        if quote:
            if char == quote:
                quote = None
            else:
                current.append(char)
        elif char in "'\"":
            quote = char
        elif char.isspace():
            if char in '\n\r':
                raise HookInvalid('Use one direct BYW command')
            if current:
                parts.append(''.join(current)); current = []
        elif char in ';|<>`' or char == '$':
            raise HookInvalid('Shell chaining or substitution is unsupported')
        else:
            current.append(char)
    if quote:
        raise HookInvalid('Unclosed command quote')
    if current:
        parts.append(''.join(current))
    if parts and parts[0] == '&':
        parts = parts[1:]
    if any(value in ('&', '&&') for value in parts):
        raise HookInvalid('Use one direct BYW command')
    return parts


def path(raw, cwd, must_exist=True):
    if not isinstance(raw, str) or not raw or '\x00' in raw:
        raise HookInvalid('Explicit workspace path is required')
    value = Path(raw)
    if not value.is_absolute():
        value = cwd / value
    # Refuse aliasing through links/junctions before canonical resolution.
    for part in (value, *value.parents):
        if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
            raise HookInvalid('Workspace path must not traverse links or junctions')
    value = value.resolve(strict=must_exist)
    if must_exist and not value.is_file():
        raise HookInvalid('Workspace must be an existing file')
    return value


def cwd_from(event):
    raw = event.get('cwd')
    if not isinstance(raw, str) or not Path(raw).is_absolute():
        raise HookInvalid('Native event cwd must be absolute')
    value = Path(raw).resolve(strict=True)
    if not value.is_dir():
        raise HookInvalid('Native event cwd is not a directory')
    return value


def declared_workspace(event, environ):
    # No transcript scanning or assistant-supplied arbitrary event field can
    # silently select a workspace. The run environment binds this opt-in.
    raw = environ.get('BYW_WORKSPACE')
    return path(raw, cwd_from(event)) if raw else None


def command_scope(event):
    if event.get('tool_name') not in SHELL_TOOLS:
        return None
    value = event.get('tool_input')
    if not isinstance(value, dict):
        return None
    command = value.get('command', value.get('cmd'))
    if not isinstance(command, str):
        return None
    # Probe only the command prefix before parsing shell tails. An unrelated
    # Python script with shell syntax must not become a BYW denial.
    if 'bv2.py' not in command:
        return None
    token_pattern = re.compile(r'''\s*(?:'([^']*)'|"([^"]*)"|([^\s]+))''')
    prefix = []
    cursor = 0
    while len(prefix) < 32:
        match = token_pattern.match(command, cursor)
        if not match:
            break
        prefix.append(next(value for value in match.groups() if value is not None))
        cursor = match.end()
    if prefix and prefix[0] == '&':
        prefix = prefix[1:]
    offset = 1
    if not prefix or not re.fullmatch(r'(?i)(?:python(?:\d+(?:\.\d+)?)?|python\.exe|py|py\.exe)',
                                    prefix[0].replace('\\', '/').rsplit('/', 1)[-1]):
        return None
    while offset < len(prefix):
        if prefix[offset] in ('-3', '-B', '-I', '-Xutf8'):
            offset += 1
        elif prefix[offset] == '-X' and offset + 1 < len(prefix) and prefix[offset + 1] == 'utf8':
            offset += 2
        else:
            break
    if len(prefix) <= offset:
        return None
    try:
        cwd = cwd_from(event)
        candidate = path(prefix[offset], cwd, must_exist=False)
    except (HookInvalid, OSError, ValueError):
        # Invalid native cwd or a foreign linked script cannot expand this
        # plugin's hook jurisdiction. A literal package path stays fail-closed.
        if prefix[offset].replace('\\', '/').lower() == str(SCRIPT).replace('\\', '/').lower():
            raise
        return None
    if candidate != SCRIPT.resolve():
        return None
    parts = tokens(command)
    argv = parts[offset + 1:]
    if not argv:
        raise HookInvalid('BYW operation is missing')
    action = argv[0]
    operation = OPERATIONS.get(action)
    if action == 'work-begin':
        operation = {'prep': 'prepare', 'reviewer': 'review'}.get(option(argv, '--role'))
        if operation is None:
            raise HookInvalid('BYW task role must be prep or reviewer')
    elif action == 'work-admit':
        operation = option(argv, '--operation')
        if operation not in {'prepare', 'review', 'release', 'write'}:
            raise HookInvalid('Unknown BYW admission operation')
    if operation is None:
        return None
    if len(argv) < 2 or argv[1].startswith('-'):
        raise HookInvalid('BYW operation needs an explicit workspace argument')
    source = path(argv[1], cwd)
    return {'action': action, 'operation': operation, 'source': source,
            'argv': argv}


def option(argv, name):
    occurrences = [i for i, value in enumerate(argv) if value == name]
    inline = [value.split('=', 1)[1] for value in argv if value.startswith(name + '=')]
    if len(occurrences) + len(inline) != 1:
        return None
    if inline:
        return inline[0]
    index = occurrences[0]
    return argv[index + 1] if index + 1 < len(argv) else None


def load_workspace(source):
    import bv2
    return bv2.load(source)


def admit(doc, operation):
    import work_profiles
    if operation == 'release':
        return work_profiles.assert_release(doc)
    return work_profiles.admit(doc, operation)


def profile_status(doc):
    import work_profiles
    return work_profiles.status(doc)


def native_result(event):
    """Summarize reported result metadata without copying tool text/secrets."""
    result = event.get('tool_response')
    reported = set()
    known = {'PASS', 'FAIL', 'UNKNOWN', 'NOT_RUN', 'BLOCKED', 'CANCELLED',
             'COMPLETED', 'PENDING'}
    def visit(value, depth=0):
        if depth > 12:
            return
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {'status', 'outcome', 'readiness', 'decision'} and isinstance(child, str) and child in known:
                    reported.add(child)
                elif key in {'stdout', 'output'} and isinstance(child, str):
                    try:
                        visit(strict_json(child), depth + 1)
                    except HookInvalid:
                        pass
                elif isinstance(child, (dict, list)):
                    visit(child, depth + 1)
        elif isinstance(value, list):
            for child in value:
                visit(child, depth + 1)
    visit(result)
    code = result.get('exit_code', result.get('exitCode')) if isinstance(result, dict) else None
    if type(code) is not int:
        code = None
    return {'exit_code': code, 'reported_statuses': sorted(reported),
            'status': 'REPORTED_FAILURE' if code not in (None, 0) or 'FAIL' in reported
            else 'REPORTED_INCOMPLETE' if reported & {'UNKNOWN', 'NOT_RUN', 'BLOCKED', 'PENDING', 'CANCELLED'}
            else 'REPORTED_SUCCESS' if code == 0 else 'UNKNOWN',
            'completion_evidence': False}


def check_scope(scope, loader, admission):
    doc = loader(scope['source'])
    if scope['action'] == 'handoff-batch':
        if not isinstance(doc, dict) or set(doc) != {'developments'} or not isinstance(doc['developments'], list) or not doc['developments']:
            raise HookInvalid('Batch needs a nonempty developments manifest')
        base = scope['source'].parent
        statuses = []
        for row in doc['developments']:
            if not isinstance(row, dict) or set(row) != {'workspace', 'assets_root'}:
                raise HookInvalid('Batch entries need workspace and assets_root')
            raw = row['workspace']
            if not isinstance(raw, str) or Path(raw).is_absolute() or '..' in raw.replace('\\', '/').split('/'):
                raise HookInvalid('Batch workspace must stay within its manifest root')
            source = path(raw, base)
            if not source.is_relative_to(base):
                raise HookInvalid('Batch workspace escaped its manifest root')
            statuses.append(admission(loader(source), 'release'))
        return {'status': 'ADMISSION_CHECKED', 'developments': len(statuses)}
    return admission(doc, scope['operation'])


def deny(reason):
    reason = 'BYW admission denied: ' + str(reason)[:1200]
    return 2, {'hookSpecificOutput': {'hookEventName': 'PreToolUse',
               'permissionDecision': 'deny', 'permissionDecisionReason': reason}}, reason


def notice(event_name, message, data):
    summary = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    text = (message + ': ' + summary)[:3000]
    if event_name in {'PreToolUse', 'PostToolUse'}:
        return 0, {'hookSpecificOutput': {'hookEventName': event_name,
                                         'additionalContext': text}}, ''
    return 0, {'systemMessage': text}, ''


def agent_scope(event, environ):
    if event.get('tool_name') not in AGENT_TOOLS:
        return None
    value = event.get('tool_input')
    if not isinstance(value, dict):
        return None
    name = value.get('subagent_type', value.get('agent_type', value.get('name', '')))
    if not isinstance(name, str):
        return None
    leaf = name.removeprefix('belirtim-yazmani:')
    if leaf not in LEAVES:
        return None
    source = declared_workspace(event, environ)
    if source is None:
        raise HookInvalid('BYW leaf dispatch requires explicit BYW_WORKSPACE')
    raw = value.get('prompt', value.get('message'))
    packet = strict_json(raw) if isinstance(raw, str) else None
    task = packet.get('byw_task') if isinstance(packet, dict) else None
    if not isinstance(task, dict) or any(not isinstance(task.get(key), str) or not task[key] for key in
                                       ('task_id', 'attempt_id', 'context_id', 'input_sha256')):
        raise HookInvalid('BYW leaf dispatch requires the issued structured task identity')
    return {'source': source, 'operation': LEAVES[leaf], 'task': task,
            'leaf': leaf, 'action': 'agent', 'argv': []}


def check_dispatch(doc, scope):
    control = doc.get('delivery', {}).get('control', {})
    state = control.get('work_profile')
    if not isinstance(state, dict):
        raise HookInvalid('BYW leaf dispatch needs a selected work profile')
    if not state.get('capabilities', {}).get('coordinator_file'):
        raise HookInvalid('Native BYW leaf dispatch requires its explicit shared coordinator file')
    coordinator_raw = state['capabilities']['coordinator_file']
    if not isinstance(coordinator_raw, str) or not Path(coordinator_raw).is_absolute():
        raise HookInvalid('Native BYW coordinator must be an explicit absolute path')
    coordinator = path(coordinator_raw, scope['source'].parent)
    if coordinator == scope['source'] or coordinator.is_relative_to(ROOT) or coordinator.suffix != '.json':
        raise HookInvalid('Native BYW coordinator must be a separate JSON file outside the plugin')
    rows = state.get('attempts', [])
    task = scope['task']
    matches = [row for row in rows if isinstance(row, dict)
               and row.get('task_id') == task['task_id']
               and row.get('attempt_id') == task['attempt_id']]
    if len(matches) != 1 or matches[0].get('status') != 'RUNNING':
        raise HookInvalid('BYW leaf dispatch must bind one issued RUNNING attempt')
    row = matches[0]
    if row.get('context_id') != task['context_id'] or row.get('input_sha256') != task['input_sha256']:
        raise HookInvalid('BYW leaf dispatch task identity/hash differs from the issued attempt')
    if row.get('role') != ('reviewer' if scope['operation'] == 'review' else 'prep'):
        raise HookInvalid('BYW leaf role differs from the issued attempt')
    capacity = state.get('capacity', {})
    if any(row.get(key) != capacity.get(key) for key in ('spec_sha256', 'checker_sha256')):
        raise HookInvalid('BYW leaf dispatch belongs to a stale specification/checker')
    import dispatch_registry
    dispatch_registry.assert_reserved(doc, scope['source'], row)
    return row


def handle(event, host, event_name, environ=None, loader=load_workspace,
           admission=admit, status=profile_status):
    if host not in {'claude', 'codex'} or event_name not in EVENTS:
        raise HookInvalid('Unsupported adapter host or event')
    if not isinstance(event, dict) or event.get('hook_event_name') != event_name:
        raise HookInvalid('Native event name must match the configured callback')
    environ = os.environ if environ is None else environ
    if event_name in {'PreToolUse', 'PostToolUse'}:
        try:
            scope = command_scope(event)
            if scope is None:
                scope = agent_scope(event, environ)
            if scope is None:
                return 0, {}, ''
            if event_name == 'PreToolUse':
                if scope['action'] == 'agent':
                    doc = loader(scope['source'])
                    # Admission is read-only; begin already reserves quota.
                    admission(doc, scope['operation'])
                    row = check_dispatch(doc, scope)
                    tool_use_id = event.get('tool_use_id')
                    if not isinstance(tool_use_id, str) or not tool_use_id.strip() or len(tool_use_id) > 256:
                        raise HookInvalid('Native BYW dispatch requires a bounded tool_use_id')
                    import dispatch_registry
                    dispatch_registry.claim_native_dispatch(doc, scope['source'], row, host, tool_use_id)
                else:
                    check_scope(scope, loader, admission)
                # Silence declines to decide; it never expands permissions.
                return 0, {}, ''
            doc = loader(scope['source'])
            snapshot = digest(doc.get('delivery', {}).get('spec', doc))
            data = {'status': 'OBSERVED', 'snapshot_sha256': snapshot,
                    'action': scope['action'], 'receipt_evidence': 'NOT_AUTHENTICATED',
                    'actual_host_result': native_result(event),
                    'idempotency_key': digest({'session': event.get('session_id'),
                        'tool': event.get('tool_use_id'), 'action': scope['action'],
                        'snapshot': snapshot}), 'core': status(doc)}
            return notice(event_name, 'BYW read-only observation', data)
        except Exception as error:
            if event_name == 'PreToolUse':
                return deny(error)
            return notice(event_name, 'BYW observation failed; core gate remains required',
                          {'status': 'UNKNOWN', 'reason': str(error)[:1200]})
    source = declared_workspace(event, environ)
    if source is None:
        return 0, {}, ''
    try:
        doc = loader(source)
        data = {'event': event_name, 'host': host, 'core': status(doc),
                'reader_receipt': 'NOT_AUTHENTICATED', 'workspace_modified': False,
                'native_execution': 'NOT_VERIFIED'}
        if event_name == 'Stop':
            # No continuation is issued: zero retry loops, including when
            # stop_hook_active is true. Explicit core release is the gate.
            data.update(continuation=False, final_release='NOT_RUN',
                        stop_hook_active=event.get('stop_hook_active') is True)
        if event_name == 'SubagentStop':
            data['result_status'] = 'UNVERIFIED_NATIVE_STOP'
        return notice(event_name, 'BYW checkpoint; retain explicit core admission', data)
    except Exception as error:
        return notice(event_name, 'BYW checkpoint unavailable',
                      {'status': 'UNKNOWN', 'reason': str(error)[:1200],
                       'continuation': False, 'final_release': 'NOT_RUN'})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True, choices=['claude', 'codex'])
    parser.add_argument('--event', required=True, choices=sorted(EVENTS))
    args = parser.parse_args(argv)
    raw = sys.stdin.buffer.read(MAX_INPUT + 1)
    try:
        if len(raw) > MAX_INPUT:
            raise HookInvalid('Native event exceeds 1 MiB')
        event = strict_json(raw.decode('utf-8-sig'))
        code, output, reason = handle(event, args.host, args.event)
    except Exception as error:
        # Fail closed only when the damaged payload still identifies this
        # package/leaf scope. Unrelated malformed events get no decision.
        probe = raw.decode('utf-8', errors='replace').replace('\\\\', '\\').replace('\\', '/').lower()
        scoped = str(SCRIPT).replace('\\', '/').lower() in probe or any(
            re.search(r'\b' + re.escape(name) + r'\b', probe) for name in LEAVES)
        if args.event == 'PreToolUse' and scoped:
            code, output, reason = deny(error)
        elif args.event == 'PreToolUse':
            code, output, reason = 0, {}, ''
        else:
            code, output, reason = notice(args.event, 'BYW native event invalid',
                {'status': 'UNKNOWN', 'reason': str(error)[:1200], 'continuation': False})
    if output:
        print(json.dumps(output, ensure_ascii=True, separators=(',', ':')))
    if reason:
        print(reason, file=sys.stderr)
    return code


if __name__ == '__main__':
    sys.exit(main())
