from __future__ import annotations

import gzip
import hashlib
import json
import re

from .common import RELEASE_URL, YulaError, age_days, rows, scalar, has_table


def loads(value, default=None):
    return json.loads(value) if value else default


def public_identity(db, object_type, name):
    if not object_type or not name:
        raise YulaError("IDENTITY_REQUIRED", "Use the exact objectType and objectName pair.")
    result = rows(db, "select * from released_catalog where edition='s4hc-latest' and object_type=? and object_name=?",
                  (object_type.upper(), name.upper()))
    return result[0] if result else None


def released(db, objects):
    if not 1 <= len(objects) <= 100:
        raise YulaError("LIMIT", "Check 1..100 exact identities in one call.")
    snapshot = rows(db, "select * from corpus_snapshots where edition='s4hc-latest'")
    if not snapshot:
        raise YulaError("CATALOG_MISSING", "No verified Public Edition catalog is loaded.")
    age = age_days(snapshot[0]["index_fetched_at"])
    result = []
    for item in objects:
        entry = public_identity(db, item.get("objectType"), item.get("objectName"))
        state = entry["release_state"] if entry else "notListed"
        successor = loads(entry['successor_json'],{}) if entry else {}
        has_successor = bool(successor.get('successors') or successor.get('objects') or successor.get('concept')) if isinstance(successor,dict) else bool(successor)
        result.append({"objectType": item["objectType"].upper(), "objectName": item["objectName"].upper(),
                       "state": state, "eligible": state == "released",
                       "decision": "REVIEW_REQUIRED" if state == "released" else "FAIL",
                       **({"successors": successor} if has_successor else {})})
    return {"edition": "s4hc-latest", "catalog": {"url": RELEASE_URL, "sha256": snapshot[0]["index_sha256"],
            "fetchedAt": snapshot[0]["index_fetched_at"], "stale": age is None or age > 7},
            "targetTenant": "unverified", "results": result}


def fold(text):
    import unicodedata
    text = str(text).casefold().replace("ı", "i").replace("i\u0307", "i")
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def search_terms(db, query):
    if not isinstance(query, str) or not 1 <= len(query.strip()) <= 500:
        raise YulaError("QUERY_REQUIRED", "Provide 1..500 characters.")
    lowered = fold(query)
    expansions = []
    for alias in rows(db, "select term,expansion from yula_aliases order by length(term) desc,term"):
        if re.search(r"(?<!\w)" + re.escape(fold(alias["term"])) + r"(?!\w)", lowered):
            expansions.extend(loads(alias["expansion"], []))
    stop = {"the","an","to","how","what","which","with","want","can","for","do","a","i",
            "bir","bu","icin","istiyorum","nasil","hangi","nedir","ile"}
    # Keep original Unicode terms as well as curated English expansions; FTS handles diacritics.
    terms = [t for t in re.findall(r"\w+", query.casefold()) if len(t)>1 and fold(t) not in stop]
    phrases = list(dict.fromkeys(expansions + terms))[:16]
    if not phrases:
        raise YulaError("QUERY_EMPTY", "No searchable term.")
    return " OR ".join('"' + t.replace('"','""') + '"' for t in phrases)


def capabilities(db, oid, operation=None):
    sql = """select c.id,c.label_en label,c.operation,oc.member_name member,oc.evidence_level evidenceLevel
        from object_capabilities oc join capabilities c on c.id=oc.capability_id where oc.object_id=?"""
    params = [oid]
    if operation:
        sql += " and c.operation=?"; params.append(operation)
    return rows(db, sql+" order by c.id", params)


def matched_capabilities(db, oid, query, operation=None):
    intent = fold(query)
    all_caps = capabilities(db,oid,operation)
    matched = set()
    for row in rows(db, """select oc.capability_id,a.alias from object_capabilities oc
        join capability_aliases a on a.capability_id=oc.capability_id where oc.object_id=?""", (oid,)):
        alias = fold(row['alias'])
        if alias == intent or re.search(r"(?<!\w)"+re.escape(alias)+r"(?!\w)",intent):
            matched.add(row['capability_id'])
    return [c for c in all_caps if c['id'] in matched or fold(c['id'])==intent]


