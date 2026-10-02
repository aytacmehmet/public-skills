# SPDX-License-Identifier: GPL-3.0-only
"""Role-owned questions, self-contained named packages and atomic batch delivery."""
import copy, io, json, posixpath, re, tempfile, zipfile
from pathlib import Path
import bv2 as b

EXTRAS={'developer_decisions','references','architecture'}
CORE_DEPENDENCIES={
 'core':set(), 'architecture':{'core','decisions'},
 'decisions':{'references'}, 'references':{'core'},
 'questions':{'decisions'}, 'packaging':{'core','architecture','references','decisions','questions'}}
FILE_TOKEN=re.compile(r'(?<![\w:/.-])((?:\./|\.\./)*[\w-]+(?:/[\w.-]+)*\.(?:toon|md|png|xlsx|csv|xml|pdf|docx|txt|html|mjs|js|css|json|svg))(?:#([^\s)\]`,]+))?',re.I)
ASSET_LINK=re.compile(r'(?:\b(?:src|href)\s*=\s*[\"\x27]([^\"\x27]+)[\"\x27]|url\(\s*[\"\x27]?([^\s\"\x27)]+))',re.I)
LINK=re.compile(r'\[[^\]]*\]\(([^)]+)\)')
REF_TOKEN=re.compile(r'\bREF-[A-Z0-9-]+\b')
SCHEMA=json.loads((b.ROOT/'schema/handoff.schema.json').read_text(encoding='utf-8'))

def core_spec(spec):
    value={k:copy.deepcopy(v) for k,v in spec.items() if k not in EXTRAS}
    value['schemaVersion']='2.0'
    return value

def layout(spec):
    slug=spec['meta']['development_name'];b.safe_name(slug)
    return {role:slug+'-'+suffix for role,suffix in {
      'specification':'belirtim.toon','schema':'schema.toon','readiness':'readiness.toon',
      'objects':'objects.toon','naming':'naming.md','defaults':'defaults.md',
      'changelog':'changelog.md','format':'format.md','readme':'readme.md',
      'manifest':'manifest.toon','technical_decisions':'developer-decisions.toon',
      'architecture':'architecture.toon','references':'references.toon',
      'baseline':'baseline.toon','baseline_spec':'baseline-spec.toon','changes':'changes.toon',
      'excel':'specification.xlsx','dependency_contracts':'dependency-contracts.toon'}.items()}

def prefixed(spec,path):
    rel=b.safe_name(path);return rel.name.startswith(spec['meta']['development_name']+'-')

def upgrade(doc):
    import delivery as d
    spec,control=d.get_state(doc)
    if spec.get('schemaVersion')=='3.0': raise b.Invalid('Already a 3.0 workspace')
    if spec.get('schemaVersion')!='2.0': raise b.Invalid('Unsupported source contract')
    before=d.revision(spec)
    spec['schemaVersion']='3.0';spec['developer_decisions']=[];spec['references']=[]
    spec['architecture']={'summary':'BİLGİ BEKLİYOR','boundaries':[], 'constraints':[]}
    mapping={}
    for asset in control.get('assets',[]):
        old=asset['path'];rel=b.safe_name(old)
        new=old if prefixed(spec,old) else str(rel.with_name(spec['meta']['development_name']+'-'+rel.name)).replace('\\','/')
        mapping[old]=new;asset.update(path=new,source_path=asset.get('source_path',old))
    def remap(value):
        if isinstance(value,dict): return {k:remap(v) for k,v in value.items()}
        if isinstance(value,list): return [remap(v) for v in value]
        return mapping.get(value,value) if isinstance(value,str) else value
    doc['delivery']['spec']=remap(spec)
    control['import_reference']={'schemaVersion':'2.0','spec_sha256':before}
    control.setdefault('architecture_findings',[])
    d.invalidate(doc)
    return {'source_sha256':before,'status':'DRAFT','asset_mapping':mapping}

