from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sqlite3
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from .common import (PLUGIN, RELEASE_URL, YulaError, connect, digest, encode, file_hash,
                     load_json, now, official_url, rows, safe_id, sanitize, scalar)

CONFIG_TABLES = ("metadata", "activities", "access_map", "expert_config", "changes", "dependencies", "incidents", "lessons", "documents", "documents_fts")
OBJECT_TABLES = ("objects", "evidence", "members", "capabilities", "capability_aliases", "object_capabilities", "recipes", "object_content", "object_knowledge_fts")


def source_path(spec, base):
    import os
    value = spec.get("path")
    if spec.get("pathEnv"):
        value = os.environ.get(spec["pathEnv"])
    if not isinstance(value, str) or not value:
        raise YulaError("SOURCE_PATH", "This adapter requires a source path.")
    path = Path(value).expanduser()
    path = (Path(base) / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.exists():
        raise YulaError("SOURCE_MISSING", "Configured local source does not exist.", source=spec["id"])
    return path


def local_snapshot(path, stage):
    snapshot = Path(stage) / ("source-" + digest(str(path).encode())[:16] + ".sqlite")
    with connect(path) as src:
        dst = sqlite3.connect(snapshot)
        try:
            src.backup(dst); dst.execute("pragma journal_mode=delete"); dst.commit()
        finally:
            dst.close()
    with connect(snapshot) as db:
        if scalar(db, "pragma quick_check") != "ok":
            raise YulaError("SOURCE_CORRUPT", "Local SQLite source failed its integrity check.")
    return snapshot


def normalize_catalog(data):
    if not isinstance(data, dict) or data.get("formatVersion") != "1" or not isinstance(data.get("objectReleaseInfo"), list):
        raise YulaError("CATALOG_FORMAT", "Expected SAP objectReleaseInfo formatVersion 1.")
    entries = data["objectReleaseInfo"]
    if not 1 <= len(entries) <= 200000:
        raise YulaError("CATALOG_SIZE", "Invalid catalog entry count.")
    result = []
    seen = set()
    for entry in entries:
        for key in ("tadirObject", "tadirObjName", "objectType", "objectKey", "softwareComponent", "applicationComponent", "state"):
            if not isinstance(entry.get(key), str) or not 1 <= len(entry[key]) <= 512:
                raise YulaError("CATALOG_ENTRY", "Invalid required catalog field.", field=key)
        identity = (entry["objectType"].upper(), entry["objectKey"].upper())
        if identity in seen or entry["state"] not in {"released", "deprecated", "notToBeReleased"}:
            raise YulaError("CATALOG_IDENTITY", "Duplicate identity or unknown release state.")
        seen.add(identity)
        successors = entry.get("successors", [])
        if not isinstance(successors, list) or len(successors) > 100:
            raise YulaError("CATALOG_SUCCESSOR", "Invalid successor list.")
        normalized_successors = []
        for successor in successors:
            if not isinstance(successor, dict) or not all(isinstance(successor.get(k), str) and 1 <= len(successor[k]) <= 512 for k in ("objectType", "objectKey", "tadirObject")):
                raise YulaError("CATALOG_SUCCESSOR", "Invalid successor identity.")
            normalized_successors.append({"objectType": successor["objectType"], "objectKey": successor["objectKey"], "tadirType": successor["tadirObject"]})
        result.append({"object_type": identity[0], "object_name": identity[1], "tadir_type": entry["tadirObject"],
            "container": entry["tadirObjName"] if entry["tadirObjName"] != entry["objectKey"] else None,
            "software_component": entry["softwareComponent"], "application_component": entry["applicationComponent"],
            "release_state": entry["state"], "successor_json": encode({"classification": entry.get("successorClassification", ""),
                "successors": normalized_successors, **({"concept": entry["successorConceptName"]} if entry.get("successorConceptName") else {})}).decode()})
    return result


class ExtractText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag in ("p", "div", "br", "li", "tr", "h1", "h2", "h3", "pre"):
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
        if tag in ("p", "div", "li", "tr", "h1", "h2", "h3", "pre"):
            self.parts.append("\n")
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)
    def text(self):
        return re.sub(r"\n{3,}", "\n\n", "".join(self.parts)).strip()


