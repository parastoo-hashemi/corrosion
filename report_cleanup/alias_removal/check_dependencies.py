"""Check historical path records against the folder map without rewriting evidence."""
from pathlib import Path
import csv
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from corrosion.research_paths import LEGACY_FOLDERS, resolve_project_path

def strings(value):
    if isinstance(value,str):yield value
    elif isinstance(value,dict):
        for key,item in value.items():
            yield from strings(key)
            yield from strings(item)
    elif isinstance(value,list):
        for item in value:yield from strings(item)

def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

mode=sys.argv[1] if len(sys.argv)>1 else 'after'
if mode=='before':
    target=OUT/'references_resolved_before.json'
    assert not target.exists(), 'The before record is frozen.'
    records=[]
    for entry in json.loads((OUT/'references_before.json').read_text()):
        source=ROOT/entry['file']
        if source.suffix=='.json':values=strings(json.loads(source.read_text()))
        elif source.suffix=='.csv':
            with source.open(newline='') as stream:values=list(strings(list(csv.DictReader(stream))))
        else:continue
        for value in sorted(set(values)):
            if not any(value==k or value.startswith(k+'/') for k in LEGACY_FOLDERS):continue
            old=ROOT/value;new=resolve_project_path(value)
            records.append(dict(source=entry['file'],recorded_path=value,current_path=str(new.relative_to(ROOT)),
                                existed_before=old.exists(),same_target_before=old.resolve()==new))
    target.write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(dict(records=len(records),existing=sum(r['existed_before'] for r in records),
                         mismatched_existing_targets=[r for r in records if r['existed_before'] and not r['same_target_before']]),indent=2))
else:
    assert mode=='after'
    records=json.loads((OUT/'references_resolved_before.json').read_text())
    failures=[];resolved=[]
    for record in records:
        path=resolve_project_path(record['recorded_path'])
        if str(path.relative_to(ROOT))!=record['current_path']:
            failures.append('Changed mapping: '+record['recorded_path'])
        if record['existed_before'] and not path.exists():
            failures.append('Lost dependency: '+record['recorded_path'])
        resolved.append(dict(**record,exists_after=path.exists()))
    # The standalone report-script adapter must use the same mapping.
    sys.path.insert(0,str(ROOT/'report_v2/scripts'))
    from _project_paths import resolve_project_path as report_path
    assert report_path('main_4/outputs/data/master_table.csv')==ROOT/'structural_capacity/outputs/data/master_table.csv'
    expected=json.loads((ROOT/'report_cleanup/renaming/folder_map.json').read_text())
    assert LEGACY_FOLDERS==expected
    result=dict(passed=not failures,failures=failures,records=len(records),
                existing_dependencies_preserved=sum(r['existed_before'] and r['exists_after'] for r in resolved),
                preexisting_missing=[r for r in resolved if not r['existed_before']],resolved=resolved)
    (OUT/'references_resolved_after.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'resolved','preexisting_missing'}},indent=2))
    print('Previously unavailable historical references:',len(result['preexisting_missing']))
    raise SystemExit(bool(failures))