def score_options(options):
    if not isinstance(options,list) or not 0<=len(options)<=3: raise b.Invalid('Provide at most three grounded consultant options')
    rows=[]
    for option in options:
        if not isinstance(option,dict) or not option.get('text') or not option.get('rationale') or not option.get('assumptions'):
            raise b.Invalid('Option text, rationale and explicit assumptions required')
        scores=option.get('scores',{})
        if set(scores)!={'consistency','suitability','quality'} or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not 0<=v<=5 for v in scores.values()):
            raise b.Invalid('Three judgment scores in 0..5 required')
        row=copy.deepcopy(option);row['score']=round(sum(scores.values())/3,4);rows.append(row)
    rows.sort(key=lambda x:-x['score'])
    for label,row in zip('ABC',rows): row['label']=label;row['evidence']='RELATIVE_JUDGMENT'
    return rows

def consultant_questions(doc):
    _,control=state(doc);rows=[]
    for name in ('intake','decisions_gaps','open_questions'):
        for question in control.get(name,[]):
            if question.get('status')=='CLOSED': continue
            if question.get('owner')=='ABAP_DEVELOPER':
                if question.get('domain')!='IMPLEMENTATION': raise b.Invalid('Split mixed/business questions; do not assign them to developer')
                continue
            if question.get('domain')=='IMPLEMENTATION': raise b.Invalid('Technical question is not consultant-owned; classify/split it first')
            if question.get('domain') not in ('BUSINESS','USER_EXPERIENCE','BUSINESS_DESIGN'):
                raise b.Invalid('Consultant question needs an explicit business/design domain')
            if not question.get('options') and not question.get('options_reason'):
                raise b.Invalid('Missing grounded options require an explicit information gap reason')
            rows.append({'id':question['id'],'owner':'CONSULTANT','domain':question['domain'],
                'question':question['question'],'options':score_options(question.get('options')),
                'options_reason':question.get('options_reason'),
                'score_note':'Equal-weight relative judgment; tied scores do not imply a quality difference'})
    return rows

def state(doc):
    import delivery as d
    return d.get_state(doc)

def eligible_technical(spec,row):
    matches=[x for x in spec.get('developer_decisions',[]) if x['id']==row.get('id')]
    return (row.get('owner')=='ABAP_DEVELOPER' and row.get('domain')=='IMPLEMENTATION'
        and len(matches)==1 and matches[0]['status']=='OPEN'
        and row.get('question')==matches[0]['question'])

def profile(spec):
    import delivery as d
    errors=[];ids={}
    for name in ('developer_decisions','references'):
        for row in spec.get(name,[]):
            if row['id'] in ids: errors.append(d.issue('V3_DUPLICATE','/'+name,row['id']))
            ids[row['id']]=name
    allids={r['id'] for name in d.COLLECTIONS for r in spec[name]}
    if allids&set(ids): errors.append(d.issue('V3_DUPLICATE','/','Decision/reference ID collides'))
    constraints={r['id'] for r in spec['architecture']['constraints']}
    architecture_ids=[r['id'] for name in ('constraints','boundaries') for r in spec['architecture'][name]]
    if len(architecture_ids)!=len(set(architecture_ids)) or set(architecture_ids)&(allids|set(ids)):
        errors.append(d.issue('V3_DUPLICATE','/architecture','Architecture IDs must be unique across collections'))
    objects={r['id'] for r in spec['objects']};requirements={r['id'] for r in spec['requirements']}
    boundaries=[]
    for row in spec['architecture']['boundaries']:
        boundaries+=row['object_refs']
        if not set(row['object_refs'])<=objects: errors.append(d.issue('ARCHITECTURE_REF','/architecture/boundaries','Unknown object'))
    if set(boundaries)!=objects or len(boundaries)!=len(set(boundaries)):
        errors.append(d.issue('ARCHITECTURE_BOUNDARIES','/architecture','Each object needs exactly one responsibility boundary'))
    for row in spec['architecture']['constraints']:
        if not set(row['requirement_refs'])<=requirements: errors.append(d.issue('ARCHITECTURE_REF','/architecture/constraints','Unknown requirement'))
    refs={r['id'] for r in spec['references']}
    for row in spec['developer_decisions']:
        if not set(row['reference_ids'])<=refs or not set(row['architecture_constraint_refs'])<=constraints:
            errors.append(d.issue('TECHNICAL_CONTEXT','/developer_decisions','Missing packaged reference or architecture constraint'))
        if row['status']=='OPEN' and row['answer'] is not None or row['status']=='ANSWERED' and not row['answer']:
            errors.append(d.issue('TECHNICAL_STATUS','/developer_decisions','Answer/status mismatch'))
    for row in spec['references']:
        try:
            b.safe_name(row['path'])
            if not prefixed(spec,row['path']): raise b.Invalid('Reference filename must start with development short name')
        except b.Invalid as e: errors.append(d.issue('REFERENCE_PATH','/references',str(e)))
    for media in spec['media']:
        if not prefixed(spec,media['path']): errors.append(d.issue('FILE_PREFIX','/media','Media filename must start with short name'))
    return errors