def help_topic(fetcher, spec):
    def help_json(url, **options):
        envelope, metadata = fetcher.json(url, **options)
        if not isinstance(envelope, dict) or envelope.get("status") != "OK" or not isinstance(envelope.get("data"), dict):
            raise YulaError("HELP_FORMAT", "SAP Help returned an unsupported response envelope.")
        return envelope["data"], metadata
    url = spec["url"]
    parsed = urllib.parse.urlsplit(url)
    parts = [x for x in parsed.path.split("/") if x]
    if parsed.scheme != "https" or parsed.netloc != "help.sap.com" or len(parts) != 4 or parts[0] != "docs":
        raise YulaError("HELP_URL", "Use a complete SAP Help /docs/product/deliverable/topic URL.")
    query = urllib.parse.parse_qs(parsed.query)
    args = dict(product_url=parts[1], deliverable_url=parts[2], topic_url=parts[3],
                version=query.get("version", ["LATEST"])[0], language=query.get("locale", ["en-US"])[0],
                state=query.get("state", ["PRODUCTION"])[0])
    meta, retrieval = help_json("https://help.sap.com/http.svc/deliverableMetadata?" + urllib.parse.urlencode(args))
    if not isinstance(meta.get("deliverable"), dict) or not meta.get("filePath"):
        raise YulaError("HELP_FORMAT", "SAP Help metadata has an unsupported shape.")
    d = meta["deliverable"]
    doc_id = str(meta.get("deliverableLoio") or d["id"])
    base = {"deliverableInfo": 1, "deliverable_id": d["id"], "buildNo": d["buildNo"], "file_path": meta["filePath"]}
    first, _ = help_json("https://help.sap.com/http.svc/pagecontent?" + urllib.parse.urlencode(base), immutable=True)
    details = first.get("deliverable", {})
    title = details.get("title") or parts[2]
    tasks = [(meta["filePath"], title, [])]
    mode = spec.get("mode", "topic")
    if mode not in {"topic", "document"}:
        raise YulaError("HELP_MODE", "SAP Help mode must be topic or document.")
    if mode == "document":
        tasks = []
        def walk(nodes, parents):
            if len(parents) > 50:
                raise YulaError("HELP_TOC", "TOC nesting exceeds the adapter bound.")
            for node in nodes:
                label = str(node.get("t") or "")
                if node.get("u"):
                    tasks.append((node["u"], label, parents))
                walk(node.get("c") or [], parents + [label])
        walk(details.get("fullToc") or [], [])
        if not tasks:
            raise YulaError("HELP_TOC", "Document mode requires a nonempty TOC.")
    tasks = list({t[0]: t for t in tasks}.values())
    if len(tasks) > int(spec.get("maxTopics", 5000)):
        raise YulaError("HELP_LIMIT", "The complete TOC exceeds maxTopics; no partial document is published.")
    topics = []
    for file_path, task_title, parents in tasks:
        if file_path == meta["filePath"]:
            page = first
        else:
            params = {**base, "deliverableInfo": 0, "file_path": file_path}
            page, _ = help_json("https://help.sap.com/http.svc/pagecontent?" + urllib.parse.urlencode(params), immutable=True)
        body = page.get("body")
        if not isinstance(body, str):
            raise YulaError("HELP_CONTENT", "Missing page body; the previous corpus is preserved.")
        extract = ExtractText(); extract.feed(body)
        text = extract.text()
        if len(text.encode()) > 4 * 1024 * 1024:
            raise YulaError("HELP_CONTENT", "Topic text exceeds the adapter bound.")
        current = page.get("currentPage") or {}
        tid = str(current.get("loio") or file_path.removesuffix(".html"))
        topic_url = "https://help.sap.com/docs/" + "/".join(parts[1:3] + [tid]) + "?" + urllib.parse.urlencode({"version": args["version"], "locale": args["language"]})
        topics.append({"document_id": doc_id, "topic_id": tid, "topic_title": current.get("t") or task_title,
                       "text": text, "url": url if mode == "topic" else topic_url, "breadcrumb": " > ".join(parents)})
    document = {"document_id": doc_id, "title": title, "root_url": url,
                "scope": "Public Edition" if parts[1].upper() == "SAP_S4HANA_CLOUD" else "Cross-product ABAP documentation",
                "version": str(d.get("version") or args["version"]), "language": str(d.get("language") or args["language"])}
    scope_markers=(url+' '+document['version']+' '+str(d.get('product',''))+' '+str(d.get('productName',''))).lower()
    if any(x in scope_markers for x in ('pce','private','on-premise','on_premise')):
        document["scope"] = "Private Edition (reference only)"
    payload = {"document": document, "topics": topics, "mode": mode, "build": str(d["buildNo"])}
    return payload, digest(payload), {"url": url, "mode": mode, "build": str(d["buildNo"]), "topics": len(topics),
                                     'fetchedAt':retrieval.get('checkedAt') or retrieval.get('fetchedAt') or now()}


