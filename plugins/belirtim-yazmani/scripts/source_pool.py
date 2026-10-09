# SPDX-License-Identifier: GPL-3.0-only
"""One complete source per byte hash; lazy reference resolution and bounded packets."""
import hashlib
import json
from pathlib import Path

import bv2 as b

PROTOCOL = '3.3'
POOL_VERSION = 1
MAX_PACKET_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 3 * MAX_PACKET_BYTES


def chunks(value):
    return json.JSONEncoder(ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                            allow_nan=False).iterencode(value)


def value_sha(value):
    digest = hashlib.sha256()
    for chunk in chunks(value):
        digest.update(chunk.encode('utf-8'))
    return digest.hexdigest()


def size(value, limit=None):
    count = 0
    for chunk in chunks(value):
        count += len(chunk.encode('utf-8'))
        if limit is not None and count > limit:
            raise b.Invalid('BLOCKED: REVIEW_PACKET_VOLUME exceeds serialization limit ' + str(limit))
    return count


def limits(control=None):
    configured = (control or {}).get('review_packet_limits', {})
    if not isinstance(configured, dict) or set(configured) - {'max_packet_bytes', 'max_total_bytes'}:
        raise b.Invalid('BLOCKED: invalid private review packet limits')
    per = configured.get('max_packet_bytes', MAX_PACKET_BYTES)
    total = configured.get('max_total_bytes', MAX_TOTAL_BYTES)
    if type(per) is not int or type(total) is not int or not 1 <= per <= MAX_PACKET_BYTES or not 1 <= total <= MAX_TOTAL_BYTES:
        raise b.Invalid('BLOCKED: review packet limits must fit the existing read contract')
    return per, total


def check_volume(packets, control=None):
    per, total = limits(control)
    counts = [size(packet, per) for packet in packets]
    if sum(counts) > total:
        raise b.Invalid('BLOCKED: REVIEW_PACKET_VOLUME exceeds total serialization limit ' + str(total))
    return {'packet_bytes': counts, 'total_bytes': sum(counts), 'max_packet_bytes': per,
            'max_total_bytes': total, 'measurement': 'CANONICAL_JSON_UTF8_BEFORE_ENCODING'}


def decode_documents(files):
    """Decode byte-identical TOON files once even when exposed under aliases."""
    texts, by_path = {}, {}
    for path, data in files.items():
        if Path(path).suffix == '.toon':
            digest = b.digest(data)
            by_path[path] = digest
            if digest not in texts:
                texts[digest] = data.decode('utf-8')
    decoded = b.decode_many(texts) if texts else {}
    return {path: decoded[digest] for path, digest in by_path.items()}


def collect(references, files, decoded=None):
    """Return lightweight bindings and a hash-keyed pool; no input mutation."""
    import delivery as d
    decoded = decode_documents(files) if decoded is None else decoded
    sources, bindings, ids, hashes = {}, [], set(), {}
    for row in references:
        if row['id'] in ids:
            raise b.Invalid('Duplicate reference identity: ' + row['id'])
        ids.add(row['id'])
        path = row['path']
        if path in files and path not in hashes:
            hashes[path] = b.digest(files[path])
        if path not in files or hashes[path] != row['sha256']:
            raise b.Invalid('Referenced file missing or hash differs: ' + path)
        kind = 'TOON' if Path(path).suffix == '.toon' else 'TEXT'
        source_id = 'SRC-' + row['sha256']
        if source_id not in sources:
            content = decoded[path] if kind == 'TOON' else files[path].decode('utf-8')
            size(content, MAX_PACKET_BYTES)
            sources[source_id] = {'source_id': source_id, 'sha256': row['sha256'],
                                  'paths': [], 'format': kind, 'content': content,
                                  'content_sha256': value_sha(content)}
        source = sources[source_id]
        if source['format'] != kind:
            raise b.Invalid('Same source hash cannot have conflicting encodings')
        if path not in source['paths']:
            source['paths'].append(path)
        if row['pointer'] is not None:
            if kind != 'TOON':
                raise b.Invalid('Pointers require a decoded TOON document')
            try:
                d.resolve(source['content'], row['pointer'])
            except (b.Invalid, KeyError, IndexError, TypeError):
                raise b.Invalid('Referenced text/list pointer missing: ' + row['id'])
        bindings.append({**row, 'source_id': source_id})
    for source in sources.values():
        source['paths'].sort()
    return bindings, {'version': POOL_VERSION, 'sources': list(sources.values())}