def blocking_markers(spec):
    import delivery as d
    return sum(isinstance(v,str) and bool(d.GAP.search(v)) for v in b.flatten({k:v for k,v in spec.items() if k!='developer_decisions'}).values())

def fingerprints(doc):
    spec,control=state(doc)
    values={'core':core_spec(spec),'architecture':spec.get('architecture'),
      'decisions':{'rows':spec.get('developer_decisions'),'architecture':spec.get('architecture')},
      'references':{'rows':spec.get('references'),'contracts':control.get('dependency_contracts')},
      'questions':{k:control.get(k) for k in ('intake','decisions_gaps','open_questions','system_conflicts','architecture_findings')},
      'packaging':{'assets':control.get('assets'),'baseline':spec['baseline'],'dependencies':spec['dependencies']}}
    hashes={}
    def visit(name):
        if name not in hashes:
            dep={x:visit(x) for x in CORE_DEPENDENCIES[name]}
            hashes[name]=b.digest(b.canonical({'input':values[name],'dependencies':dep,'checker_version':'3.0.0'}))
        return hashes[name]
    for name in values: visit(name)
    return hashes

def check_plan(doc,final=False):
    _,control=state(doc);now=fingerprints(doc);cache=control.get('check_cache',{})
    run=[n for n,h in now.items() if cache.get(n,{}).get('input_sha256')!=h or cache[n].get('status')!='PASS']
    reused=sorted(set(now)-set(run))
    return {'run':run,'reuse':reused,'input_sha256':now,'final_integrity_required':bool(final),
      'reader_policy':'Collect edits first; run current-snapshot independent release reviews only after consultant closure and architecture checks',
      'scope':'Planning only; reused PASS requires matching checker and dependency hashes'}

def record_check(doc,name,input_sha256,status):
    _,control=state(doc)
    if name not in CORE_DEPENDENCIES or fingerprints(doc)[name]!=input_sha256 or status not in ('PASS','FAIL'):
        raise b.Invalid('Check result must bind to its current input/dependency snapshot')
    control.setdefault('check_cache',{})[name]={'input_sha256':input_sha256,'status':status}

def archive_reviews(control):
    if control.get('eval_rounds'):
        control.setdefault('review_history',[]).append({'rounds':copy.deepcopy(control['eval_rounds']),
          'requests':copy.deepcopy(control.get('eval_requests',[]))})

