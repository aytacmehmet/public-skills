"""Additive storage revision, staged and published by the normal hash-bound protocol."""
from __future__ import annotations
import uuid
from pathlib import Path
import json
from .common import PLUGIN, atomic_json, connect, digest, file_hash, has_table, now, rows, validate_database
from .snapshots import active, clone_database


def ensure_extensions(db):
    # Execute statements individually: executescript would commit the caller's transaction.
    sql = (PLUGIN / 'data/schema-revision-2.sql').read_text(encoding='utf-8')
    for statement in sql.split(';'):
        if statement.strip():
            db.execute(statement)
    missing = rows(db, """select c.document_id,c.topic_id from doc_chunks c left join doc_topic_evidence e
        on e.document_id=c.document_id and e.topic_id=c.topic_id where e.topic_id is null
        group by c.document_id,c.topic_id""")
    import itertools
    needed = {(x['document_id'],x['topic_id']) for x in missing}
    known_sources=[(r,json.loads(r['details_json'])) for r in rows(db,"select id,fetched_at,details_json from yula_sources where kind='sap-help'")]
    stream = db.execute('select document_id,topic_id,text,url,root_url from doc_chunks order by document_id,topic_id,rowid')
    for key, items in itertools.groupby(stream, key=lambda r:(r[0],r[1])):
        parts=list(items)
        if key not in needed:
            continue
        matches=[(r,d) for r,d in known_sources if (d.get('mode')=='topic' and d.get('url')==parts[0][3]) or
                  (d.get('mode')=='document' and d.get('url')==parts[0][4])]
        # Yula's prior Help adapter already used non-overlapping chunks. Imported legacy
        # indexes have no equivalent guarantee and keep an explicit legacy representation.
        chosen=max(matches,key=lambda x:x[0]['fetched_at'] or '') if matches else None
        joiner='' if chosen else '\n\n';text=joiner.join(r[2] for r in parts)
        db.execute('insert into doc_topic_evidence values (?,?,?,?,?,?,?,?)',
                   (*key,chosen[0]['id'] if chosen else None,chosen[0]['fetched_at'] if chosen else None,
                    chosen[1].get('build') if chosen else None,joiner,'source_text' if chosen else 'legacy_chunks',digest(text.encode())))
    db.execute('insert or ignore into yula_migrations values (2,?,?)', (now(),'Additive exact-name/identity indexes and per-topic provenance; base ABI 1 retained.'))


def prepare(root):
    state, source = active(root)
    with connect(source) as db:
        present = has_table(db,'doc_topic_evidence')
    stage = Path(root)/'plans'/uuid.uuid4().hex
    stage.mkdir(parents=True)
    if present:
        validate_database(source)
        candidate_sha = state['sha256']
    else:
        candidate = stage/'candidate.sqlite'
        clone_database(source,candidate)
        with connect(candidate,readonly=False) as db:
            ensure_extensions(db)
        validate_database(candidate)
        candidate_sha = file_hash(candidate)
    plan={'format':'yula-update-plan/1','createdAt':now(),'baseSha256':state['sha256'],
          'baseGeneration':state['generation'],'candidateSha256':candidate_sha,'changed':not present,
          'sources':[{'source':'storage-revision-2','kind':'migration','changed':not present}]}
    path=stage/'plan.json';atomic_json(path,plan)
    return {'status':'current' if present else 'update_available','plan':str(path),'planSha256':digest(plan),'changed':not present}
