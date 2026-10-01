# Derived from the supplied SAP Configuration Architect importer.
# Only the XLSM and canonical configuration index import call graph is retained.
from __future__ import annotations
import argparse
import collections
import datetime as dt
import hashlib
import html
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import textwrap
import uuid
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any, Iterable, Iterator
SCHEMA_VERSION = '1.0.0'
MAIN_NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
OFFICE_REL_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG_REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS = {'m': MAIN_NS, 'r': OFFICE_REL_NS}
ACTIVITY_FIELDS = ['application_area', 'application_subarea', 'configuration_item_name', 'configuration_item_id', 'configuration_activity', 'available_in_configure_your_solution', 'configuration_approach', 'category', 'configuration_activity_id', 'main_scope_item_id', 'main_scope_item_description', 'locality_type', 'specialized_countries', 'img_activity', 'application_component_id', 'redo_in_p', 'delete_customer_records', 'additional_information', 'file_upload_enabled']
ACCESS_FIELDS = ['business_catalog_id', 'description', 'transaction_code', 'iam_app_id', 'img_activity', 'explanatory_text', 'sscui_id', 'component_id', 'img_ach']
OFFICIAL_DOMAINS = ('help.sap.com', 'learning.sap.com', 'me.sap.com', 'support.sap.com', 'launchpad.support.sap.com', 'api.sap.com', 'fioriappslibrary.hana.ondemand.com', 'signavio.com')

def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

def clean_text(value: Any) -> str:
    if value is None:
        return ''
    s = str(value).replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
    s = re.sub('[ \\t]+', ' ', s)
    s = re.sub('\\n{3,}', '\n\n', s)
    return s.strip()

def parse_yes_no(value: str) -> bool | None:
    v = clean_text(value).lower()
    if v in {'yes', 'y', 'true', 'x', 'enabled'}:
        return True
    if v in {'no', 'n', 'false', 'disabled'}:
        return False
    return None

def split_codes(value: str) -> list[str]:
    value = clean_text(value)
    if not value:
        return []
    parts = re.split('[,;|\\n]+', value)
    return [p.strip() for p in parts if p.strip()]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def stable_id(prefix: str, *parts: Any, length: int=16) -> str:
    raw = '\x1f'.join((clean_text(p) for p in parts)).encode('utf-8')
    return f'{prefix}-{hashlib.sha256(raw).hexdigest()[:length]}'

