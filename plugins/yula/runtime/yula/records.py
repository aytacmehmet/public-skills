from __future__ import annotations
import json
import re

from .common import YulaError, digest, encode, now, official_url, primary_source, sanitize, scalar, age_days

KINDS = {"research", "dependency", "incident", "lesson", "whats_new"}


def string_list(value, field, max_items=100):
    if not isinstance(value,list) or len(value)>max_items or any(not isinstance(x,str) or not x.strip() or len(x)>2000 for x in value):
        raise YulaError('RECORD_FIELD','Expected a bounded list of nonempty strings.',field=field)
    return value


def validate_record(record):
    if not isinstance(record, dict) or record.get("kind") not in KINDS:
        raise YulaError("RECORD_KIND", "Use research, dependency, incident, lesson or whats_new.")
    for key in ("id", "release", "title", "status"):
        if not isinstance(record.get(key), str) or not record[key] or len(record[key]) > 500:
            raise YulaError("RECORD_FIELD", "Missing or invalid record field.", field=key)
    if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,120}", record["id"]) or not re.fullmatch(r"\d{4}", record["release"]):
        raise YulaError("RECORD_IDENTITY", "Invalid record ID or release.")
    if type(record.get("revision")) is not int or not 1 <= record["revision"] <= 100000:
        raise YulaError("RECORD_REVISION", "A positive explicit revision is required.")
    allowed = {"candidate", "researched", "reviewed", "validated", "confirmed", "stale", "contradicted", "deprecated",
               "superseded", "rejected", "observed", "diagnosed", "fix_proposed", "fix_applied", "verified", "closed", "failed", "inconclusive"}
    if record["status"] not in allowed:
        raise YulaError("RECORD_STATUS", "Unsupported evidence status.")
    sources = record.get("sources", [])
    if not isinstance(sources, list) or len(sources) > 30:
        raise YulaError("RECORD_SOURCES", "Sources must be a bounded array.")
    for source in sources:
        if not isinstance(source, dict) or not all(isinstance(source.get(k), str) and source[k] for k in ("id", "url", "checkedAt", "claim")):
            raise YulaError("RECORD_SOURCE", "Each source requires id, url, checkedAt and the supported claim.")
        if age_days(source['checkedAt']) is None:
            raise YulaError('SOURCE_TIMESTAMP','checkedAt must be a valid timezone-aware timestamp, not a future date.')
    official = any(primary_source(s["url"]) for s in sources)
    if record["kind"] in {"research", "whats_new"} and not official:
        raise YulaError("OFFICIAL_EVIDENCE_REQUIRED", "Research and release-change records need an official source.")
    verified = record["status"] in {"validated", "confirmed", "verified", "closed"}
    verification = string_list(record.get('verification',[]),'verification')
    string_list(record.get('activityIds',[]),'activityIds')
    if 'activityId' in record and (not isinstance(record['activityId'],str) or not record['activityId'].strip()):
        raise YulaError('ACTIVITY_REQUIRED','activityId must be a nonempty string.')
    if verified and not verification:
        raise YulaError("VERIFICATION_REQUIRED", "Verified states require explicit verification evidence.")
    if record["kind"] == "lesson" and verified:
        cases = string_list(record.get("successfulCases", []),'successfulCases')
        if not ((official and len(cases) >= 1) or (len(set(cases)) >= 2 and record.get("architectReviewed") is True)):
            raise YulaError("LESSON_GATE", "A validated lesson needs an official source plus a verified case, or two independent cases plus review.")
        for field in ("applicability", "rootCause", "resolution", "rollback"):
            if not record.get(field):
                raise YulaError("LESSON_FIELD", "Missing required lesson context.", field=field)
    if record["kind"] == "dependency":
        for key in ("sourceActivityId", "targetActivityId", "relation", "evidenceLevel"):
            if not isinstance(record.get(key), str) or not record[key]:
                raise YulaError("DEPENDENCY_FIELD", "Missing dependency field.", field=key)
        if record["relation"] == "required_if" and not record.get("condition"):
            raise YulaError("DEPENDENCY_CONDITION", "Conditional edges require their condition.")
        if record["status"] == "confirmed" and not official:
            raise YulaError("DEPENDENCY_EVIDENCE", "Confirmed dependency requires official evidence.")
        if record['status']=='confirmed' and record['evidenceLevel']!='confirmed':
            raise YulaError('DEPENDENCY_EVIDENCE','Confirmed status cannot carry hypothetical or inferred evidence.')
    if record["kind"] == "research" and not record.get("activityId"):
        raise YulaError("ACTIVITY_REQUIRED", "A research dossier requires an activity ID.")
    raw = encode(record).decode()
    if re.search(r'(?i)"(?:password|authorization|cookie|access_token|client_secret)"\s*:', raw):
        raise YulaError("SECRET_FIELD", "Knowledge records must not contain credential fields.")
    return sanitize(record)