def adt_metadata(fetcher, spec, db):
    import os
    origin = (os.environ.get(spec["originEnv"], "") if spec.get("originEnv") else spec.get("origin", "")).rstrip("/")
    p = urllib.parse.urlsplit(origin)
    if p.scheme != "https" or p.path or p.query or p.fragment or p.username:
        raise YulaError("SAP_ORIGIN", "Configure an HTTPS SAP origin without a path or credentials.")
    objects = spec.get("objects", [])
    if not 1 <= len(objects) <= 100:
        raise YulaError("SAP_OBJECT_LIMIT", "Specify 1..100 exact released identities.")
    routes = {"CLAS": "oo/classes", "INTF": "oo/interfaces"}
    result = []
    for obj in objects:
        typ, name = str(obj.get("objectType", "")).upper(), str(obj.get("objectName", "")).upper()
        if typ not in routes:
            raise YulaError("SAP_ADAPTER_UNSUPPORTED", "Native metadata refresh supports CLAS and INTF; use a reviewed object export for other types.", objectType=typ)
        if not re.fullmatch(r"[A-Z0-9_/]{1,128}", name):
            raise YulaError("SAP_IDENTITY", "Invalid object identity.")
        if scalar(db, "select release_state from released_catalog where edition='s4hc-latest' and object_type=? and object_name=?", (typ, name)) != "released":
            raise YulaError("OBJECT_NOT_RELEASED", "Catalog gate rejected the requested SAP identity.", objectType=typ, objectName=name)
        # Read the repository metadata shell only. No /source/main or object discovery.
        url = origin + "/sap/bc/adt/" + routes[typ] + "/" + urllib.parse.quote(name.lower(), safe="")
        payload, _ = fetcher.get(url, max_bytes=2 * 1024 * 1024, auth_env=spec.get("authorizationEnv"), origin=origin, use_cache=False)
        if b"<!DOCTYPE" in payload.upper() or b"<!ENTITY" in payload.upper():
            raise YulaError("XML_UNSAFE", "DTD/entity declarations are not accepted.")
        try:
            element = ET.fromstring(payload)
        except ET.ParseError:
            raise YulaError("SAP_RESPONSE", "Expected ADT metadata XML, not a login page.") from None
        attrs = {k.rsplit("}", 1)[-1]: v for k, v in element.attrib.items()}
        if str(attrs.get("name", "")).upper() != name:
            raise YulaError("SAP_IDENTITY_MISMATCH", "ADT metadata did not match the exact requested object.")
        result.append({"objectType": typ, "objectName": name, "description": attrs.get("description", ""),
                       "language": attrs.get("language"), "sourceSha256": digest(payload),
                       "observation": "metadata_only", "signatureRefresh": False})
    return result, digest(result), {"objects": len(result), "signatureRefresh": False, "origin": "sap-system://configured"}


