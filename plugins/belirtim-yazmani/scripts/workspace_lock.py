# SPDX-License-Identifier: GPL-3.0-only
"""Single-writer CLI locks; do not remove another process's lock on timeout."""
import json
import os
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

import bv2 as b


@contextmanager
def held(source, timeout=5, require_file=True):
    raw=Path(source).absolute()
    if any(path.is_symlink() or getattr(path,'is_junction',lambda:False)() for path in (raw,*raw.parents)):
        raise b.Invalid('Workspace/coordinator lock path cannot traverse links or junctions')
    source = raw.resolve()
    if require_file and not source.is_file():
        raise b.Invalid('Workspace file does not exist')
    lock = source.with_name(source.name + '.byw.lock')
    owner = {'pid': os.getpid(), 'token': str(uuid.uuid4()), 'workspace': str(source)}
    end = time.monotonic() + timeout
    while True:
        try:
            with lock.open('x', encoding='utf-8') as stream:
                json.dump(owner, stream)
            break
        except FileExistsError:
            if time.monotonic() >= end:
                raise b.Invalid('Workspace writer lock is held; inspect its owner before recovery: ' + str(lock))
            time.sleep(0.05)
    try:
        yield
    finally:
        try:
            if json.loads(lock.read_text(encoding='utf-8')).get('token') == owner['token']:
                lock.unlink()
        except (FileNotFoundError, ValueError, OSError):
            pass