def apply_records(db, records, reproject=False):
    applied = 0
    for record in records:
        kind, rid, release, revision = (record[k] for k in ("kind", "id", "release", "revision"))
        sha = digest(record)
        old = scalar(db, "select sha256 from yula_records where kind=? and id=? and release=? and revision=?", (kind, rid, release, revision))
        if old and old != sha:
            raise YulaError("IMMUTABLE_REVISION", "A stored revision cannot be overwritten; provide a new revision.", id=rid)
        if old and not reproject:
            continue
        latest = scalar(db, "select max(revision) from yula_records where kind=? and id=? and release=?", (kind, rid, release))
        if not reproject and latest is not None and revision <= latest:
            raise YulaError("REVISION_ORDER", "New records must advance the current revision.", id=rid)
        js = encode(record).decode()
        if not reproject:
            db.execute("insert into yula_records values (?,?,?,?,?,?,?)", (kind, rid, release, revision, sha, now(), js))
        activities = record.get("activityIds", [record["activityId"]] if record.get("activityId") else [])
        if kind == "dependency":
            activities = list(set(activities + [record["sourceActivityId"], record["targetActivityId"]]))
        for aid in activities:
            if not scalar(db, "select count(*) from cfg_activities where release=? and activity_id=?", (release, aid)):
                raise YulaError("ACTIVITY_MISSING", "Record refers to an activity outside the selected release catalog.", activityId=aid)
        if kind == "research":
            db.execute("insert or replace into cfg_profiles values (?,?,?)", (release, record["activityId"], js))
            # A new dossier revision owns its source links; removed links must not survive.
            db.execute('delete from cfg_sources where release=? and activity_id=?',(release,record['activityId']))
            for source in record.get("sources", []):
                db.execute("insert or replace into cfg_sources values (?,?,?,?)", (release, record["activityId"], source["id"], encode(source).decode()))
        elif kind == "dependency":
            db.execute("delete from cfg_dependencies where release=? and edge_id=?", (release, rid))
            db.execute("insert into cfg_dependencies values (?,?,?,?,?,?,?,?)", (
                release, rid, record["sourceActivityId"], record["targetActivityId"], record["relation"], record["status"], record["evidenceLevel"], js))
        elif kind == "lesson":
            db.execute("delete from cfg_lessons where release=? and lesson_id=?", (release, rid))
            db.execute("insert into cfg_lessons values (?,?,?,?,?,?)", (release, rid, record["status"], encode(activities).decode(), None, js))
        elif kind == "incident":
            db.execute("delete from cfg_incidents where release=? and incident_id=?", (release, rid))
            db.execute("insert into cfg_incidents values (?,?,?,?,?,?)", (release, rid, record["status"], encode(activities).decode(), now(), js))
        elif kind == "whats_new":
            db.execute("delete from cfg_changes where release=? and entry_id=?", (release, rid))
            db.execute("insert into cfg_changes values (?,?,?,?,?,?,?,?)", (release, rid, record["title"], record.get("changeType", "changed"),
                       encode(activities).decode(), record.get("validFrom", release), record["sources"][0]["url"], js))
            for aid in activities:
                db.execute("insert or replace into yula_review_flags values (?,?,?,?)", (release, aid, "release_change", now()))
        doc_id = "record:" + kind + ":" + release + ":" + rid
        db.execute("delete from cfg_documents where doc_id=?", (doc_id,))
        db.execute("delete from cfg_documents_fts where doc_id=?", (doc_id,))
        body = record.get("summary") or record.get("resolution") or record["title"]
        if not isinstance(body, str):
            body = encode(body).decode()
        entity = activities[0] if activities else rid
        db.execute("insert into cfg_documents values (?,?,?,?,?,?,?,?,?,?,?)", (
            doc_id, release, kind, entity, "record", record["title"], body, record["status"], "knowledge-record://" + rid, now(), js))
        db.execute("insert into cfg_documents_fts values (?,?,?,?,?,?,?,?)", (
            doc_id, release, kind, entity, "record", record["title"], body, record["status"]))
        applied += 1
    return {"recordsApplied": applied}