def prepare(spec, base, stage, fetcher, db):
    kind = spec["kind"]
    if kind == "released-catalog":
        url = spec.get("url", RELEASE_URL)
        if url != RELEASE_URL:
            raise YulaError("CATALOG_AUTHORITY", "The Public Edition gate uses SAP's exact official latest catalog URL.")
        raw, meta = fetcher.get(url)
        try:
            data = json.loads(raw)
        except ValueError:
            raise YulaError("CATALOG_FORMAT", "Invalid catalog JSON.") from None
        return normalize_catalog(data), digest(raw), {"url": url, "fetchedAt": meta.get("checkedAt") or meta["fetchedAt"], "entries": len(data["objectReleaseInfo"])}
    if kind == "sap-help":
        return help_topic(fetcher, spec)
    if kind == "sap-adt-metadata":
        return adt_metadata(fetcher, spec, db)
    if kind in {"legacy-objects", "configuration-db"}:
        path = source_path(spec, base)
        snapshot = local_snapshot(path, stage)
        with connect(snapshot) as src:
            table = "objects" if kind == "legacy-objects" else "activities"
            if not scalar(src, f"select count(*) from {table}"):
                raise YulaError("SOURCE_EMPTY", "Source database is empty.")
            # Logical digest avoids false changes caused by SQLite file layout or WAL checkpoints.
            import hashlib
            h = hashlib.sha256()
            tables = (*OBJECT_TABLES,'corpus_ingestion') if kind == "legacy-objects" else CONFIG_TABLES
            for name in tables:
                h.update(name.encode())
                for row in src.execute('select * from "' + name + '" order by rowid'):
                    h.update(encode([{"blobSha256": digest(v)} if isinstance(v, bytes) else v for v in row]))
        return {"path": str(snapshot)}, h.hexdigest(), {"format": kind, "source": "local-source://" + spec["id"]}
    if kind == "configuration-root":
        root = source_path(spec, base)
        files = sorted(p for p in (root / "data/releases").rglob("*") if p.is_file() and p.suffix in {".json", ".jsonl", ".md"} and "indexes" not in p.parts)
        if not files:
            raise YulaError("SOURCE_EMPTY", "No canonical configuration release files were found.")
        fingerprint = digest([(p.relative_to(root).as_posix(), file_hash(p)) for p in files])
        target = Path(stage) / (spec["id"] + "-config")
        # Copy only canonical content; never let the legacy indexer touch the original source.
        for p in files:
            dest = target / p.relative_to(root); dest.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, dest)
        from .vendor import sca
        sca.build_index(target)
        return {"path": str(target / "data/knowledge.sqlite3"), "root": str(target)}, fingerprint, {"format": kind, "files": len(files)}
    if kind == "configuration-workbook":
        release = spec.get("release")
        if not isinstance(release, str) or not re.fullmatch(r"\d{4}", release):
            raise YulaError("RELEASE_REQUIRED", "Workbook sources require an explicit four-digit release.")
        if spec.get("url"):
            raw, _ = fetcher.get(spec["url"], max_bytes=32 * 1024 * 1024)
            book = Path(stage) / (spec["id"] + ".xlsm"); book.write_bytes(raw)
        else:
            book = source_path(spec, base)
            if book.stat().st_size > 32 * 1024 * 1024:
                raise YulaError("WORKBOOK_SIZE", "Workbook exceeds the compressed size bound.")
            raw = book.read_bytes()
        # Standard-library XML/ZIP importer; macros are never executed.
        import zipfile
        with zipfile.ZipFile(book) as z:
            if sum(i.file_size for i in z.infolist()) > 256 * 1024 * 1024:
                raise YulaError("WORKBOOK_SIZE", "Expanded workbook exceeds the bound.")
        target = Path(stage) / (spec["id"] + "-config")
        from .vendor import sca
        sca.command_import_catalog(argparse.Namespace(root=str(target), release=release, xlsm=str(book)))
        sca.build_index(target)
        return {"path": str(target / "data/knowledge.sqlite3"), "release": release}, digest({"sha256": digest(raw), "release": release}), {"release": release, "format": "SAP SSCUI XLSM", "workbookSha256": digest(raw)}
    if kind == "knowledge-records":
        path = source_path(spec, base)
        if path.stat().st_size > 8 * 1024 * 1024:
            raise YulaError("RECORD_SIZE", "Knowledge record file exceeds the bound.")
        data = load_json(path)
        if not isinstance(data, list) or not 1 <= len(data) <= 1000:
            raise YulaError("RECORD_FORMAT", "Expected 1..1000 records in a JSON array.")
        from .records import validate_record
        data = [validate_record(r) for r in data]
        return data, digest(data), {"records": len(data), "format": "yula-knowledge-records/1"}
    raise YulaError("ADAPTER_UNKNOWN", "Unsupported source adapter.", kind=kind)