def validate_filters(domain, filters):
    allowed = {'objects':{'objectType','component','operation'},'catalog':{'objectType','component'},
               'configuration':{'release','scope','country','component'},
               'docs':{'release','includeOtherEditions'},'lessons':{'release'}}
    if domain not in allowed:
        raise YulaError('DOMAIN','Unknown search domain.')
    unused = [k for k,v in filters.items() if v not in (None,'',False) and k not in allowed[domain]]
    if unused:
        raise YulaError('UNSUPPORTED_FILTER','Filter is not applicable to this domain.',fields=unused,domain=domain,allowed=sorted(allowed[domain]))


def search(db, domain, query, limit=5, offset=0, **filters):
    validate_filters(domain,filters)
    limit=max(1,min(int(limit),10));offset=max(0,min(int(offset),10000))
    envelope={'domain':domain}
    if domain in ('objects','catalog'):
        params=[];where=["c.edition='s4hc-latest'"]
        if domain=='objects':where.append("c.release_state='released'")
        for key,column in (('objectType','object_type'),('component','application_component')):
            if filters.get(key):where.append('c.'+column+'=?');params.append(filters[key].upper())
        exact_where=where+["c.object_name=?"]
        exact=rows(db,"select c.object_type,c.object_name from released_catalog c where "+' and '.join(exact_where)+" order by c.object_type",params+[query.upper()])
        if domain=='objects':
            if not scalar(db,'select count(*) from objects'):
                raise YulaError('CORPUS_EMPTY','No enriched object corpus is loaded.')
            columns="o.id,o.object_type objectType,o.object_name objectName,substr(o.description,1,320) description,o.application_component component"
            join="""objects o join released_catalog c on c.object_type=o.object_type and c.object_name=o.object_name"""
            if exact:
                result=rows(db,"select "+columns+" from "+join+" where "+' and '.join(exact_where)+" order by o.object_type,o.object_name limit ? offset ?",params+[query.upper(),limit+1,offset])
                if not result and offset==0:
                    return {**envelope,'results':[], 'nextOffset':None,'signal':'ENRICHMENT_MISSING',
                            'identities':[{'objectType':x['object_type'],'objectName':x['object_name']} for x in exact]}
            else:
                # Parse the stored typed key and use the existing composite object index.
                # Joining on concatenated object columns caused a repeated full-table scan.
                sql="""with hits as materialized (
                    select object_key,bm25(object_knowledge_fts,0,8,5,1,2,8,10) score
                    from object_knowledge_fts where object_knowledge_fts match ?)
                    select """+columns+""" from hits h join objects o
                    on o.object_type=substr(h.object_key,1,instr(h.object_key,':')-1)
                    and o.object_name=substr(h.object_key,instr(h.object_key,':')+1)
                    join released_catalog c on c.object_type=o.object_type and c.object_name=o.object_name
                    where """+' and '.join(where)+" order by h.score,o.object_type,o.object_name limit ? offset ?"
                result=rows(db,sql,[search_terms(db,query)]+params+[limit+1,offset])
            for item in result:
                oid=item.pop('id')
                matches=matched_capabilities(db,oid,query,filters.get('operation'))
                item['capabilities']=matches if matches else capabilities(db,oid,filters.get('operation'))
                item['matchEvidence']='exact_identity' if exact else ('curated_mapping' if matches else 'lexical_candidate')
                if filters.get('operation'):
                    item['operationEvidence']='curated' if matches else 'unverified'
        else:
            if exact:
                where=exact_where;params.append(query.upper())
            else:
                term=query.upper().replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
                where.append("(c.object_name like ? escape '\\' or c.container like ? escape '\\')");params.extend(['%'+term+'%']*2)
            result=rows(db,"""select c.object_type objectType,c.object_name objectName,c.release_state state,
                c.application_component component from released_catalog c where """+' and '.join(where)+
                ' order by c.object_type,c.object_name limit ? offset ?',params+[limit+1,offset])
    elif domain=='configuration':
        release=resolve_release(db,filters.get('release'));envelope['release']=release
        if not filters.get('release'):envelope['releaseAssumption']='latest_stored'
        where=['a.release=?'];params=[release]
        exact=scalar(db,'select count(*) from cfg_activities where release=? and activity_id=?',(release,query))
        if exact:
            where.append('a.activity_id=?');params.append(query);table='cfg_activities a';order='a.source_row'
        else:
            table="""cfg_documents_fts join cfg_activities a on cfg_documents_fts.release=a.release
                and a.source_row=cast(substr(cfg_documents_fts.doc_id,length('catalog:'||cfg_documents_fts.release||':')+1) as integer)
                and cfg_documents_fts.entity_id=a.activity_id"""
            where += ["cfg_documents_fts match ?","cfg_documents_fts.doc_type='catalog_activity'"]
            params.append(search_terms(db,query));order='bm25(cfg_documents_fts),a.activity_id,a.source_row'
        for key,column in (('scope','scope_item_id'),('country','specialized_countries'),('component','component_id')):
            if not filters.get(key):continue
            value=filters[key].upper()
            if key=='component':where.append('a.'+column+'=?');params.append(value)
            else:
                if not re.fullmatch(r'[A-Z0-9-]{1,40}',value):raise YulaError('FILTER_VALUE','Use one exact scope/country code.')
                match="(','||replace(a."+column+",' ','')||',') like ?"
                if key=='country':match="("+match+" or a.locality_type='Global' or (','||replace(a.specialized_countries,' ','')||',') like '%,XX,%')"
                where.append(match);params.append('%,'+value+',%')
        result=rows(db,"""select a.release,a.activity_id activityId,a.source_row sourceRow,a.activity_name name,
            a.category,a.scope_item_id scope,a.specialized_countries countries,a.locality_type locality,a.component_id component,
            a.configuration_approach access,json_extract(a.json,'$.additional_information') lifecycle
            from """+table+' where '+' and '.join(where)+' order by '+order+' limit ? offset ?',params+[limit+1,offset])
    elif domain=='docs':
        where=['doc_chunks match ?'];params=[search_terms(db,query)]
        if not filters.get('includeOtherEditions'):
            where += ["d.version not like '%pce%'", "lower(d.scope) not like '%private%'",
                      "lower(d.root_url) not like '%private%'", "lower(d.root_url) not like '%on-premise%'"]
        if filters.get('release'):where.append('d.version=?');params.append(filters['release'])
        result=rows(db,"""with hits as materialized (
            select c.document_id,c.topic_id,c.topic_title title,c.url,d.version,d.language,d.scope,
                   snippet(doc_chunks,9,'[',']',' … ',28) snippet,bm25(doc_chunks) score
            from doc_chunks c join doc_documents d on c.document_id=d.document_id where """+' and '.join(where)+""")
            select document_id documentId,topic_id topicId,title,url,version,language,scope,snippet,min(score) score
            from hits group by document_id,topic_id order by score,document_id,topic_id limit ? offset ?""",params+[limit+1,offset])
        for item in result:item.pop('score',None)
    else:
        where=["cfg_documents_fts match ?","d.doc_type in ('lesson','incident')"]
        params=[search_terms(db,query)]
        if filters.get('release'):where.append('d.release=?');params.append(filters['release'])
        result=rows(db,"""select d.doc_id recordId,d.release,d.doc_type kind,d.title,substr(d.body,1,320) summary,d.json
            from cfg_documents_fts f join cfg_documents d on d.doc_id=f.doc_id where """+' and '.join(where)+
            ' order by bm25(cfg_documents_fts),d.doc_id limit ? offset ?',params+[limit+1,offset])
        for item in result:
            data=loads(item.pop('json'),{});item['status']=data.get('status','unknown');item['evidenceLevel']='project_record'
    return {**envelope,'results':result[:limit],'nextOffset':offset+limit if len(result)>limit else None,
            **({'signal':'NO_MATCH','meaning':'No matching stored evidence; SAP unavailability is not established.'} if not result else {})}


