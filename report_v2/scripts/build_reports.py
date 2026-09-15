"""Compile all present drafts, enforce clean references, and verify frozen files."""
from pathlib import Path
import subprocess,re,json,hashlib
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'report_v2'
masters=[OUT/'thesis/thesis.tex',OUT/'article/article.tex',OUT/'thesis/v2/thesis.tex',OUT/'article/v2/article.tex']
records=[]
for p in masters:
 if not p.exists():continue
 run=subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error',p.name],cwd=p.parent,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 (OUT/'qa'/f'{p.parent.parent.name}_{p.parent.name}_build.txt').write_text(run.stdout)
 if run.returncode:print(run.stdout[-6500:]);raise SystemExit(run.returncode)
 log=p.with_suffix('.log').read_text(errors='replace')
 errors=re.findall(r'^.*(?:undefined references|undefined citations|Citation .* undefined|Reference .* undefined|Rerun to get cross-references right|! LaTeX Error|! Package .* Error).*$',log,re.M|re.I)
 if errors:raise RuntimeError(f'{p}: {errors}')
 records.append(dict(document=str(p.relative_to(ROOT)),pdf=str(p.with_suffix('.pdf').relative_to(ROOT)),errors=0,unresolved_references=0,overfull_boxes=len(re.findall('Overfull',log)),underfull_boxes=len(re.findall('Underfull',log))))
 print(p.relative_to(ROOT),'compiled;',records[-1]['overfull_boxes'],'overfull boxes')
frozen=json.loads((OUT/'evidence/frozen_report_hashes.json').read_text())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in frozen.items())
(OUT/'qa/build_results.json').write_text(json.dumps(records,indent=2)+'\n')
print('Frozen report hash check: PASS')