def verify_references(spec,files):
    import delivery as d
    refs={r['id']:r for r in spec['references']}
    for row in refs.values():
        path=row['path']
        if path not in files or b.digest(files[path])!=row['sha256']: raise b.Invalid('Referenced file missing or hash differs: '+path)
        if row['pointer'] is not None:
            if Path(path).suffix!='.toon': raise b.Invalid('Pointers require a decoded TOON document')
            try: d.resolve(json.loads(b.codec('decode',files[path].decode())),row['pointer'])
            except (b.Invalid,KeyError,IndexError,TypeError): raise b.Invalid('Referenced text/list pointer missing: '+row['id'])
    def scan(text,source):
        for rid in REF_TOKEN.findall(text):
            if rid not in refs: raise b.Invalid('Undeclared document/text reference: '+rid)
        candidates=[m.group(1)+(('#'+m.group(2)) if m.group(2) else '') for m in FILE_TOKEN.finditer(text)]
        candidates += [x for x in LINK.findall(text) if not x.startswith('#')]
        if source.startswith('mockup/interactive/'):
            candidates += [left or right for left,right in ASSET_LINK.findall(text)]
        for target in candidates:
            target=target.strip('<>')
            if target.startswith(('#','data:')): continue
            if re.match(r'(?i)https?://|file:|plugin:',target): raise b.Invalid('Required external reference is not self-contained: '+target)
            target,_,fragment=target.partition('#')
            if target.startswith('/') or '\\' in target: raise b.Invalid('Reference must be a relative ZIP path')
            direct=posixpath.normpath(target);relative=posixpath.normpath(posixpath.join(posixpath.dirname(source),target))
            resolved=direct if direct in files else relative
            if resolved not in files: raise b.Invalid('Dangling file reference: '+target)
            if fragment and Path(resolved).suffix=='.toon':
                try: d.resolve(json.loads(b.codec('decode',files[resolved].decode())),fragment)
                except (b.Invalid,KeyError,IndexError,TypeError): raise b.Invalid('Dangling TOON text/list pointer: '+target+'#'+fragment)
    for name,data in files.items():
        if Path(name).suffix in ('.md','.toon','.csv','.xml','.txt','.html','.js','.mjs','.css','.json','.svg'): scan(data.decode('utf-8'),name)
    for row in spec['developer_decisions']:
        if not set(row['reference_ids'])<=set(refs): raise b.Invalid('Developer decision needs another file')
    return {'status':'PASS','references':len(refs),'files':len(files)}

def copy_asset(asset,root):
    import delivery as d
    physical=asset.get('source_path',asset['path'])
    _,data=d.copy_asset({**asset,'path':physical},root)
    return asset['path'],data

def dependency_records(doc):
    _,control=state(doc)
    records=control.get('dependency_contracts',[])
    if len({x['development_id'] for x in records})!=len(records): raise b.Invalid('Duplicate dependency contract')
    if any(not isinstance(x.get('requires_change'),bool) for x in records): raise b.Invalid('Dependency change status must be explicit')
    return {x['development_id']:x for x in records}