class Reader:
    """Validate once, then resolve all references without decoding/re-embedding."""
    def __init__(self, packet, allow_legacy=False):
        import delivery as d
        if not isinstance(packet,dict):
            raise b.Invalid('Reader packet must be an object')
        references=packet.get('references',[])
        if not isinstance(references,list) or any(not isinstance(row,dict) or not isinstance(row.get('id'),str) or not row['id'] for row in references):
            raise b.Invalid('Reader references must be identity-bound objects')
        protocol = packet.get('protocol')
        if protocol != PROTOCOL and protocol != '3.2':
            if not allow_legacy or protocol not in ('3.0', '3.1'):
                raise b.Invalid('Unsupported or stale reader protocol; fresh 3.3 issuance required')
            self.legacy_read_only = True
            self.references = {r['id']: r for r in references}
            if len(self.references) != len(references):
                raise b.Invalid('Duplicate legacy reference identity')
            if packet.get('request_sha256') != value_sha({k: v for k, v in packet.items() if k != 'request_sha256'}):
                raise b.Invalid('Legacy request hash differs')
            self.sources = {}
            for ref in self.references.values():
                if 'content' not in ref:
                    raise b.Invalid('Legacy reference content is missing')
                key = ref['sha256']
                digest = value_sha(ref['content'])
                if key in self.sources and self.sources[key]['content_sha256'] != digest:
                    raise b.Invalid('Conflicting legacy source content')
                self.sources.setdefault(key, {'content': ref['content'], 'content_sha256': digest})
            return
        if protocol == '3.2' and not allow_legacy:
            raise b.Invalid('Unsupported or stale reader protocol; fresh 3.3 issuance required')
        self.legacy_read_only = protocol != PROTOCOL
        self.pooled = True
        pool = packet.get('source_pool', {})
        if not isinstance(pool,dict) or pool.get('version') != POOL_VERSION or not isinstance(pool.get('sources'), list):
            raise b.Invalid('Source pool version or shape differs')
        self.sources = {}
        for row in pool['sources']:
            if not isinstance(row,dict) or not isinstance(row.get('source_id'),str) or not isinstance(row.get('sha256'),str) or not isinstance(row.get('paths'),list) or any(not isinstance(path,str) for path in row['paths']) or row.get('format') not in ('TOON','TEXT'):
                raise b.Invalid('Source pool records must have valid identity/path/format')
            key = row.get('source_id')
            if key in self.sources or key != 'SRC-' + str(row.get('sha256')):
                raise b.Invalid('Duplicate or mismatched source identity')
            if value_sha(row.get('content')) != row.get('content_sha256'):
                raise b.Invalid('Source content hash differs')
            self.sources[key] = row
        self.references = {}
        for ref in references:
            if not all(isinstance(ref.get(key),str) for key in ('path','sha256','source_id')) or ref.get('pointer') is not None and not isinstance(ref['pointer'],str):
                raise b.Invalid('Reference source/path/hash/pointer shape differs')
            if ref['id'] in self.references or 'content' in ref:
                raise b.Invalid('References must be unique lightweight source bindings')
            source = self.sources.get(ref.get('source_id'))
            if not source or source['sha256'] != ref['sha256'] or ref['path'] not in source['paths']:
                raise b.Invalid('Reference source identity/path/hash differs')
            if ref['pointer'] is not None:
                if source.get('format') != 'TOON':
                    raise b.Invalid('Pointers require a decoded TOON document')
                try:
                    d.resolve(source['content'], ref['pointer'])
                except (b.Invalid, KeyError, IndexError, TypeError):
                    raise b.Invalid('Referenced text/list pointer missing: ' + ref['id'])
            self.references[ref['id']] = ref
        if packet.get('source_pool_sha256') != value_sha(pool):
            raise b.Invalid('Source pool binding hash differs')
        if packet.get('request_sha256') != value_sha({k: v for k, v in packet.items() if k != 'request_sha256'}):
            raise b.Invalid('Issued request hash differs')
        if not self.legacy_read_only:
            import review_contract
            review_contract.assert_scenario_packet(packet)

    def resolve(self, reference_id):
        import delivery as d
        if reference_id not in self.references:
            raise b.Invalid('Unknown reference identity: ' + reference_id)
        ref = self.references[reference_id]
        key = ref['source_id'] if getattr(self, 'pooled', False) else ref['sha256']
        content = self.sources[key]['content']
        return content if ref['pointer'] is None else d.resolve(content, ref['pointer'])

    def resolve_many(self, reference_ids):
        """Read a validated pool once, then resolve a requested ordered subset."""
        return {identity: self.resolve(identity) for identity in reference_ids}


def save_packets(packets, directory, control=None):
    """Bound all three encodings before writing any new packet file."""
    check_volume(packets, control)
    import review_contract
    if any(type(p.get('round')) is not int or p['round']<1 or p.get('reader_id') not in review_contract.READER_ROLES for p in packets):
        raise b.Invalid('Invalid reader packet output identity')
    names = {str(p['round']) + '-' + p['reader_id'] + '.toon': p for p in packets}
    if len(names) != len(packets):
        raise b.Invalid('Duplicate packet output identity')
    encoded = b.encode_many(names)
    per, total = limits(control)
    actual = {name: len(text.encode('utf-8')) for name, text in encoded.items()}
    if any(count > per for count in actual.values()) or sum(actual.values()) > total:
        raise b.Invalid('BLOCKED: REVIEW_PACKET_VOLUME encoded TOON exceeds read/serialization limit')
    directory = Path(directory)
    if any((directory / name).exists() for name in names):
        raise b.Invalid('Existing reader packets are immutable; use a new directory')
    directory.mkdir(parents=True, exist_ok=True)
    for name, text in encoded.items():
        (directory / name).write_bytes(text.encode('utf-8'))
    return {'files': list(names), 'bytes': actual, 'total_bytes': sum(actual.values())}