def apply_catalog(db, payload, sha, fetched):
    old = {(r["object_type"], r["object_name"]): r for r in rows(db, "select * from released_catalog where edition='s4hc-latest'")}
    keys = set(); changed = []; added = 0
    for item in payload:
        key = (item["object_type"], item["object_name"]); keys.add(key)
        previous = old.get(key)
        if previous is None:
            added += 1
        else:
            fields = [k for k, v in item.items() if ((json.loads(previous[k]) != json.loads(v)) if k == "successor_json" else previous[k] != v)]
            if fields:
                changed.append({"objectType": key[0], "objectName": key[1], "before": previous["release_state"], "after": item["release_state"], "fields": fields})
        db.execute("""insert into released_catalog values ('s4hc-latest',?,?,?,?,?,?,?,?,?,?)
            on conflict(edition,object_type,object_name) do update set tadir_type=excluded.tadir_type,
            container=excluded.container,software_component=excluded.software_component,application_component=excluded.application_component,
            release_state=excluded.release_state,successor_json=excluded.successor_json,index_sha256=excluded.index_sha256,index_fetched_at=excluded.index_fetched_at""",
            tuple(item[k] for k in ("object_type", "object_name", "tadir_type", "container", "software_component", "application_component", "release_state", "successor_json")) + (sha, fetched))
    removed = sorted(set(old) - keys)
    for typ, name in removed:
        db.execute("update released_catalog set release_state='notListed',index_sha256=?,index_fetched_at=? where edition='s4hc-latest' and object_type=? and object_name=?", (sha, fetched, typ, name))
    db.execute("insert or replace into corpus_snapshots values ('s4hc-latest',?,?,?,?,?)",
               (sha, fetched, len(payload), sum(x["release_state"] == "released" for x in payload), now()))
    return {"added": added, "changed": len(changed), "removed": len(removed), "sample": changed[:5], "historyPreserved": True}


def copy_rows(source, target, source_table, target_table, release=None):
    columns = [r[1] for r in target.execute('pragma table_info("' + target_table + '")')]
    source_columns = {r[1] for r in source.execute('pragma table_info("' + source_table + '")')}
    if not set(columns) <= source_columns:
        raise YulaError("SOURCE_SCHEMA", "Local database schema is incompatible.", table=source_table)
    sql = 'select ' + ','.join('"' + c + '"' for c in columns) + ' from "' + source_table + '"'
    params = ()
    if release:
        sql += " where release=?"; params = (release,)
    insert = 'insert into "' + target_table + '" (' + ','.join('"' + c + '"' for c in columns) + ') values (' + ','.join('?' for _ in columns) + ')'
    count = 0
    for row in source.execute(sql, params):
        values = list(row)
        for i, column in enumerate(columns):
            if column in {"target_system", "target_host", "target_client", "tenant_role"}:
                values[i] = None
            elif isinstance(values[i], str) and column not in {'public_api','signature'}:
                values[i] = sanitize(values[i])
        target.execute(insert, values); count += 1
    return count