def build(doc,assets_root,include_excel=True):
    import delivery as d
    spec,control=state(doc)
    if spec['schemaVersion']!='3.0': raise b.Invalid('2.0 handoffs are read-only references; run release-upgrade')
    report=d.evaluate(doc)
    if report['decision']!='DELIVERABLE': raise b.Invalid('Consultant, architecture, reference or review gate remains: '+','.join(sorted({i['code'] for i in report['issues']})))
    roles=layout(spec)
    files={roles['specification']:b.encode(spec).encode(),roles['schema']:b.encode(SCHEMA).encode(),
      roles['readiness']:b.encode(d.neutral_report(report)).encode(),roles['objects']:b.encode({'objects':spec['objects']}).encode(),
      roles['technical_decisions']:b.encode({'decisions':spec['developer_decisions']}).encode(),
      roles['architecture']:b.encode(spec['architecture']).encode(),roles['references']:b.encode({'references':spec['references']}).encode(),
      roles['naming']:('# Naming\n\n'+spec['naming_rules']['name']+' '+spec['naming_rules']['version']+'\n'+spec['naming_rules']['description']+'\n').encode(),
      roles['defaults']:('# '+spec['functional_defaults']['name']+'\n\n'+spec['functional_defaults']['version']+'\n'+'\n'.join(x['id']+': '+x['text'] for x in spec['functional_defaults']['rules'])+'\n').encode(),
      roles['changelog']:('# Changes\n\n'+'\n'.join(x['version']+' | '+x['date']+' | '+x['change'] for x in spec['changelog'])+'\n').encode(),
      roles['format']:('''# Data contract

Use the manifest role map to find the authoritative specification and schema.
UTF-8/LF, strict TOON 4.1, two-space indentation and comma delimiter apply.
Resolve pointers on decoded data. Quoted IDs/exact decimals preserve precision.
Excel is derived; PNG is layout authority only. Versions are immutable.
Open developer decisions are bounded implementation choices, not missing business requirements.
Recorded local/reviewer checks do not prove SAP activation, runtime or UAT.
''').encode()}
    for asset in control.get('assets',[]):
        name,data=copy_asset(asset,assets_root)
        if not prefixed(spec,name): raise b.Invalid('Every asset filename must start with the development short name')
        if name in files: raise b.Invalid('Duplicate generated/asset path')
        if name.startswith('mockup/interactive/'):
            exception=control.get('mockup_exception',{})
            if not all(exception.get(x) for x in ('authorized','receipt','offline_verified','offline_evidence')): raise b.Invalid('Explicit offline interactive exception missing')
        files[name]=data
    for media in spec['media']:
        if media['path'] not in files or b.digest(files[media['path']])!=media['sha256']: raise b.Invalid('PNG/callout snapshot missing or changed')
    for name in spec['baseline']['evidence_paths']:
        if name not in files: raise b.Invalid('Baseline evidence missing')
    if spec['meta']['mode']=='UPDATE':
        source_path=control.get('baseline_reference_path')
        if not source_path: raise b.Invalid('Exact baseline artifact required')
        root=Path(assets_root).resolve();source=root.joinpath(*b.safe_name(source_path).parts)
        if source.is_symlink() or not source.resolve().is_relative_to(root) or not source.is_file() or b.digest(source.read_bytes())!=spec['baseline']['reference_sha256']: raise b.Invalid('Baseline artifact missing or changed')
        if spec['baseline']['kind']=='FINAL_HANDOFF':
            if source.name!=spec['baseline']['reference_name']: raise b.Invalid('Baseline filename differs')
            result=d.verify(source)
            if result['specSha256']!=spec['baseline']['spec_sha256']: raise b.Invalid('Baseline reference content differs')
        files[roles['baseline']]=b.encode(spec['baseline']).encode()
        files[roles['baseline_spec']]=b.encode(control['baseline_spec']).encode()
        files[roles['changes']]=b.encode(d.changes(control['baseline_spec'],spec)).encode()
    contracts=dependency_records(doc)
    if set(contracts)!={x['development_id'] for x in spec['dependencies']}: raise b.Invalid('Every dependency contract must be packaged locally')
    for dep in spec['dependencies']:
        row=contracts[dep['development_id']]
        if row.get('version')!=dep['version'] or row.get('contract')!=dep['contract'] or not row.get('content'):
            raise b.Invalid('Dependency version/contract/content differs')
    files[roles['dependency_contracts']]=b.encode({'contracts':list(contracts.values())}).encode()
    if include_excel:
        with tempfile.TemporaryDirectory(prefix='spec-view-') as temp:
            book=Path(temp)/roles['excel'];d.render_excel(spec,report,book);d.verify_excel(spec,book);files[roles['excel']]=book.read_bytes()
    files[roles['readme']]=('# '+spec['meta']['name']+'\n\nDevelopment: '+spec['meta']['development_id']+'\nVersion: '+spec['meta']['handoff_version']+'\n\n'
      'Read '+roles['manifest']+', then '+roles['specification']+', '+roles['technical_decisions']+' and '+roles['architecture']+'.\n'
      'The specification and supplied project constraints are authoritative; Excel is derived and PNG only defines layout.\n'
      'Complete only the listed implementation decisions, within the fixed functional and architectural constraints, before coding.\n'
      'No additional development document is required. Use the acceptance vectors and packaged contracts to verify the implementation.\n'
      'Inventory:\n'+'\n'.join('- '+n for n in sorted(files))+'\n- '+roles['readme']+'\n- '+roles['manifest']+'\n').encode()
    manifest={'schemaVersion':'3.0','development_id':spec['meta']['development_id'],'handoff_version':spec['meta']['handoff_version'],
      'fs_version':spec['meta']['fs_version'],'spec_sha256':d.revision(spec),'roles':{k:v for k,v in roles.items() if v in files or k=='manifest'},
      'baseline':spec['baseline'],'linked_handoffs':spec['dependencies'],
      'files':[{'path':n,'sha256':b.digest(data),'bytes':len(data)} for n,data in sorted(files.items())], 'self_hash':'EXTERNAL'}
    manifest['files'].append({'path':roles['manifest'],'sha256':None,'bytes':None})
    files[roles['manifest']]=b.encode(manifest).encode()
    # Final integrity/closure/privacy is checked once on the staged saved ZIP,
    # before single or atomic batch publication; assembly never declares PASS.
    return files,manifest

