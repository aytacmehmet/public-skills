from __future__ import annotations

import os
import shutil
import sqlite3
import uuid
from pathlib import Path

from . import VERSION

from .common import (PLUGIN, APPLICATION_ID, SCHEMA_VERSION, YulaError, atomic_json, connect, digest, encode, file_hash,
                     load_json, now, require_hash, rows, validate_database, writer_lock, checked_receipt, has_table)


def active(root, initialize=True):
    marker = Path(root) / "current.json"
    if not marker.exists():
        if not initialize:
            raise YulaError("NOT_INITIALIZED", "Initialize the data root from the packaged seed.")
        init(root)
    state = load_json(marker)
    sha = require_hash(state.get("sha256"))
    path = Path(root) / "snapshots" / (sha + ".sqlite")
    if not path.is_file():
        raise YulaError("CORPUS_MISSING", "The active snapshot is missing; use a verified backup or seed.")
    with connect(path) as db:
        if db.execute("pragma application_id").fetchone()[0] != APPLICATION_ID:
            raise YulaError("WRONG_DATABASE", "Active data is not a Yula corpus.")
        if db.execute("pragma user_version").fetchone()[0] != SCHEMA_VERSION:
            raise YulaError("SCHEMA_UNSUPPORTED", "An explicit schema migration is required; active data was preserved.")
    return state, path


def select_snapshot(root, sha=None):
    if sha is None:
        return active(root)
    path = Path(root) / 'snapshots' / (require_hash(sha) + '.sqlite')
    if not path.is_file():
        raise YulaError('SNAPSHOT_MISSING', 'Requested snapshot is unavailable; restart retrieval on the current snapshot.')
    # Published snapshots are immutable. Maintenance verifies hashes; reads validate the header.
    with connect(path) as db:
        if db.execute('pragma application_id').fetchone()[0] != APPLICATION_ID or db.execute('pragma user_version').fetchone()[0] != SCHEMA_VERSION:
            raise YulaError('SCHEMA_UNSUPPORTED', 'The selected snapshot is not a supported Yula corpus.')
    return {'sha256':sha}, path


def publish_file(root, source, sha):
    dest = Path(root) / "snapshots" / (require_hash(sha) + ".sqlite")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if file_hash(dest) != sha:
            raise YulaError("SNAPSHOT_CORRUPT", "An existing content-addressed snapshot failed verification.")
        return dest
    tmp = dest.with_suffix("." + uuid.uuid4().hex + ".tmp")
    try:
        with Path(source).open("rb") as src, tmp.open("xb") as out:
            shutil.copyfileobj(src, out, 1024 * 1024)
            out.flush(); os.fsync(out.fileno())
        if file_hash(tmp) != sha:
            raise YulaError("COPY_CORRUPT", "Snapshot copy does not match the planned SHA-256.")
        os.replace(tmp, dest)
        return dest
    finally:
        tmp.unlink(missing_ok=True)


def init(root):
    with writer_lock(root):
        marker = Path(root) / "current.json"
        if marker.exists():
            state, path = active(root, initialize=False)
            return {"status": "preserved", **state}
        manifest = load_json(PLUGIN / "data/manifest.json")
        from .seed import unpack_seed
        with unpack_seed(root) as seed:
            counts = validate_database(seed)
            publish_file(root, seed, manifest["sha256"])
        state = {"sha256": manifest["sha256"], "previous": None, "generation": 1, "committedAt": now(), "action": "init"}
        atomic_json(marker, state)
        return {"status": "initialized", **state, "counts": counts}


def clone_database(source, destination):
    # SQLite backup includes committed WAL state. Never copy a live database's main file alone.
    with connect(source) as src:
        dst = sqlite3.connect(destination)
        try:
            src.backup(dst)
            dst.execute("pragma journal_mode=delete")
            dst.commit()
        finally:
            dst.close()