def apply_help(db, payload, source_id=None, fetched_at=None):
    from .migrations import ensure_extensions
    ensure_extensions(db)
    d=dict(payload['document']);doc_id=d['document_id']
    previous=rows(db,'select version,language from doc_documents where document_id=?',(doc_id,))
    if previous and (previous[0]['version'],previous[0]['language'])!=(d['version'],d['language']):
        # Reuse an existing version/language partition; never relabel untouched content.
        legacy=doc_id+'-'+digest(d['version'].encode())[:12]
        old=rows(db,'select document_id from doc_documents where document_id=? and version=? and language=?',(legacy,d['version'],d['language']))
        doc_id=old[0]['document_id'] if old else doc_id+'-'+digest([d['version'],d['language']])[:12]
    d['document_id']=doc_id
    db.execute("""insert into doc_documents values (?,?,?,?,?,?,0) on conflict(document_id) do update set
        title=excluded.title,root_url=excluded.root_url,scope=excluded.scope,version=excluded.version,language=excluded.language""",
        tuple(d[k] for k in ('document_id','title','root_url','scope','version','language')))
    if payload['mode']=='document':
        db.execute('delete from doc_topic_evidence where document_id=?',(doc_id,))
        db.execute('delete from doc_chunks where document_id=?',(doc_id,))
    seen=set()
    for topic in payload['topics']:
        tid=topic['topic_id']
        if tid in seen:raise YulaError('TOPIC_DUPLICATE','Duplicate topic identity in a source snapshot.')
        seen.add(tid)
        db.execute('delete from doc_chunks where document_id=? and topic_id=?',(doc_id,tid))
        db.execute('delete from doc_topic_evidence where document_id=? and topic_id=?',(doc_id,tid))
        text=topic['text']
        for i,start in enumerate(range(0,len(text),6000)):
            db.execute('insert into doc_chunks values (?,?,?,?,?,?,?,?,?,?)',(
                tid+':'+str(i),doc_id,d['title'],tid,topic['topic_title'],topic['breadcrumb'],topic['url'],d['root_url'],d['scope'],text[start:start+6000]))
        if text:
            db.execute('insert into doc_topic_evidence values (?,?,?,?,?,?,?,?)',
                (doc_id,tid,source_id,fetched_at,payload.get('build'),'', 'source_text',digest(text.encode())))
    topics=scalar(db,'select count(distinct topic_id) from doc_chunks where document_id=?',(doc_id,))
    db.execute('update doc_documents set topics=? where document_id=?',(topics,doc_id))
    return {'topicsRefreshed':len(payload['topics']),'documentTopics':topics,'mode':payload['mode'],'documentId':doc_id}


def apply_configuration(db, payload, kind):
    with connect(payload["path"]) as source:
        releases = [r[0] for r in source.execute("select distinct release from activities")]
        tables = CONFIG_TABLES if kind != "configuration-workbook" else ("activities", "access_map", "expert_config", "documents", "documents_fts")
        counts = {}
        for release in releases:
            old = {r["activity_id"]: r["json"] for r in rows(db, "select activity_id,json from cfg_activities where release=?", (release,))}
            new = {r["activity_id"]: r["json"] for r in rows(source, "select activity_id,json from activities where release=?", (release,))}
            affected = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
            for table in tables:
                if table == "metadata":
                    continue
                if table in {"documents", "documents_fts"} and kind == "configuration-workbook":
                    db.execute(f"delete from cfg_{table} where release=? and doc_type in ('catalog_activity','access_map','expert_configuration')", (release,))
                else:
                    db.execute(f"delete from cfg_{table} where release=?", (release,))
                counts[table] = copy_rows(source, db, table, "cfg_" + table, release)
            for aid in affected:
                db.execute("insert or replace into yula_review_flags values (?,?,?,?)", (release, aid, "catalog_changed", now()))
            counts["reviewRequired"] = len(affected)
        if payload.get("root"):
            for release in releases:
                db.execute('delete from cfg_profiles where release=?',(release,))
                db.execute('delete from cfg_sources where release=?',(release,))
            import_config_details(db, Path(payload["root"]))
        # Canonical source imports cannot discard locally curated immutable revisions.
        from .records import apply_records
        latest = rows(db, """select r.json from yula_records r where r.revision=(select max(x.revision)
            from yula_records x where x.kind=r.kind and x.id=r.id and x.release=r.release)""")
        apply_records(db, [json.loads(r["json"]) for r in latest if json.loads(r["json"])["release"] in releases], reproject=True)
        return {"releases": releases, "counts": counts}


def import_config_details(db, root):
    for release_dir in sorted((root / "data/releases").iterdir()):
        if not release_dir.is_dir():
            continue
        release = release_dir.name
        for p in (release_dir / "knowledge/activities").glob("*/profile.json"):
            profile = sanitize(load_json(p))
            db.execute("insert or replace into cfg_profiles values (?,?,?)", (release, p.parent.name, encode(profile).decode()))
        for p in sorted(release_dir.rglob("*.jsonl")):
            if p.name not in {"sources.jsonl", "source-registry.jsonl"}:
                continue
            aid = p.parent.name if p.name == "sources.jsonl" else ""
            for line in p.read_text(encoding="utf-8-sig").splitlines():
                if not line.strip():
                    continue
                source = sanitize(json.loads(line)); sid = source.get("source_id")
                if sid:
                    db.execute("insert or replace into cfg_sources values (?,?,?,?)", (release, aid, sid, encode(source).decode()))