def write_zip(files,path):
    with zipfile.ZipFile(path,'x',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,data)

def verify(path,expected_name=None):
    import delivery as d
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or z.testzip() or z.comment or sum(i.file_size for i in z.infolist())>128*1024*1024: raise b.Invalid('Invalid ZIP inventory/CRC/size')
        for info in z.infolist():
            b.safe_name(info.filename)
            if info.flag_bits&1 or (info.external_attr>>16)&0o170000==0o120000: raise b.Invalid('ZIP encryption/symlink')
        candidates=[n for n in names if n.endswith('-manifest.toon')]
        if len(candidates)!=1: raise b.Invalid('Exactly one scoped manifest required')
        manifest_data=z.read(candidates[0]);manifest=json.loads(b.codec('decode',manifest_data.decode()))
        roles=manifest['roles'];required={'manifest','specification','schema','readiness','objects','naming','defaults','changelog','format','readme','technical_decisions','architecture','references','dependency_contracts'}
        if not required<=set(roles) or len(set(roles.values()))!=len(roles) or any(n not in names for n in roles.values()): raise b.Invalid('Manifest roles missing/ambiguous')
        spec=json.loads(b.codec('decode',z.read(roles['specification']).decode()))
        if spec.get('schemaVersion')!='3.0' or d.shape_and_profile(spec): raise b.Invalid('Invalid complete v3 specification')
        if roles!={k:v for k,v in layout(spec).items() if v in names}: raise b.Invalid('Role filenames differ from scoped layout')
        rows={r['path']:r for r in manifest['files']}
        if set(rows)!=set(names) or len(rows)!=len(manifest['files']) or manifest['self_hash']!='EXTERNAL' or rows[roles['manifest']]['sha256'] is not None: raise b.Invalid('Manifest inventory/self hash')
        files={n:z.read(n) for n in names}
        for name,data in files.items():
            if not prefixed(spec,name): raise b.Invalid('Unscoped filename')
            if name!=roles['manifest'] and (b.digest(data)!=rows[name]['sha256'] or len(data)!=rows[name]['bytes']): raise b.Invalid('File hash differs')
            suffix=Path(name).suffix.lower()
            if name.startswith('mockup/interactive/'):
                if re.search(r'(?i)<!--|<meta[^>]+name\s*=\s*[\"\x27]generator',data.decode()): raise b.Invalid('Interactive metadata not clean')
                if suffix not in ('.html','.js','.mjs','.css','.json','.svg') or d.TOOL.search(data.decode()) or d.NETWORK.search(data.decode()): raise b.Invalid('Interactive metadata/network/code')
            elif suffix in ('.toon','.md','.csv','.xml','.txt'):
                if d.privacy(data.decode()): raise b.Invalid('Producer/code/private content')
            elif suffix=='.png': d.clean_png(data)
            elif suffix=='.xlsx':
                with zipfile.ZipFile(io.BytesIO(data)) as book:
                    if any(p.endswith('.xml') and d.TOOL.search(book.read(p).decode()) for p in book.namelist()): raise b.Invalid('Workbook producer metadata')
            else: raise b.Invalid('Unsupported/code artifact')
        if manifest['spec_sha256']!=d.revision(spec) or manifest['development_id']!=spec['meta']['development_id'] or manifest['handoff_version']!=spec['meta']['handoff_version'] or manifest['baseline']!=spec['baseline'] or manifest['linked_handoffs']!=spec['dependencies']: raise b.Invalid('Manifest binding differs')
        schema=json.loads(b.codec('decode',files[roles['schema']].decode()))
        if b.canonical(schema)!=b.canonical(SCHEMA): raise b.Invalid('Public schema differs')
        for role,wanted in [('objects',{'objects':spec['objects']}),('technical_decisions',{'decisions':spec['developer_decisions']}),('architecture',spec['architecture']),('references',{'references':spec['references']})]:
            if json.loads(b.codec('decode',files[roles[role]].decode()))!=wanted: raise b.Invalid('Projection differs: '+role)
        report=json.loads(b.codec('decode',files[roles['readiness']].decode()))
        if report['decision']!='DELIVERABLE' or report['spec_sha256']!=d.revision(spec) or any(report['open_counts'].values()) or any(r['status']!='PASS' for r in report['layers']) or len(report['rounds'])<2 or any(r['status']!='PASS' or r['new_open_count']!=0 or r['reader_count']<3 for r in report['rounds'][-2:]): raise b.Invalid('Release reviews not clean')
        pending=sum(x['status']=='OPEN' for x in spec['developer_decisions'])
        if report.get('technical_open_count')!=pending or report.get('coding_readiness')!=('READY_FOR_DEVELOPER_DECISIONS' if pending else 'READY_FOR_CODING'): raise b.Invalid('Technical readiness differs')
        for media in spec['media']:
            if media['path'] not in files or b.digest(files[media['path']])!=media['sha256']: raise b.Invalid('Media differs')
        contracts=json.loads(b.codec('decode',files[roles['dependency_contracts']].decode()))['contracts']
        byid={x['development_id']:x for x in contracts}
        if len(byid)!=len(contracts) or set(byid)!={x['development_id'] for x in spec['dependencies']}: raise b.Invalid('Dependency content missing')
        for dep in spec['dependencies']:
            if byid[dep['development_id']]['version']!=dep['version'] or byid[dep['development_id']]['contract']!=dep['contract'] or not byid[dep['development_id']].get('content'): raise b.Invalid('Dependency contract differs')
        if spec['meta']['mode']=='UPDATE':
            if not {'baseline','baseline_spec','changes'}<=set(roles): raise b.Invalid('Baseline content/delta missing')
            baseline=json.loads(b.codec('decode',files[roles['baseline_spec']].decode()));delta=json.loads(b.codec('decode',files[roles['changes']].decode()))
            if d.revision(baseline)!=spec['baseline']['spec_sha256'] or delta!=d.changes(baseline,spec): raise b.Invalid('Baseline/delta differs')
        verify_references(spec,files)
        filename='handoff-'+spec['meta']['development_name']+'-'+spec['meta']['handoff_version']+'.zip'
        if (expected_name or Path(path).name)!=filename: raise b.Invalid('ZIP filename differs')
        if 'excel' in roles:
            with tempfile.TemporaryDirectory(prefix='spec-view-check-') as temp:
                book=Path(temp)/roles['excel'];book.write_bytes(files[roles['excel']]);d.verify_excel(spec,book)
    return {'status':'PASS','files':len(names),'manifestSha256':b.digest(manifest_data),'specSha256':d.revision(spec),
      'scope':'Self-contained local artifact verification; not fresh semantic or SAP execution'}