def resolve_release(db, release=None):
    if release:
        if not scalar(db, "select count(*) from cfg_activities where release=?", (release,)):
            raise YulaError("RELEASE_MISSING", "No configuration catalog for this release.", release=release)
        return release
    available = [r[0] for r in db.execute("select distinct release from cfg_activities order by release desc")]
    if not available:
        raise YulaError("CONFIG_CORPUS_EMPTY", "No configuration catalog is loaded.")
    return available[0]


def text_page(text, offset, max_chars):
    offset = max(0, int(offset)); max_chars = max(1, min(int(max_chars), 12000))
    end = min(len(text), offset + max_chars)
    return {"text": text[offset:end], "offset": offset, "totalChars": len(text), "nextOffset": end if end < len(text) else None}


def activity_record_page(envelope, section, records, offset, limit, max_chars, text_offset):
    """Keep record offsets stable; page an oversized atomic record as lossless JSON."""
    # Reserve room for the snapshot added by MCP and budget JSON escaping too.
    budget = 47000
    encode = lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    selected = records[offset:offset + limit]
    def record_page():
        end = offset + len(selected)
        return {**envelope, "section": section, "records": selected,
                "nextOffset": end if end < len(records) else None, "total": len(records)}
    page = record_page()
    while len(selected) > 1 and len(encode(page)) > budget:
        selected = selected[:-1]
        page = record_page()
    if len(encode(page)) <= budget:
        if text_offset is not None:
            raise YulaError("UNSUPPORTED_FILTER", "textOffset applies only to oversized activity record pages.")
        return page
    if not selected:
        raise YulaError("RESPONSE_LIMIT", "Activity metadata exceeds the response bound.")
    text = encode(selected[0])
    start = 0 if text_offset is None else text_offset
    if start > len(text):
        raise YulaError("OFFSET_RANGE", "textOffset exceeds this record's JSON character count.", totalChars=len(text))
    size = max_chars
    while True:
        chunk = text_page(text, start, size)
        end = chunk["nextOffset"]
        page = {**envelope, "section": section, "representation": "json_record_page",
                "recordIndex": offset, "text": chunk["text"], "textOffset": chunk["offset"],
                "totalChars": chunk["totalChars"], "nextTextOffset": end,
                "nextOffset": offset + 1 if end is None and offset + 1 < len(records) else None,
                "total": len(records)}
        if len(encode(page)) <= budget:
            return page
        if size <= 1:
            raise YulaError("RESPONSE_LIMIT", "Activity metadata exceeds the response bound.")
        size = max(1, size // 2)


def object_context(db, object_type, name, section="summary", member=None, offset=0, limit=5, max_chars=4000):
    if section=='summary' and member:section='members'
    if section=='sources' and member:raise YulaError('UNSUPPORTED_FILTER','member applies to members/declaration, not source provenance.')
    fact=released(db,[{'objectType':object_type,'objectName':name}])
    available=fact['results'][0]
    if not available['eligible']:return {**fact,'signal':'OBJECT_NOT_ELIGIBLE'}
    entry=rows(db,'select id,object_type,object_name,description from objects where object_type=? and object_name=?',(object_type.upper(),name.upper()))
    receipt=rows(db,"select status,error_code from corpus_ingestion where edition='s4hc-latest' and object_type=? and object_name=?",(object_type.upper(),name.upper()))
    if not entry:return {**fact,'signal':'ENRICHMENT_MISSING','ingestion':receipt}
    obj=entry[0];oid=obj['id']
    evidence=rows(db,"""select source_kind kind,source_id source,fetched_at fetchedAt,source_sha256 sha256
        from evidence where object_id=? order by fetched_at desc,id desc limit 1""",(oid,))
    envelope={'objectType':obj['object_type'],'objectName':obj['object_name'],
              'availability':{'state':available['state'],'eligible':True,'decision':'REVIEW_REQUIRED','targetTenant':'unverified'},'catalog':fact['catalog'],'evidence':evidence}
    caps=capabilities(db,oid)
    if section=='summary':
        result={**envelope,'description':obj['description'],'capabilities':caps,
                'ingestion':receipt,'sections':['members','declaration','sources']}
        return result
    if section=='sources':
        observed=rows(db,'select source_id,sha256,observed_at,json from yula_observations where object_type=? and object_name=? order by observed_at desc limit 3',(object_type.upper(),name.upper()))
        for item in observed:item['metadata']=loads(item.pop('json'),{})
        return {**envelope,'metadataObservations':observed,'ingestion':receipt}
    if receipt and receipt[0]['status'] in ('failed','metadata_only','not_applicable'):
        return {**envelope,'signal':'SIGNATURE_UNAVAILABLE','ingestion':receipt,'members':[],'nextOffset':None}
    if section=='declaration':
        info=rows(db,'select content_kind,encoding,source_sha256,content_bytes,content_chars from object_content where object_id=? order by content_kind',(oid,))
        if not info:raise YulaError('CONTENT_MISSING','No public declaration is stored.')
        if len(info)>1 and not member:return {**envelope,'contentKinds':[x['content_kind'] for x in info],'signal':'CONTENT_KIND_REQUIRED','selectorParameter':'member'}
        selected=next((r for r in info if not member or r['content_kind']==member),None)
        if not selected:raise YulaError('CONTENT_MISSING','Unknown content kind.')
        if selected['encoding'] not in {'gzip','gzip-utf8'}:raise YulaError('CONTENT_ENCODING','Unsupported public-content encoding.')
        import io
        blob=scalar(db,'select content_blob from object_content where object_id=? and content_kind=?',(oid,selected['content_kind']))
        with gzip.GzipFile(fileobj=io.BytesIO(blob)) as stream:payload=stream.read(16*1024*1024+1)
        if len(payload)>16*1024*1024 or len(payload)!=selected['content_bytes'] or hashlib.sha256(payload).hexdigest()!=selected['source_sha256']:
            raise YulaError('CONTENT_CORRUPT','Public declaration hash/size mismatch.')
        text=payload.decode('utf-8')
        if len(text)!=selected['content_chars']:raise YulaError('CONTENT_CORRUPT','Public declaration character count mismatch.')
        return {**envelope,'kind':selected['content_kind'],'sha256':selected['source_sha256'],**text_page(text,offset,max_chars)}
    if section!='members':raise YulaError('SECTION','Object sections: summary, members, declaration, sources.')
    where='object_id=?';params=[oid]
    if member:where+=' and name=? collate nocase';params.append(member)
    members=rows(db,'select name,kind,signature from members where '+where+' order by name,kind limit ? offset ?',params+[limit+1,offset])
    for m in members:
        if not m['signature']:m['signatureStatus']='missing'
        elif len(m['signature'])>max_chars:
            m['signature']=m['signature'][:max_chars];m['signatureTruncated']=True;m['readComplete']='declaration'
    recipes=rows(db,"""select distinct r.id,r.title_en title,r.summary_en summary,r.prerequisites_json,r.warnings_json
        from recipes r join object_capabilities c on c.object_id=r.object_id and c.capability_id=r.capability_id
        where r.object_id=? and (? is null or c.member_name=? collate nocase)""",(oid,member,member))
    for recipe in recipes:
        recipe['prerequisites']=loads(recipe.pop('prerequisites_json'),[]);recipe['warnings']=loads(recipe.pop('warnings_json'),[])
    return {**envelope,'members':members[:limit],'usage':recipes,'nextOffset':offset+limit if len(members)>limit else None,
            **({'signal':'MEMBER_MISSING'} if member and not members else {})}


def source_references(value):
    found=set()
    if isinstance(value,dict):
        for key,item in value.items():
            if key in ('source_id','sourceId') and isinstance(item,str):found.add(item)
            elif key in ('source_ids','sourceIds') and isinstance(item,list):found.update(x for x in item if isinstance(x,str))
            elif key=='sources' and isinstance(item,list):
                for x in item:
                    if isinstance(x,str):found.add(x)
                    elif isinstance(x,dict):
                        ident=x.get('source_id',x.get('id'))
                        if isinstance(ident,str):found.add(ident)
                found.update(source_references(item))
            else:found.update(source_references(item))
    elif isinstance(value,list):
        for item in value:found.update(source_references(item))
    return found


def activity_sources(db,release,key,profile):
    selected=rows(db,'select source_id,json from cfg_sources where release=? and activity_id=? order by source_id',(release,key))
    ids=source_references(profile)
    related=[profile]
    for row in db.execute("select json from cfg_dependencies where release=? and (source_activity_id=? or target_activity_id=?)",(release,key,key)):
        value=loads(row[0],{});related.append(value);ids.update(source_references(value))
    for table in ('cfg_changes','cfg_lessons'):
        for row in db.execute('select json from '+table+' where release=? and activity_ids like ?',(release,'%"'+key+'"%')):
            value=loads(row[0],{});related.append(value);ids.update(source_references(value))
    for record in related:
        for source in record.get('sources',[]):
            if isinstance(source,dict) and source.get('url'):
                sid=source.get('source_id',source.get('id'))
                if isinstance(sid,str):selected.append({'source_id':sid,'json':json.dumps(source,ensure_ascii=False)})
    if ids:
        selected += rows(db,"select source_id,json from cfg_sources where release=? and activity_id='' and source_id in ("+','.join('?' for _ in ids)+') order by source_id',(release,*sorted(ids)))
    # An activity-specific record wins only when the duplicate has identical semantics;
    # differing source records remain visible as explicit alternatives.
    result=[];seen={}
    for row in selected:
        value=loads(row['json'],{});sid=row['source_id']
        if sid not in seen:seen[sid]=value;result.append(value)
        elif value!=seen[sid]:
            # Registry and local copies can differ only in supplementary fields.
            identity_keys=('url','title','release','checked_at','checkedAt','evidence_level')
            if any(k in value and k in seen[sid] and value[k]!=seen[sid][k] for k in identity_keys):
                result.append({'source_id':sid,'conflict':True,'alternative':value})
    result += [{'source_id':sid,'signal':'SOURCE_MISSING'} for sid in sorted(ids-set(seen))]
    return result


def activity_context(db, key, release=None, section="summary", offset=0, limit=5, max_chars=4000, source_row=None, text_offset=None):
    if text_offset is not None and section in ("summary", "dossier"):
        raise YulaError("UNSUPPORTED_FILTER", "textOffset applies only to oversized structured activity record pages.")
    assumed = release is None
    release = resolve_release(db, release)
    records = rows(db, "select * from cfg_activities where release=? and activity_id=? order by source_row", (release, key))
    if not records:
        raise YulaError("ACTIVITY_MISSING", "Activity is not in the selected release catalog.", release=release, activityId=key)
    envelope = {"release": release, "activityId": key,
                "reviewFlags": rows(db, "select reason,flagged_at from yula_review_flags where release=? and activity_id=?", (release, key))}
    variant_count=len(records)
    if variant_count>1:envelope['contextStatus']='ACTIVITY_ID_AMBIGUOUS'
    if assumed:envelope['releaseAssumption']='latest_stored'
    if source_row is not None:
        records=[r for r in records if r['source_row']==source_row]
        if not records:raise YulaError('VARIANT_MISSING','The selected source row does not match the activity.')
    if len(records)>1 and section not in ('catalog','sources'):
        if text_offset is not None:
            raise YulaError("UNSUPPORTED_FILTER", "Select an activity variant before using textOffset.")
        return {**envelope,'signal':'AMBIGUOUS_ACTIVITY','variants':[
            {'sourceRow':r['source_row'],'name':r['activity_name'],'scope':r['scope_item_id'],'countries':r['specialized_countries'],'component':r['component_id']} for r in records[offset:offset+limit]],
            'nextOffset':offset+limit if offset+limit<len(records) else None}
    profile_rows = rows(db, "select json from cfg_profiles where release=? and activity_id=?", (release, key))
    profile = loads(profile_rows[0]["json"], {}) if profile_rows else {}
    if variant_count>1 and source_row is not None and profile.get('source_row')!=source_row:
        envelope['contextStatus']='VARIANT_DOSSIER_UNVERIFIED'
    if section == "summary":
        r = records[0]; catalog = loads(r["json"], {})
        summary = profile.get("summary", "")
        summary_metadata = {}
        if not isinstance(summary, str):
            summary = json.dumps(summary, ensure_ascii=False, separators=(",", ":"))
            summary_metadata = {"summaryRepresentation": "json"}
        return {**envelope, "name": r["activity_name"], "scope": r["scope_item_id"], "component": r["component_id"],
                "category": r["category"], "access": r["configuration_approach"], "redoInProduction": r["redo_in_p"],
                "deletion": r["delete_customer_records"], "lifecycle": catalog.get("additional_information", ""),
                "dossierStatus": 'context_unverified' if envelope.get('contextStatus')=='VARIANT_DOSSIER_UNVERIFIED' else profile.get("status", "missing"), "summary": summary[:max_chars],
                **({"summaryTruncated":True,"readComplete":"dossier"} if len(summary)>max_chars else {}),
                "catalogVariants": len(records), "whatsNew": profile.get("whats_new", {"result": "not_checked"}),
                "sections": ["catalog", "dossier", "sources", "access", "dependencies", "changes", "lessons", "tests"],
                "evidence": "Catalog metadata and curated project research; target setup and current release changes require verification.",
                **summary_metadata}
    if section == "catalog":
        result = [loads(r["json"], {}) for r in records]
    elif section == "sources":
        result = activity_sources(db,release,key,profile)
    elif section == "access":
        imgs = list(dict.fromkeys(r["img_activity"] for r in records if r["img_activity"]))
        clauses = ["sscui_id=?"]; args = [release, key]
        if imgs:
            clauses.append("img_activity in (" + ",".join("?" for _ in imgs) + ")"); args += imgs
        result = [loads(r["json"], {}) for r in rows(db, "select distinct json from cfg_access_map where release=? and (" + " or ".join(clauses) + ")", args)]
    elif section == "dependencies":
        result = [loads(r["json"], {}) for r in rows(db,
                  "select json from cfg_dependencies where release=? and (source_activity_id=? or target_activity_id=?)", (release, key, key))]
    elif section in ("changes", "lessons"):
        result = [loads(r["json"], {}) for r in rows(db, f"select json from cfg_{section} where release=? and activity_ids like ?", (release, '%"' + key + '"%'))]
    elif section == "tests":
        result = profile.get("tests", [])
    elif section == "dossier":
        text = json.dumps(profile, ensure_ascii=False, separators=(",", ":"))
        return {**envelope, **text_page(text, offset, max_chars), "status": profile.get("status", "missing")}
    else:
        # A discovered dossier subsection can be retrieved without reading the whole profile.
        if section not in profile:
            raise YulaError("SECTION_MISSING", "No such dossier section.", available=list(profile))
        result = profile[section] if isinstance(profile[section], list) else [profile[section]]
    return activity_record_page(envelope, section, result, offset, limit, max_chars, text_offset)


def get(db, kind, key, objectType=None, release=None, section="summary", member=None, offset=0, limit=5, maxChars=4000, sourceRow=None, textOffset=None):
    if kind != 'activity' and textOffset is not None:
        raise YulaError('UNSUPPORTED_FILTER','textOffset applies only to oversized activity record pages.')
    if kind != 'object' and (objectType is not None or member is not None):
        raise YulaError('UNSUPPORTED_FILTER','objectType/member apply only to object retrieval.')
    if kind in ('topic','record') and section != 'summary':
        raise YulaError('UNSUPPORTED_FILTER','Topic/record text uses offset and maxChars, not object/activity sections.')
    if kind != 'activity' and sourceRow is not None:raise YulaError('UNSUPPORTED_FILTER','sourceRow applies only to activities.')
    if kind == "object":
        if release:raise YulaError('UNSUPPORTED_FILTER','Objects use s4hc-latest; a target release requires separate tenant evidence.',field='release')
        return object_context(db, objectType, key, section, member, offset, limit, maxChars)
    if kind == "activity":
        return activity_context(db, key, release, section, offset, limit, maxChars, sourceRow, textOffset)
    if kind == "topic":
        if ":" not in key:
            raise YulaError("TOPIC_KEY", "Topic key must be documentId:topicId.")
        document_id, topic_id = key.split(":", 1)
        found = rows(db, """select c.topic_title,c.url,c.root_url,c.scope,c.text,d.version
            from doc_chunks c join doc_documents d on d.document_id=c.document_id
            where c.document_id=? and c.topic_id=? order by c.rowid""",
                     (document_id, topic_id))
        if not found:
            raise YulaError("TOPIC_MISSING", "No stored topic matches this key.")
        if release and release != found[0]['version']:raise YulaError('RELEASE_MISMATCH','Topic version does not match the requested release.')
        metadata=rows(db,'select * from doc_topic_evidence where document_id=? and topic_id=?',(document_id,topic_id)) if has_table(db,'doc_topic_evidence') else []
        joiner=metadata[0]['joiner'] if metadata else '\n\n'
        text = joiner.join(x['text'] for x in found)
        text_hash=hashlib.sha256(text.encode()).hexdigest()
        if metadata and text_hash!=metadata[0]['text_sha256']:raise YulaError('TOPIC_EVIDENCE_STALE','Topic changed outside its provenance update; refresh this source.')
        freshness={'fetchedAt':None,'state':'unknown'}
        if metadata and metadata[0]['fetched_at']:
            freshness={'source':metadata[0]['source_id'],'fetchedAt':metadata[0]['fetched_at']}
        return {"key": key, "title": found[0]["topic_title"], "url": found[0]["url"], "version": found[0]["version"],
                "scope": "Private Edition (reference only)" if "pce" in found[0]["version"].lower() else found[0]["scope"],
                "freshness": freshness, "representation": metadata[0]["representation"] if metadata else "legacy_chunks",
                "storedTextSha256": text_hash,
                **text_page(text, offset, maxChars)}
    if kind == "record":
        found = rows(db, "select json,body,title,updated_at,release from cfg_documents where doc_id=?", (key,))
        if not found:
            raise YulaError("RECORD_MISSING", "No stored knowledge record matches this key.")
        if release and release != found[0]["release"]:raise YulaError("RELEASE_MISMATCH","Record release does not match the request.")
        return {"key": key, "title": found[0]["title"], "release":found[0]["release"], "updatedAt": found[0]["updated_at"],
                **text_page(found[0]["json"] or found[0]["body"], offset, maxChars)}
    raise YulaError("KIND", "Unknown context kind.")
