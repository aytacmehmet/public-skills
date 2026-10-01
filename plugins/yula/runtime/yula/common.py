from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

PLUGIN = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = 1
APPLICATION_ID = 0x59554C41
RELEASE_URL = "https://raw.githubusercontent.com/SAP/abap-atc-cr-cv-s4hc/main/src/objectReleaseInfoLatest.json"


class YulaError(Exception):
    def __init__(self, code: str, message: str, **details):
        super().__init__(message)
        self.code, self.message, self.details = code, message, details

    def result(self):
        return {"error": self.code, "message": self.message, **self.details}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def age_days(value):
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            return None
        seconds = (datetime.now(timezone.utc) - stamp).total_seconds()
        return None if seconds < -300 else max(0, seconds / 86400)
    except (ValueError, TypeError):
        return None


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else encode(value)).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def atomic_json(path, value):
    import uuid
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with tmp.open("wb") as stream:
            stream.write(encode(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        if os.name != "nt":
            fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
    finally:
        tmp.unlink(missing_ok=True)


def data_root(value=None):
    # @user/yula is an explicit portable selector used by the host MCP manifest.
    configured = os.environ.get("YULA_DATA_ROOT") if value == "@user/yula" else value or os.environ.get("YULA_DATA_ROOT")
    if configured:
        root = Path(configured).expanduser().resolve()
    elif value != "@user/yula":
        raise YulaError("DATA_ROOT_REQUIRED", "Set --data-root or YULA_DATA_ROOT; use @user/yula for the host's shared corpus.")
    elif os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local")) / "yula"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "yula"
    root = root.resolve()
    if root == PLUGIN or PLUGIN in root.parents:
        raise YulaError("DATA_ROOT_INSIDE_PLUGIN", "Choose a mutable data root outside the installed plugin.")
    return root


def safe_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,95}", value):
        raise YulaError("INVALID_ID", "Expected a bounded alphanumeric identifier.")
    return value


def require_hash(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value):
        raise YulaError("INVALID_HASH", "Expected a SHA-256 digest.")
    return value


@contextmanager
def writer_lock(root):
    """Kernel lock: process death releases it; no unsafe stale-lock deletion."""
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    stream = (root / "writer.lock").open("a+b")
    stream.seek(0, 2)
    if not stream.tell():
        stream.write(b"\0")
        stream.flush()
    stream.seek(0)
    try:
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise YulaError("WRITER_BUSY", "Another process owns the data-root write lock.") from None
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    finally:
        stream.close()


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


def connect(path, readonly=True):
    path = Path(path).resolve()
    if readonly and not path.is_file():
        raise YulaError("CORPUS_MISSING", "The selected SQLite snapshot does not exist.")
    db = sqlite3.connect(path.as_uri() + ("?mode=ro" if readonly else "?mode=rw"), uri=True, factory=ClosingConnection)
    db.row_factory = sqlite3.Row
    db.execute("pragma foreign_keys=on")
    db.execute("pragma trusted_schema=off")
    if readonly:
        db.execute("pragma query_only=on")
    return db


def rows(db, sql, parameters=()):
    return [dict(row) for row in db.execute(sql, parameters)]


def scalar(db, sql, parameters=()):
    row = db.execute(sql, parameters).fetchone()
    return row[0] if row else None


def has_table(db, name):
    return bool(scalar(db, "select 1 from sqlite_master where type='table' and name=?", (name,)))


def checked_receipt(root, source_id, fingerprint):
    """A damaged optional check receipt cannot invalidate an intact corpus."""
    try:
        record = load_json(Path(root) / "checks" / (safe_id(source_id) + ".json"))
        age = age_days(record.get("checkedAt"))
        if record.get("fingerprint") == fingerprint and age is not None:
            return {"checkedAt": record["checkedAt"], "ageDays": age}
    except (OSError, ValueError, TypeError, AttributeError, YulaError):
        pass
    return None


def official_url(url):
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and not parsed.username and not parsed.password and (
        host == "sap.com" or host.endswith(".sap.com") or
        host == "fioriappslibrary.hana.ondemand.com" or
        (host in {"github.com", "raw.githubusercontent.com"} and parsed.path.startswith("/SAP/")))


def primary_source(url):
    if not official_url(url):
        return False
    return (urlsplit(url).hostname or "").lower() not in {"community.sap.com", "blogs.sap.com", "answers.sap.com"}


def sanitize(value):
    """Strip transport/tenant identifiers while retaining public technical identities."""
    if isinstance(value, dict):
        denied = {"password", "username", "authorization", "cookie", "token", "access_token",
                  "target_host", "target_system", "target_client", "targetHost", "targetSystem",
                  "targetClient", "tenant_role", "tenantRole"}
        return {k: sanitize(v) for k, v in value.items() if k.lower() not in {x.lower() for x in denied}}
    if isinstance(value, list):
        return [sanitize(v) for v in value]
    if isinstance(value, str):
        value = re.sub(r"(?i)\b[A-Z]:[\\/][^\s\"<>]+", "local-source://redacted", value)
        def clean_url(match):
            url = match.group(0)
            p = urlsplit(url)
            if official_url(url):
                # Never retain authentication query values, even on an official host.
                from urllib.parse import parse_qsl, urlencode
                query = [(k, v) for k, v in parse_qsl(p.query) if not re.search("token|password|secret|key|auth|session", k, re.I)]
                return urlunsplit((p.scheme, p.netloc, p.path, urlencode(query), p.fragment))
            return "sap-system://redacted" + p.path
        return re.sub(r"https?://[^\s\"<>]+", clean_url, value)
    return value


def validate_database(path, full=False):
    with connect(path) as db:
        if scalar(db, "pragma application_id") != APPLICATION_ID:
            raise YulaError("WRONG_DATABASE", "This is not a Yula corpus.")
        version = scalar(db, "pragma user_version")
        if version != SCHEMA_VERSION:
            raise YulaError("SCHEMA_UNSUPPORTED", "Schema migration is required before opening this corpus.", version=version)
        check = scalar(db, "pragma integrity_check" if full else "pragma quick_check")
        if check != "ok" or db.execute("pragma foreign_key_check").fetchone():
            raise YulaError("CORPUS_CORRUPT", "SQLite integrity or referential check failed.")
        if scalar(db, "select count(*) from sqlite_master where type in ('trigger','view')"):
            raise YulaError("UNEXPECTED_SCHEMA", "Corpus snapshots must not contain triggers or views.")
        expected = load_json(PLUGIN / "data/schema-contract.json")
        for name, columns in expected.items():
            actual = [r[1] for r in db.execute('pragma table_info("' + name + '")')]
            if actual != columns:
                raise YulaError("SCHEMA_MISMATCH", "Missing or incompatible corpus table.", table=name)
        counts = {name: scalar(db, 'select count(*) from "' + name + '"') for name in
                  ("objects", "members", "released_catalog", "cfg_activities", "doc_documents", "doc_chunks")}
        if not counts["released_catalog"] or not counts["objects"] or not counts["cfg_activities"]:
            raise YulaError("CORPUS_EMPTY", "The corpus lacks one of its required knowledge domains.")
        fts_count = scalar(db, "select count(*) from object_knowledge_fts")
        missing = scalar(db, """select count(*) from object_knowledge_fts f left join objects o
            on o.object_type=substr(f.object_key,1,instr(f.object_key,':')-1)
            and o.object_name=substr(f.object_key,instr(f.object_key,':')+1) where o.id is null""")
        unique = scalar(db, "select count(distinct lower(object_key)) from object_knowledge_fts")
        if fts_count != counts["objects"] or unique != fts_count or missing:
            raise YulaError("INDEX_INCONSISTENT", "Object and FTS identities are not one-to-one.")
        if scalar(db, """select count(*) from cfg_documents_fts f left join cfg_documents d on d.doc_id=f.doc_id
            where d.doc_id is null""") or scalar(db, "select count(distinct doc_id) from cfg_documents_fts") != scalar(db, "select count(*) from cfg_documents") or scalar(db, "select count(*) from cfg_documents_fts") != scalar(db, "select count(*) from cfg_documents"):
            raise YulaError("INDEX_INCONSISTENT", "Configuration documents and FTS coverage differ.")
        for s in rows(db, "select edition,entry_count,released_count from corpus_snapshots"):
            active_count = scalar(db, "select count(*) from released_catalog where edition=? and release_state!='notListed'", (s["edition"],))
            released_count = scalar(db, "select count(*) from released_catalog where edition=? and release_state='released'", (s["edition"],))
            if (active_count, released_count) != (s["entry_count"], s["released_count"]):
                raise YulaError("CATALOG_COUNTS", "Catalog coverage does not match its snapshot metadata.")
        for table, key in (("cfg_changes", "entry_id"), ("cfg_dependencies", "edge_id"), ("cfg_lessons", "lesson_id"), ("cfg_incidents", "incident_id")):
            if db.execute(f"select 1 from {table} group by release,{key} having count(*)>1 limit 1").fetchone():
                raise YulaError("DUPLICATE_IDENTITY", "Conflicting projection identities.", table=table)
        if has_table(db, "doc_topic_evidence"):
            columns=[r[1] for r in db.execute('pragma table_info(doc_topic_evidence)')]
            if columns!=['document_id','topic_id','source_id','fetched_at','build','joiner','representation','text_sha256']:
                raise YulaError('SCHEMA_MISMATCH','Invalid documentation evidence extension.')
            if db.execute("""select 1 from (select document_id,topic_id from doc_topic_evidence
                except select document_id,topic_id from doc_chunks) limit 1""").fetchone():
                raise YulaError("TOPIC_EVIDENCE_ORPHAN", "Documentation provenance references a missing topic.")
        return counts