def package(doc,output,assets_root,include_excel=True):
    import delivery as d
    spec,control=state(doc)
    if control.get('batch_required') or any(x.get('requires_change') for x in control.get('dependency_contracts',[])):
        raise b.Invalid('Linked changes require handoff-batch; do not deliver one final ZIP early')
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    filename='handoff-'+spec['meta']['development_name']+'-'+spec['meta']['handoff_version']+'.zip';b.safe_name(filename)
    target=out/filename
    if target.exists(): raise b.Invalid('Immutable version already delivered')
    files,_=build(doc,assets_root,include_excel)
    with tempfile.TemporaryDirectory(dir=out,prefix='spec-candidate-') as temp:
        staged=Path(temp)/filename;write_zip(files,staged);result=verify(staged)
        with target.open('xb') as handle: handle.write(staged.read_bytes())
    control.setdefault('delivery_history',[]).append({'version':spec['meta']['handoff_version'],'spec_sha256':d.revision(spec),'zip_sha256':b.digest(target.read_bytes())})
    return {'path':str(target),'zipSha256':b.digest(target.read_bytes()),'manifestSha256':result['manifestSha256'],'verification':result}

def batch(items,output,batch_id,include_excel=True):
    import delivery as d
    b.safe_name(batch_id)
    if '/' in batch_id: raise b.Invalid('Batch ID must be one path component')
    if not items: raise b.Invalid('Batch needs at least one development')
    docs={};slugs=set();prepared=[];mutations={}
    for item in items:
        doc=item['doc'];spec,_=state(doc);identity=spec['meta']['development_id'];slug=spec['meta']['development_name']
        if identity in docs or slug in slugs: raise b.Invalid('Batch development IDs/short names must be unique')
        docs[identity]=doc;slugs.add(slug)
        for obj in spec['objects']:
            if obj['operation'] in ('NEW','CHANGE'):
                key=(obj['object_type'],obj['name'])
                if key in mutations: raise b.Invalid('Two developments mutate the same technical object')
                mutations[key]=identity
    edges={key:set() for key in docs}
    for identity,doc in docs.items():
        spec,_=state(doc);orders=[x['implementation_order'] for x in spec['dependencies']]
        if len(orders)!=len(set(orders)): raise b.Invalid('Dependency rollout order is ambiguous')
        edges[identity]={x['development_id'] for x in spec['dependencies'] if x['development_id'] in docs}
    ordered=[];pending=set(docs)
    while pending:
        ready=sorted(x for x in pending if not edges[x]&pending)
        if not ready: raise b.Invalid('Cyclic batch rollout dependencies')
        ordered+=ready;pending-=set(ready)
    for item in items:
        doc=item['doc'];spec,_=state(doc);contracts=dependency_records(doc)
        for dep in spec['dependencies']:
            row=contracts.get(dep['development_id'],{})
            if row.get('requires_change') is True and dep['development_id'] not in docs: raise b.Invalid('Affected development ZIP missing from batch')
            if dep['development_id'] in docs:
                partner,_=state(docs[dep['development_id']])
                if dep['version']!=partner['meta']['handoff_version'] or dep['handoff_name']!='handoff-'+partner['meta']['development_name']+'-'+partner['meta']['handoff_version']+'.zip' or row.get('spec_sha256')!=d.revision(partner): raise b.Invalid('Batch dependency/version/content binding differs')
                pointer=row.get('source_pointer')
                if not isinstance(pointer,str) or not pointer.startswith('/'):
                    raise b.Invalid('Linked contract needs an exact source pointer')
                try: expected=d.resolve(partner,pointer)
                except (b.Invalid,KeyError,IndexError,TypeError): raise b.Invalid('Linked contract source pointer missing')
                if row.get('content')!=expected: raise b.Invalid('Packaged linked contract differs from partner')
        files,_=build(doc,item['assets_root'],include_excel);filename='handoff-'+spec['meta']['development_name']+'-'+spec['meta']['handoff_version']+'.zip'
        prepared.append((doc,filename,files))
    out=Path(output).resolve();out.mkdir(parents=True,exist_ok=True);target=out/batch_id
    if target.exists(): raise b.Invalid('Immutable batch already delivered')
    results=[]
    with tempfile.TemporaryDirectory(dir=out,prefix='batch-candidate-') as temporary:
        staged=Path(temporary)/batch_id;staged.mkdir()
        for doc,filename,files in prepared:
            archive=staged/filename;write_zip(files,archive);verified=verify(archive)
            results.append({'filename':filename,'zipSha256':b.digest(archive.read_bytes()),'verification':verified})
        # One directory publication exposes all separately verified ZIPs together.
        staged.rename(target)
    for doc,filename,_ in prepared:
        spec,control=state(doc);entry=next(x for x in results if x['filename']==filename)
        control.setdefault('delivery_history',[]).append({'version':spec['meta']['handoff_version'],'spec_sha256':d.revision(spec),'zip_sha256':entry['zipSha256']})
        entry['path']=str(target/filename)
    return {'status':'DELIVERED','path':str(target),'zip_files':results,'delivery_order':ordered,'scope':'Separate development ZIPs atomically published after all gates'}