def apply(root, plan_path, expected_hash):
    require_hash(expected_hash)
    plan_path = Path(plan_path).resolve()
    plan = load_json(plan_path)
    if digest(plan) != expected_hash:
        raise YulaError("PLAN_HASH_MISMATCH", "The supplied plan changed after check.")
    if plan.get("format") != "yula-update-plan/1":
        raise YulaError("PLAN_FORMAT", "Unsupported update plan.")
    with writer_lock(root):
        state, current_path = active(root, initialize=False)
        if file_hash(current_path) != state["sha256"]:
            raise YulaError("SNAPSHOT_CORRUPT", "Active snapshot hash differs from its identity.")
        if state.get("planSha256") == expected_hash and state["sha256"] == plan["candidateSha256"]:
            return {"status": "already_applied", "sha256": state["sha256"], "applied": False}
        if state["sha256"] != plan["baseSha256"] or state["generation"] != plan["baseGeneration"]:
            raise YulaError("STALE_PLAN", "Active data changed after check; create a new plan.")
        if not plan["changed"]:
            return {"status": "unchanged", "sha256": state["sha256"], "applied": False}
        # Plan controls only a sibling file with a fixed name; it cannot publish arbitrary paths.
        staged = plan_path.parent / "candidate.sqlite"
        sha = require_hash(plan["candidateSha256"])
        if not staged.is_file() or file_hash(staged) != sha:
            raise YulaError("CANDIDATE_CHANGED", "The staged database is missing or its hash changed.")
        counts = validate_database(staged)
        publish_file(root, staged, sha)
        # The previous immutable snapshot is the backup. The pointer is the only commit point.
        next_state = {"sha256": sha, "previous": state["sha256"], "generation": state["generation"] + 1,
                      "committedAt": now(), "action": "apply", "planSha256": expected_hash}
        atomic_json(Path(root) / "current.json", next_state)
        return {"status": "applied", **next_state, "counts": counts, "backup": state["sha256"]}


def rollback(root, expected_active, target=None):
    require_hash(expected_active)
    with writer_lock(root):
        state, path = active(root, initialize=False)
        if state["sha256"] != expected_active:
            raise YulaError("ACTIVE_CHANGED", "Active snapshot differs from the rollback expectation.")
        target = require_hash(target or state.get("previous"))
        dest = Path(root) / "snapshots" / (target + ".sqlite")
        if not dest.is_file() or file_hash(dest) != target:
            raise YulaError("BACKUP_INVALID", "Requested backup is absent or corrupt.")
        validate_database(dest)
        if target == state["sha256"]:
            return {"status": "unchanged", **state}
        result = {"sha256": target, "previous": state["sha256"], "generation": state["generation"] + 1,
                  "committedAt": now(), "action": "rollback"}
        atomic_json(Path(root) / "current.json", result)
        return {"status": "rolled_back", **result}


def status(root, verify=False):
    from .common import age_days, scalar
    state, path = active(root)
    if verify and file_hash(path) != state["sha256"]:
        raise YulaError("SNAPSHOT_CORRUPT", "Active snapshot hash differs from its marker.")
    with connect(path) as db:
        counts = {name: scalar(db, 'select count(*) from "' + name + '"') for name in
                  ("objects", "members", "released_catalog", "cfg_activities", "doc_documents", "doc_chunks")}
        sources = rows(db, "select id,kind,fingerprint,fetched_at,verified_at,details_json from yula_sources order by id")
        for source in sources:
            source["details"] = __import__("json").loads(source.pop("details_json"))
            checked = checked_receipt(root, source['id'], source['fingerprint'])
            if checked:
                source['lastCheckedAt'] = checked['checkedAt']
            source["ageDays"] = age_days(source.get("lastCheckedAt") or source["fetched_at"])
        coverage = rows(db, "select status,count(*) count from corpus_ingestion group by status")
        coverage_current = {
            "released": scalar(db, "select count(*) from released_catalog where edition='s4hc-latest' and release_state='released'"),
            "releasedMissingContext": scalar(db, """select count(*) from released_catalog c left join objects o
                on o.object_type=c.object_type and o.object_name=c.object_name where c.edition='s4hc-latest'
                and c.release_state='released' and o.id is null"""),
            "curatedCapabilities": scalar(db, "select count(*) from capabilities"),
            "curatedRecipes": scalar(db, "select count(*) from recipes")}
        return {"version": VERSION, "snapshot": state["sha256"], "generation": state["generation"],
                "counts": counts, "enrichment": coverage, "currentCatalogCoverage": coverage_current, "sources": sources,
                "targetTenant": "unverified", "integrity": validate_database(path) if verify else "not_requested",
                "schemaVersion": 1, "storageRevision": 2 if has_table(db,'doc_topic_evidence') else 1}