def apply_prepared(db, spec, payload, fingerprint, details):
    kind = spec["kind"]
    if kind == "released-catalog":
        result = apply_catalog(db, payload, fingerprint, details["fetchedAt"])
    elif kind == "sap-help":
        result = apply_help(db, payload, spec['id'], details.get('fetchedAt') or now())
    elif kind in {"configuration-db", "configuration-root", "configuration-workbook"}:
        result = apply_configuration(db, payload, kind)
    elif kind == "legacy-objects":
        with connect(payload["path"]) as source:
            invalid = 0
            for typ, name in source.execute("select object_type,object_name from objects"):
                if scalar(db, "select count(*) from released_catalog where edition='s4hc-latest' and object_type=? and object_name=?", (typ, name)) != 1:
                    invalid += 1
            if invalid:
                raise YulaError("SOURCE_IDENTITY", "Local object corpus contains identities absent from the official catalog.", rejected=invalid)
            # Replace only this adapter's object-domain tables; configuration, docs, current catalog and records stay intact.
            for table in reversed(OBJECT_TABLES):
                db.execute('delete from "' + table + '"')
            for table in OBJECT_TABLES:
                copy_rows(source, db, table, table)
            for receipt in rows(source, "select * from corpus_ingestion where edition='s4hc-latest'"):
                if scalar(db, "select count(*) from released_catalog where edition=? and object_type=? and object_name=?", (receipt["edition"], receipt["object_type"], receipt["object_name"])):
                    cols = list(receipt)
                    db.execute('insert or replace into corpus_ingestion (' + ','.join(cols) + ') values (' + ','.join('?' for _ in cols) + ')', list(receipt.values()))
            import gzip, io
            for row in db.execute("select object_id,content_kind,encoding,source_sha256,content_chars,content_bytes,content_blob from object_content"):
                item = dict(row)
                if item["encoding"] not in {"gzip", "gzip-utf8"}:
                    raise YulaError("CONTENT_ENCODING", "Unsupported compressed public-content format.")
                with gzip.GzipFile(fileobj=io.BytesIO(item["content_blob"])) as stream:
                    raw = stream.read(16 * 1024 * 1024 + 1)
                if len(raw) != item["content_bytes"] or len(raw) > 16 * 1024 * 1024 or digest(raw) != item["source_sha256"]:
                    raise YulaError("CONTENT_CORRUPT", "Imported public content failed its hash/size gate.")
                text = raw.decode("utf-8")
                if len(text) != item["content_chars"]:
                    raise YulaError("CONTENT_CORRUPT", "Imported public content failed its character-count gate.")
                if item["content_kind"] in {"abap-class-public-definition", "abap-interface-public-declaration"}:
                    if re.search(r"(?im)^\s*(?:METHOD\s|CLASS\s+\S+\s+IMPLEMENTATION\b|PRIVATE\s+SECTION\b|PROTECTED\s+SECTION\b)", text):
                        raise YulaError("NONPUBLIC_CONTENT", "Incoming class/interface content contains an implementation or nonpublic section.")
            result = {"objects": scalar(db, "select count(*) from objects")}
    elif kind == "sap-adt-metadata":
        for obj in payload:
            db.execute("insert or replace into yula_observations values (?,?,?,?,?,?)", (
                spec["id"], obj["objectType"], obj["objectName"], obj["sourceSha256"], now(), encode(obj).decode()))
        result = {"observations": len(payload), "signaturesRefreshed": False}
    elif kind == "knowledge-records":
        from .records import apply_records
        result = apply_records(db, payload)
    else:
        raise YulaError("ADAPTER_UNKNOWN", "Unsupported prepared adapter.")
    db.execute("insert or replace into yula_sources values (?,?,?,?,?,?)", (
        spec["id"], kind, fingerprint, details.get("fetchedAt", now()), now(), encode(sanitize(details)).decode()))
    return result
