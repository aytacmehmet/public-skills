from __future__ import annotations

import json
import shutil
import sqlite3
import uuid
from pathlib import Path

from . import adapters
from .common import (PLUGIN, YulaError, atomic_json, connect, digest, encode, file_hash,
                     load_json, now, safe_id, scalar, validate_database)
from .network import Fetcher
from .snapshots import active, clone_database


def load_sources(config=None, selected=None):
    config = Path(config).resolve() if config else PLUGIN / "config/sources.json"
    data = load_json(config)
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("sources"), list):
        raise YulaError("SOURCE_CONFIG", "Expected a version 1 sources configuration.")
    sources = data["sources"]
    ids = [safe_id(s.get("id")) for s in sources]
    if len(set(ids)) != len(ids):
        raise YulaError("SOURCE_CONFIG", "Source IDs must be unique.")
    if selected:
        missing = set(selected) - set(ids)
        if missing:
            raise YulaError("SOURCE_UNKNOWN", "Requested sources are not configured.", missing=sorted(missing))
        sources = [s for s in sources if s["id"] in selected]
    else:
        sources = [s for s in sources if s.get("enabled", False)]
    if not sources:
        raise YulaError("NO_SOURCES", "No update source was selected.")
    # The current official catalog is established before any exact-object system read.
    sources.sort(key=lambda s: (s["kind"] != "released-catalog", s["id"]))
    return sources, config.parent


def check(root, config=None, selected=None, fetcher=None):
    sources, base = load_sources(config, selected)
    state, source = active(root)
    if file_hash(source) != state["sha256"]:
        raise YulaError("SNAPSHOT_CORRUPT", "The active snapshot changed outside the maintenance protocol.")
    stage = Path(root) / "plans" / uuid.uuid4().hex
    stage.mkdir(parents=True)
    candidate = stage / "candidate.sqlite"
    fetcher = fetcher or Fetcher(Path(root) / "http-cache")
    results = []
    candidate_db = None
    try:
        for spec in sources:
            inspect_path = candidate if candidate.exists() else source
            with connect(inspect_path) as inspection:
                payload, fingerprint, details = adapters.prepare(spec, base, stage, fetcher, inspection)
                previous = scalar(inspection, "select fingerprint from yula_sources where id=?", (spec["id"],))
            config_hash = digest({k: v for k, v in spec.items() if k != "enabled"})
            # Corpus fingerprint carries content; plan also binds source configuration.
            unchanged = fingerprint == previous
            result = {"source": spec["id"], "kind": spec["kind"], "fingerprint": fingerprint,
                      "configurationSha256": config_hash, "changed": not unchanged}
            if not unchanged:
                if not candidate.exists():
                    clone_database(source, candidate)
                candidate_db = connect(candidate, readonly=False)
                try:
                    with candidate_db:
                        from .migrations import ensure_extensions
                        ensure_extensions(candidate_db)
                        result["diff"] = adapters.apply_prepared(candidate_db, spec, payload, fingerprint, details)
                finally:
                    candidate_db.close(); candidate_db = None
            atomic_json(Path(root) / "checks" / (spec["id"] + ".json"), {
                "fingerprint": fingerprint, "checkedAt": now(), "configurationSha256": config_hash})
            results.append(result)
        changed = candidate.exists()
        if changed:
            # An older seed or changed adapter must satisfy the same stable read schema before publication.
            validate_database(candidate)
            candidate_sha = file_hash(candidate)
        else:
            candidate_sha = state["sha256"]
        plan = {"format": "yula-update-plan/1", "createdAt": now(), "baseSha256": state["sha256"],
                "baseGeneration": state["generation"], "candidateSha256": candidate_sha,
                "changed": changed, "sources": results}
        plan_path = stage / "plan.json"
        atomic_json(plan_path, plan)
        return {"status": "update_available" if changed else "current", "plan": str(plan_path),
                "planSha256": digest(plan), "baseSha256": state["sha256"], "changed": changed, "sources": results}
    except BaseException:
        if candidate_db is not None:
            candidate_db.close()
        # Partial stages never have a plan/commit marker; HTTP topic checkpoints remain reusable.
        candidate.unlink(missing_ok=True)
        raise