def json_dump(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write('\n')
    os.replace(tmp, path)

def json_load(path: Path, default: Any=None) -> Any:
    if not path.exists():
        return default
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open('r', encoding='utf-8') as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSONL {path}:{line_no}: {exc}') from exc
            if not isinstance(obj, dict):
                raise ValueError(f'JSONL object expected at {path}:{line_no}')
            rows.append(obj)
    return rows

def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    count = 0
    with tmp.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
            count += 1
    os.replace(tmp, path)
    return count

def release_dir(root: Path, release: str) -> Path:
    return root / 'data' / 'releases' / release

def ensure_release_dirs(root: Path, release: str) -> Path:
    rd = release_dir(root, release)
    for rel in ['source', 'catalog/expert-config', 'changes/whats-new/checks', 'changes/catalog-diff', 'knowledge/activities', 'knowledge/dependencies', 'knowledge/incidents', 'knowledge/lessons', 'indexes']:
        (rd / rel).mkdir(parents=True, exist_ok=True)
    for relfile in ['knowledge/dependencies/edges.jsonl', 'knowledge/incidents/incidents.jsonl', 'knowledge/lessons/lessons.jsonl', 'knowledge/source-registry.jsonl', 'changes/whats-new/entries.jsonl']:
        p = rd / relfile
        if not p.exists():
            p.touch()
    return rd

def col_letters_to_index(ref: str) -> int:
    m = re.match('([A-Z]+)', ref.upper())
    if not m:
        raise ValueError(f'Invalid cell ref: {ref}')
    n = 0
    for ch in m.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1

def index_to_col_letters(index: int) -> str:
    index += 1
    out = []
    while index:
        index, rem = divmod(index - 1, 26)
        out.append(chr(65 + rem))
    return ''.join(reversed(out))

class XlsmReader:
    """Minimal OOXML reader for values and hyperlinks; no external dependency."""

    def __init__(self, path: Path):
        self.path = path
        self.zf = zipfile.ZipFile(path)
        self.names = set(self.zf.namelist())
        self.shared_strings = self._load_shared_strings()
        self.sheet_paths = self._load_sheet_paths()

    def close(self) -> None:
        self.zf.close()

    def __enter__(self) -> 'XlsmReader':
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _load_shared_strings(self) -> list[str]:
        path = 'xl/sharedStrings.xml'
        if path not in self.names:
            return []
        root = ET.fromstring(self.zf.read(path))
        out = []
        for si in root.findall(f'{{{MAIN_NS}}}si'):
            texts = [t.text or '' for t in si.iter(f'{{{MAIN_NS}}}t')]
            out.append(''.join(texts))
        return out

    def _load_sheet_paths(self) -> dict[str, str]:
        wb = ET.fromstring(self.zf.read('xl/workbook.xml'))
        rels = ET.fromstring(self.zf.read('xl/_rels/workbook.xml.rels'))
        relmap = {r.attrib['Id']: r.attrib['Target'] for r in rels}
        out: dict[str, str] = {}
        sheets = wb.find(f'{{{MAIN_NS}}}sheets')
        if sheets is None:
            return out
        for s in sheets:
            rid = s.attrib[f'{{{OFFICE_REL_NS}}}id']
            target = relmap[rid].lstrip('/')
            if not target.startswith('xl/'):
                target = 'xl/' + target
            out[s.attrib['name']] = target
        return out

    @property
    def sheet_names(self) -> list[str]:
        return list(self.sheet_paths)

    def _sheet_rels(self, sheet_path: str) -> dict[str, str]:
        p = Path(sheet_path)
        rel_path = str(p.parent / '_rels' / (p.name + '.rels'))
        if rel_path not in self.names:
            return {}
        root = ET.fromstring(self.zf.read(rel_path))
        return {r.attrib['Id']: r.attrib.get('Target', '') for r in root}

    def hyperlinks(self, sheet_name: str) -> dict[str, dict[str, str]]:
        sheet_path = self.sheet_paths[sheet_name]
        root = ET.fromstring(self.zf.read(sheet_path))
        rels = self._sheet_rels(sheet_path)
        hroot = root.find(f'{{{MAIN_NS}}}hyperlinks')
        out: dict[str, dict[str, str]] = {}
        if hroot is None:
            return out
        for h in hroot:
            ref = h.attrib.get('ref', '')
            rid = h.attrib.get(f'{{{OFFICE_REL_NS}}}id', '')
            target = rels.get(rid, '')
            location = h.attrib.get('location', '')
            if target and location:
                if target.endswith('/'):
                    target = target + location.lstrip('/')
                elif location.startswith('/'):
                    target = target.rstrip('/') + location
                else:
                    target = target + '#' + location
            elif not target:
                target = location
            out[ref] = {'target': target, 'display': h.attrib.get('display', ''), 'tooltip': h.attrib.get('tooltip', ''), 'location': location}
        return out

    def _cell_value(self, cell: ET.Element) -> str:
        ctype = cell.attrib.get('t', '')
        if ctype == 'inlineStr':
            texts = [t.text or '' for t in cell.iter(f'{{{MAIN_NS}}}t')]
            return clean_text(''.join(texts))
        v = cell.find(f'{{{MAIN_NS}}}v')
        if v is None or v.text is None:
            return ''
        raw = v.text
        if ctype == 's':
            try:
                return clean_text(self.shared_strings[int(raw)])
            except (ValueError, IndexError):
                return clean_text(raw)
        if ctype == 'b':
            return 'Yes' if raw == '1' else 'No'
        return clean_text(raw)

    def rows(self, sheet_name: str) -> Iterator[tuple[int, dict[int, str]]]:
        sheet_path = self.sheet_paths[sheet_name]
        root = ET.fromstring(self.zf.read(sheet_path))
        sheet_data = root.find(f'{{{MAIN_NS}}}sheetData')
        if sheet_data is None:
            return
        for row in sheet_data:
            rownum = int(row.attrib.get('r', '0') or 0)
            values: dict[int, str] = {}
            for cell in row.findall(f'{{{MAIN_NS}}}c'):
                ref = cell.attrib.get('r', '')
                if not ref:
                    continue
                values[col_letters_to_index(ref)] = self._cell_value(cell)
            yield (rownum, values)

    def nonempty_cells(self, sheet_name: str) -> list[dict[str, Any]]:
        links = self.hyperlinks(sheet_name)
        out = []
        for rownum, values in self.rows(sheet_name):
            for col, value in sorted(values.items()):
                if not clean_text(value) and f'{index_to_col_letters(col)}{rownum}' not in links:
                    continue
                ref = f'{index_to_col_letters(col)}{rownum}'
                record: dict[str, Any] = {'cell': ref, 'row': rownum, 'column': index_to_col_letters(col), 'value': clean_text(value)}
                if ref in links:
                    record['hyperlink'] = links[ref]
                out.append(record)
        return out

def extract_support_components(text: str) -> list[str]:
    pats = re.findall('\\b(?:XX-S4C-[A-Z0-9-]+|[A-Z]{2,4}(?:-[A-Z0-9*]{2,}){1,5})\\b', text)
    return sorted(set(pats))

def extract_note_numbers(text: str, urls: Iterable[str]) -> list[str]:
    nums = set(re.findall('(?:note|notes/)[^0-9]{0,5}(\\d{5,10})', text, flags=re.I))
    for url in urls:
        nums.update(re.findall('(?:notes?/|/notes/)(\\d{5,10})', url, flags=re.I))
    return sorted(nums)

def expert_markdown(record: dict[str, Any]) -> str:
    lines = [f"# {record.get('title') or record.get('linked_activity_id')}", '']
    lines.append(f"- Release: `{record.get('release')}`")
    lines.append(f"- Workbook sheet: `{record.get('source_sheet')}`")
    if record.get('last_updated'):
        lines.append(f"- Last update in workbook: {record['last_updated']}")
    if record.get('support_components'):
        lines.append(f"- Support components: {', '.join(record['support_components'])}")
    if record.get('note_numbers'):
        lines.append(f"- SAP Notes: {', '.join(record['note_numbers'])}")
    lines.extend(['', '## Workbook Content', ''])
    current_row = None
    row_parts: list[str] = []
    for cell in record.get('cells', []):
        if current_row is None:
            current_row = cell['row']
        if cell['row'] != current_row:
            if row_parts:
                lines.append(' | '.join(row_parts))
            current_row = cell['row']
            row_parts = []
        value = cell.get('value', '')
        link = (cell.get('hyperlink') or {}).get('target', '')
        if link:
            value = f'{value or link} ({link})'
        if value:
            row_parts.append(f"**{cell['cell']}**: {value}")
    if row_parts:
        lines.append(' | '.join(row_parts))
    lines.append('')
    return '\n'.join(lines)

def command_import_catalog(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    xlsm = Path(args.xlsm).resolve()
    release = clean_text(args.release)
    if not xlsm.exists():
        raise FileNotFoundError(xlsm)
    rd = ensure_release_dirs(root, release)
    source_target = rd / 'source' / xlsm.name
    if xlsm != source_target:
        shutil.copy2(xlsm, source_target)
    with XlsmReader(xlsm) as reader:
        main_sheet = release if release in reader.sheet_names else reader.sheet_names[0]
        access_sheet = 'IMG Activity TRAN in BC' if 'IMG Activity TRAN in BC' in reader.sheet_names else reader.sheet_names[1]
        expert_sheets = [s for s in reader.sheet_names if s not in {main_sheet, access_sheet, 'Doc. Info'}]
        main_links = reader.hyperlinks(main_sheet)
        activities: list[dict[str, Any]] = []
        for rownum, values in reader.rows(main_sheet):
            if rownum < 5:
                continue
            raw = [clean_text(values.get(i, '')) for i in range(len(ACTIVITY_FIELDS))]
            if not any(raw):
                continue
            rec = dict(zip(ACTIVITY_FIELDS, raw))
            aid = rec['configuration_activity_id']
            cell_ref = f'I{rownum}'
            link = main_links.get(cell_ref, {})
            rec.update({'schema_version': SCHEMA_VERSION, 'release': release, 'source_sheet': main_sheet, 'source_row': rownum, 'configuration_activity_link': link.get('target', ''), 'is_expert_configuration': aid in expert_sheets, 'is_numeric_activity_id': bool(re.fullmatch('\\d+', aid)), 'available_in_configure_your_solution_bool': parse_yes_no(rec['available_in_configure_your_solution']), 'redo_in_p_bool': parse_yes_no(rec['redo_in_p']), 'file_upload_enabled_bool': parse_yes_no(rec['file_upload_enabled']), 'specialized_country_codes': split_codes(rec['specialized_countries']), 'catalog_record_id': stable_id('cat', release, rownum, aid, rec['configuration_activity'])})
            activities.append(rec)
        access_rows: list[dict[str, Any]] = []
        for rownum, values in reader.rows(access_sheet):
            if rownum < 2:
                continue
            raw = [clean_text(values.get(i, '')) for i in range(len(ACCESS_FIELDS))]
            if not any(raw):
                continue
            rec = dict(zip(ACCESS_FIELDS, raw))
            rec.update({'schema_version': SCHEMA_VERSION, 'release': release, 'source_sheet': access_sheet, 'source_row': rownum, 'access_record_id': stable_id('acc', release, rownum, *raw)})
            access_rows.append(rec)
        expert_rows: list[dict[str, Any]] = []
        for sheet in expert_sheets:
            cells = reader.nonempty_cells(sheet)
            flattened = '\n'.join((c.get('value', '') for c in cells if c.get('value')))
            urls = sorted({(c.get('hyperlink') or {}).get('target', '') for c in cells if (c.get('hyperlink') or {}).get('target', '')})
            first_row_values = [c.get('value', '') for c in cells if c.get('row') == 1 and c.get('value')]
            title = first_row_values[0] if first_row_values else sheet
            last_updated = ''
            m = re.search('Last Update\\s*:\\s*([^\\n]+)', flattened, flags=re.I)
            if m:
                last_updated = clean_text(m.group(1))
            rec = {'schema_version': SCHEMA_VERSION, 'release': release, 'linked_activity_id': sheet, 'source_sheet': sheet, 'title': title, 'last_updated': last_updated, 'support_components': extract_support_components(flattened), 'note_numbers': extract_note_numbers(flattened, urls), 'urls': urls, 'cells': cells, 'flattened_text': flattened, 'expert_record_id': stable_id('exp', release, sheet, title)}
            expert_rows.append(rec)
            md_path = rd / 'catalog' / 'expert-config' / f'{sheet}.md'
            md_path.write_text(expert_markdown(rec), encoding='utf-8')
    activities_path = rd / 'catalog' / 'activities.jsonl'
    access_path = rd / 'catalog' / 'access-map.jsonl'
    expert_path = rd / 'catalog' / 'expert-config.jsonl'
    write_jsonl(activities_path, activities)
    write_jsonl(access_path, access_rows)
    write_jsonl(expert_path, expert_rows)
    categories = collections.Counter((r['category'] or '<blank>' for r in activities))
    availability = collections.Counter((r['available_in_configure_your_solution'] or '<blank>' for r in activities))
    redo = collections.Counter((r['redo_in_p'] or '<blank>' for r in activities))
    deletion = collections.Counter((r['delete_customer_records'] or '<blank>' for r in activities))
    upload = collections.Counter((r['file_upload_enabled'] or '<blank>' for r in activities))
    manifest = {'schema_version': SCHEMA_VERSION, 'release': release, 'generated_at': utc_now(), 'source': {'filename': xlsm.name, 'packaged_path': str(source_target.relative_to(root)), 'size_bytes': source_target.stat().st_size, 'sha256': sha256_file(source_target)}, 'sheets': {'activity_catalog': main_sheet, 'access_map': access_sheet, 'expert_configuration': expert_sheets}, 'counts': {'activity_records': len(activities), 'unique_activity_ids': len({r['configuration_activity_id'] for r in activities if r['configuration_activity_id']}), 'numeric_activity_ids': len({r['configuration_activity_id'] for r in activities if re.fullmatch('\\d+', r['configuration_activity_id'] or '')}), 'non_numeric_activity_ids': len({r['configuration_activity_id'] for r in activities if r['configuration_activity_id'] and (not re.fullmatch('\\d+', r['configuration_activity_id']))}), 'unique_activity_names': len({r['configuration_activity'] for r in activities if r['configuration_activity']}), 'application_areas': len({r['application_area'] for r in activities if r['application_area']}), 'application_subareas': len({r['application_subarea'] for r in activities if r['application_subarea']}), 'access_map_records': len(access_rows), 'unique_business_catalog_ids': len({r['business_catalog_id'] for r in access_rows if r['business_catalog_id']}), 'unique_transaction_codes': len({r['transaction_code'] for r in access_rows if r['transaction_code']}), 'unique_iam_app_ids': len({r['iam_app_id'] for r in access_rows if r['iam_app_id']}), 'expert_configuration_records': len(expert_rows)}, 'distributions': {'category': dict(sorted(categories.items())), 'available_in_configure_your_solution': dict(sorted(availability.items())), 'redo_in_p': dict(sorted(redo.items())), 'delete_customer_records': dict(sorted(deletion.items())), 'file_upload_enabled': dict(sorted(upload.items()))}, 'files': {'activities': {'path': str(activities_path.relative_to(root)), 'sha256': sha256_file(activities_path)}, 'access_map': {'path': str(access_path.relative_to(root)), 'sha256': sha256_file(access_path)}, 'expert_config': {'path': str(expert_path.relative_to(root)), 'sha256': sha256_file(expert_path)}}}
    json_dump(rd / 'catalog' / 'manifest.json', manifest)
    return manifest

def discover_releases(root: Path) -> list[str]:
    base = root / 'data' / 'releases'
    if not base.exists():
        return []
    return sorted((p.name for p in base.iterdir() if p.is_dir()))

def markdown_sections(text: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    title = 'document'
    buf: list[str] = []
    for line in text.splitlines():
        if re.match('^#{1,3}\\s+', line):
            if buf and clean_text('\n'.join(buf)):
                sections.append((title, clean_text('\n'.join(buf))))
            title = re.sub('^#{1,3}\\s+', '', line).strip()
            buf = []
        else:
            buf.append(line)
    if buf and clean_text('\n'.join(buf)):
        sections.append((title, clean_text('\n'.join(buf))))
    return sections

def latest_by_revision(rows: list[dict[str, Any]], id_key: str) -> list[dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = clean_text(row.get(id_key))
        if not key:
            continue
        rev = int(row.get('revision', 1) or 1)
        if key not in out or rev >= int(out[key].get('revision', 1) or 1):
            out[key] = row
    return list(out.values())

def insert_doc(conn: sqlite3.Connection, doc: dict[str, Any]) -> None:
    conn.execute('INSERT OR REPLACE INTO documents\n        (doc_id, release, doc_type, entity_id, section, title, body, tags, source_path, updated_at, json)\n        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (doc.get('doc_id', ''), doc.get('release', ''), doc.get('doc_type', ''), doc.get('entity_id', ''), doc.get('section', ''), doc.get('title', ''), doc.get('body', ''), doc.get('tags', ''), doc.get('source_path', ''), doc.get('updated_at', ''), json.dumps({'doc_type': doc.get('doc_type', ''), 'entity_id': doc.get('entity_id', '')}, ensure_ascii=False)))
    conn.execute('INSERT INTO documents_fts\n        (doc_id, release, doc_type, entity_id, section, title, body, tags)\n        VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (doc.get('doc_id', ''), doc.get('release', ''), doc.get('doc_type', ''), doc.get('entity_id', ''), doc.get('section', ''), doc.get('title', ''), doc.get('body', ''), doc.get('tags', '')))

def build_index(root: Path, releases: list[str] | None=None) -> dict[str, Any]:
    releases = releases or discover_releases(root)
    if not releases:
        raise ValueError('No release folders found')
    index_path = root / 'data' / 'knowledge.sqlite3'
    index_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix='sca-index-', suffix='.sqlite3', dir=str(index_path.parent))
    os.close(fd)
    tmp_path = Path(tmp_name)
    counts = collections.Counter()
    source_files: dict[str, str] = {}
    try:
        conn = sqlite3.connect(tmp_path)
        conn.execute('PRAGMA journal_mode=OFF')
        conn.execute('PRAGMA synchronous=OFF')
        conn.executescript("\n            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);\n            CREATE TABLE activities (\n                release TEXT NOT NULL, source_row INTEGER NOT NULL, activity_id TEXT,\n                activity_name TEXT, application_area TEXT, application_subarea TEXT,\n                configuration_item_id TEXT, configuration_item_name TEXT, category TEXT,\n                scope_item_id TEXT, scope_item_description TEXT, locality_type TEXT,\n                specialized_countries TEXT, img_activity TEXT, component_id TEXT,\n                configuration_approach TEXT, redo_in_p TEXT, delete_customer_records TEXT,\n                file_upload_enabled TEXT, is_expert INTEGER, json TEXT NOT NULL,\n                PRIMARY KEY (release, source_row)\n            );\n            CREATE INDEX idx_activities_id ON activities(release, activity_id);\n            CREATE INDEX idx_activities_img ON activities(release, img_activity);\n            CREATE INDEX idx_activities_component ON activities(release, component_id);\n            CREATE TABLE access_map (\n                release TEXT, source_row INTEGER, business_catalog_id TEXT, description TEXT,\n                transaction_code TEXT, iam_app_id TEXT, img_activity TEXT, sscui_id TEXT,\n                component_id TEXT, json TEXT NOT NULL\n            );\n            CREATE INDEX idx_access_sscui ON access_map(release, sscui_id);\n            CREATE INDEX idx_access_img ON access_map(release, img_activity);\n            CREATE TABLE expert_config (release TEXT, activity_id TEXT, title TEXT, json TEXT NOT NULL);\n            CREATE TABLE changes (release TEXT, entry_id TEXT, title TEXT, change_type TEXT,\n                                  activity_ids TEXT, valid_from TEXT, source_url TEXT, json TEXT NOT NULL);\n            CREATE TABLE dependencies (release TEXT, edge_id TEXT, source_activity_id TEXT,\n                                       target_activity_id TEXT, relation TEXT, status TEXT,\n                                       evidence_level TEXT, json TEXT NOT NULL);\n            CREATE TABLE incidents (release TEXT, incident_id TEXT, status TEXT,\n                                    related_activity_ids TEXT, created_at TEXT, json TEXT NOT NULL);\n            CREATE TABLE lessons (release TEXT, lesson_id TEXT, status TEXT,\n                                  activity_ids TEXT, confidence_score INTEGER, json TEXT NOT NULL);\n            CREATE TABLE documents (\n                doc_id TEXT PRIMARY KEY, release TEXT, doc_type TEXT, entity_id TEXT,\n                section TEXT, title TEXT, body TEXT, tags TEXT, source_path TEXT,\n                updated_at TEXT, json TEXT NOT NULL\n            );\n            CREATE VIRTUAL TABLE documents_fts USING fts5(\n                doc_id UNINDEXED, release UNINDEXED, doc_type UNINDEXED,\n                entity_id UNINDEXED, section UNINDEXED,\n                title, body, tags,\n                tokenize='unicode61 remove_diacritics 2'\n            );\n            ")
        for release in releases:
            rd = release_dir(root, release)
            paths = [rd / 'catalog' / 'activities.jsonl', rd / 'catalog' / 'access-map.jsonl', rd / 'catalog' / 'expert-config.jsonl', rd / 'changes' / 'whats-new' / 'entries.jsonl', rd / 'knowledge' / 'dependencies' / 'edges.jsonl', rd / 'knowledge' / 'incidents' / 'incidents.jsonl', rd / 'knowledge' / 'lessons' / 'lessons.jsonl']
            for p in paths:
                if p.exists():
                    source_files[str(p.relative_to(root))] = sha256_file(p)
            for rec in read_jsonl(paths[0]):
                conn.execute('INSERT INTO activities VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (release, int(rec.get('source_row', 0) or 0), rec.get('configuration_activity_id', ''), rec.get('configuration_activity', ''), rec.get('application_area', ''), rec.get('application_subarea', ''), rec.get('configuration_item_id', ''), rec.get('configuration_item_name', ''), rec.get('category', ''), rec.get('main_scope_item_id', ''), rec.get('main_scope_item_description', ''), rec.get('locality_type', ''), rec.get('specialized_countries', ''), rec.get('img_activity', ''), rec.get('application_component_id', ''), rec.get('configuration_approach', ''), rec.get('redo_in_p', ''), rec.get('delete_customer_records', ''), rec.get('file_upload_enabled', ''), 1 if rec.get('is_expert_configuration') else 0, json.dumps(rec, ensure_ascii=False)))
                title = f"{rec.get('configuration_activity', '')} ({rec.get('configuration_activity_id', '')})"
                body = '\n'.join((clean_text(rec.get(k, '')) for k in ['application_area', 'application_subarea', 'configuration_item_name', 'configuration_activity', 'configuration_approach', 'category', 'main_scope_item_id', 'locality_type', 'specialized_countries', 'img_activity', 'application_component_id', 'redo_in_p', 'delete_customer_records', 'additional_information', 'file_upload_enabled'] if clean_text(rec.get(k, ''))))
                tags = ' '.join((clean_text(rec.get(k, '')) for k in ['configuration_activity_id', 'configuration_item_id', 'main_scope_item_id', 'img_activity', 'application_component_id']))
                insert_doc(conn, {'doc_id': f"catalog:{release}:{rec.get('source_row')}", 'release': release, 'doc_type': 'catalog_activity', 'entity_id': rec.get('configuration_activity_id', ''), 'section': 'catalog', 'title': title, 'body': body, 'tags': tags, 'source_path': str(paths[0].relative_to(root)), 'updated_at': '', 'json': rec})
                counts['catalog_activity'] += 1
            for rec in read_jsonl(paths[1]):
                conn.execute('INSERT INTO access_map VALUES (?,?,?,?,?,?,?,?,?,?)', (release, int(rec.get('source_row', 0) or 0), rec.get('business_catalog_id', ''), rec.get('description', ''), rec.get('transaction_code', ''), rec.get('iam_app_id', ''), rec.get('img_activity', ''), rec.get('sscui_id', ''), rec.get('component_id', ''), json.dumps(rec, ensure_ascii=False)))
                if any((rec.get(k) for k in ('sscui_id', 'img_activity', 'transaction_code', 'iam_app_id'))):
                    insert_doc(conn, {'doc_id': f"access:{release}:{rec.get('source_row')}", 'release': release, 'doc_type': 'access_map', 'entity_id': rec.get('sscui_id', '') or rec.get('img_activity', ''), 'section': 'authorization_access', 'title': f"{rec.get('business_catalog_id', '')} {rec.get('description', '')}", 'body': '\n'.join((clean_text(rec.get(k, '')) for k in ACCESS_FIELDS if clean_text(rec.get(k, '')))), 'tags': ' '.join((clean_text(rec.get(k, '')) for k in ['sscui_id', 'img_activity', 'transaction_code', 'iam_app_id', 'component_id'])), 'source_path': str(paths[1].relative_to(root)), 'updated_at': '', 'json': rec})
                counts['access_map'] += 1
            for rec in read_jsonl(paths[2]):
                conn.execute('INSERT INTO expert_config VALUES (?,?,?,?)', (release, rec.get('linked_activity_id', ''), rec.get('title', ''), json.dumps(rec, ensure_ascii=False)))
                insert_doc(conn, {'doc_id': f"expert:{release}:{rec.get('linked_activity_id')}", 'release': release, 'doc_type': 'expert_configuration', 'entity_id': rec.get('linked_activity_id', ''), 'section': 'expert_configuration', 'title': rec.get('title', ''), 'body': rec.get('flattened_text', ''), 'tags': ' '.join(rec.get('support_components', []) + rec.get('note_numbers', [])), 'source_path': str(paths[2].relative_to(root)), 'updated_at': rec.get('last_updated', ''), 'json': rec})
                counts['expert_configuration'] += 1
            for rec in read_jsonl(paths[3]):
                activity_ids = rec.get('activity_ids', []) or rec.get('related_activity_ids', []) or []
                conn.execute('INSERT INTO changes VALUES (?,?,?,?,?,?,?,?)', (release, rec.get('entry_id', ''), rec.get('title', ''), rec.get('change_type', ''), json.dumps(activity_ids, ensure_ascii=False), rec.get('valid_from', ''), rec.get('source_url', ''), json.dumps(rec, ensure_ascii=False)))
                insert_doc(conn, {'doc_id': f"change:{release}:{rec.get('entry_id')}", 'release': release, 'doc_type': 'whats_new', 'entity_id': ' '.join(activity_ids), 'section': rec.get('change_type', ''), 'title': rec.get('title', ''), 'body': clean_text(rec.get('summary', '')) + '\n' + '\n'.join(rec.get('implementation_impact', []) or []), 'tags': ' '.join(activity_ids + (rec.get('technical_objects', []) or []) + (rec.get('scope_items', []) or []) + (rec.get('application_components', []) or [])), 'source_path': str(paths[3].relative_to(root)), 'updated_at': rec.get('latest_revision', ''), 'json': rec})
                counts['whats_new'] += 1
            for rec in read_jsonl(paths[4]):
                conn.execute('INSERT INTO dependencies VALUES (?,?,?,?,?,?,?,?)', (release, rec.get('edge_id', ''), rec.get('source_activity_id', ''), rec.get('target_activity_id', ''), rec.get('relation', ''), rec.get('status', ''), rec.get('evidence_level', ''), json.dumps(rec, ensure_ascii=False)))
                insert_doc(conn, {'doc_id': f"dependency:{release}:{rec.get('edge_id')}", 'release': release, 'doc_type': 'dependency', 'entity_id': f"{rec.get('source_activity_id', '')} {rec.get('target_activity_id', '')}", 'section': rec.get('relation', ''), 'title': f"{rec.get('source_activity_id', '')} {rec.get('relation', '')} {rec.get('target_activity_id', '')}", 'body': '\n'.join([clean_text(rec.get('condition', '')), clean_text(rec.get('reason', '')), '\n'.join(rec.get('process_impact', []) or [])]), 'tags': f"{rec.get('status', '')} {rec.get('evidence_level', '')}", 'source_path': str(paths[4].relative_to(root)), 'updated_at': rec.get('last_validated_at', ''), 'json': rec})
                counts['dependency'] += 1
            for rec in latest_by_revision(read_jsonl(paths[5]), 'incident_id'):
                related = rec.get('related_activity_ids', []) or []
                conn.execute('INSERT INTO incidents VALUES (?,?,?,?,?,?)', (release, rec.get('incident_id', ''), rec.get('status', ''), json.dumps(related), rec.get('created_at', ''), json.dumps(rec, ensure_ascii=False)))
                insert_doc(conn, {'doc_id': f"incident:{release}:{rec.get('incident_id')}", 'release': release, 'doc_type': 'incident', 'entity_id': ' '.join(related), 'section': rec.get('status', ''), 'title': rec.get('title', '') or clean_text(rec.get('sanitized_error_text', ''))[:120], 'body': '\n'.join((clean_text(rec.get(k, '')) for k in ['sanitized_error_text', 'process_context', 'confirmed_root_cause', 'resolution', 'verification'])), 'tags': ' '.join(related + [rec.get('message_class', ''), rec.get('message_number', ''), rec.get('app_id', '')]), 'source_path': str(paths[5].relative_to(root)), 'updated_at': rec.get('updated_at', rec.get('created_at', '')), 'json': rec})
                counts['incident'] += 1
            for rec in latest_by_revision(read_jsonl(paths[6]), 'lesson_id'):
                applies = rec.get('applies_to', {}) or {}
                activity_ids = applies.get('activity_ids', []) or []
                conn.execute('INSERT INTO lessons VALUES (?,?,?,?,?,?)', (release, rec.get('lesson_id', ''), rec.get('status', ''), json.dumps(activity_ids), int(rec.get('confidence_score', 0) or 0), json.dumps(rec, ensure_ascii=False)))
                insert_doc(conn, {'doc_id': f"lesson:{release}:{rec.get('lesson_id')}", 'release': release, 'doc_type': 'lesson', 'entity_id': ' '.join(activity_ids), 'section': rec.get('status', ''), 'title': rec.get('title', ''), 'body': '\n'.join(['\n'.join(rec.get('symptoms', []) or []), clean_text(rec.get('root_cause', '')), clean_text(rec.get('resolution', '')), clean_text(rec.get('verification', ''))]), 'tags': ' '.join(activity_ids + (applies.get('scope_items', []) or []) + (applies.get('countries', []) or [])), 'source_path': str(paths[6].relative_to(root)), 'updated_at': rec.get('updated_at', rec.get('created_at', '')), 'json': rec})
                counts['lesson'] += 1
            activities_dir = rd / 'knowledge' / 'activities'
            if activities_dir.exists():
                for profile_path in sorted(activities_dir.glob('*/profile.json')):
                    profile = json_load(profile_path, {})
                    aid = clean_text(profile.get('activity_id') or profile_path.parent.name)
                    doc_path = profile_path.parent / 'documentation.md'
                    doc_text = doc_path.read_text(encoding='utf-8') if doc_path.exists() else ''
                    for section, body in markdown_sections(doc_text) or [('profile', json.dumps(profile, ensure_ascii=False))]:
                        doc_id = stable_id('doc', release, aid, section)
                        insert_doc(conn, {'doc_id': doc_id, 'release': release, 'doc_type': 'activity_dossier', 'entity_id': aid, 'section': section, 'title': f"{profile.get('official_name', aid)} — {section}", 'body': body, 'tags': ' '.join([aid, profile.get('official_name', ''), profile.get('confidence', ''), profile.get('status', '')]), 'source_path': str(doc_path.relative_to(root) if doc_path.exists() else profile_path.relative_to(root)), 'updated_at': profile.get('updated_at', ''), 'json': profile})
                        counts['activity_dossier_section'] += 1
        conn.execute('INSERT INTO metadata VALUES (?,?)', ('schema_version', SCHEMA_VERSION))
        conn.execute('INSERT INTO metadata VALUES (?,?)', ('built_at', utc_now()))
        conn.execute('INSERT INTO metadata VALUES (?,?)', ('releases', json.dumps(releases)))
        conn.commit()
        integrity = conn.execute('PRAGMA integrity_check').fetchone()[0]
        if integrity != 'ok':
            raise RuntimeError(f'SQLite integrity check failed: {integrity}')
        conn.close()
        os.replace(tmp_path, index_path)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise
    manifest = {'schema_version': SCHEMA_VERSION, 'built_at': utc_now(), 'releases': releases, 'index_path': str(index_path.relative_to(root)), 'index_sha256': sha256_file(index_path), 'counts': dict(sorted(counts.items())), 'source_files': source_files}
    json_dump(root / 'data' / 'index-manifest.json', manifest)
    for release in releases:
        rd = release_dir(root, release)
        json_dump(rd / 'indexes' / 'index-reference.json', {'global_index': str(index_path.relative_to(root)), 'built_at': manifest['built_at'], 'index_sha256': manifest['index_sha256']})
    return manifest
