"""Check final manuscripts, evidence-linked numbers, references, and frozen files.

The numeric inventory is a lint aid, not a substitute for the recorded manual
scientific review: coincident numbers alone do not establish provenance.
"""
from pathlib import Path
import csv,hashlib,json,re,subprocess,sys
import pandas as pd
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'report_v2'
QA=OUT/'qa/v3' if (OUT/'thesis/v3/thesis.tex').exists() else OUT/'qa'
QA.mkdir(parents=True,exist_ok=True)
claims=json.loads((OUT/'evidence/claims.json').read_text())
paired=json.loads((OUT/'evidence/paired_diagnostics.json').read_text())
number_sources={}
def addnum(value,source):
 if isinstance(value,bool):return
 if isinstance(value,(int,float)):
  if not pd.notna(value):return
  for places in range(7):
   s=f'{value:.{places}f}'
   number_sources.setdefault(s,set()).add(source)
   if s.startswith('0.'):number_sources.setdefault(s[1:],set()).add(source)
   if s.startswith('-0.'):number_sources.setdefault('-'+s[2:],set()).add(source)
 elif isinstance(value,list):
  for item in value:addnum(item,source)
 elif isinstance(value,dict):
  for item in value.values():addnum(item,source)
for c in claims:addnum(c['value'],' | '.join(c['sources']))
addnum(paired,'report_v2/evidence/paired_diagnostics.json')
v3checks=OUT/'evidence/v3/figure_checks.json'
if v3checks.exists():
 v3=json.loads(v3checks.read_text())
 addnum(v3,str(v3checks.relative_to(ROOT)))
 for path,expected in v3['sources'].items():
  assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
for p in (OUT/'tables').glob('*.csv'):
 d=pd.read_csv(p)
 for col in d.select_dtypes(include='number'):addnum(d[col].tolist(),str(p.relative_to(ROOT)))
pool=pd.read_csv(OUT/'tables/pooled_capacity.csv').set_index('feature_set_name')
addnum(float(pool.loc['metadata_hsv','mae_mean']-pool.loc['metadata_only','mae_mean']),'main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison.csv (difference)')
addnum(3996,'Data/splits/{train,val,test}_manifest.csv (sum)')
# Pure notation, dates, versions and numbering are not empirical estimates.
bib=(OUT/'references/references.bib').read_text();bibkeys=set(re.findall(r'@\w+\{([^,]+),',bib))
masters=[OUT/'thesis/thesis.tex',OUT/'article/article.tex',OUT/'thesis/v2/thesis.tex',OUT/'article/v2/article.tex']
masters += [p for p in [OUT/'thesis/v3/thesis.tex',OUT/'article/v3/article.tex'] if p.exists()]
rows=[];pdfs=[];issues=[]
for p in masters:
 tex=p.read_text();files=[p]
 for include in re.findall(r'\\(?:include|input)\{(chapters/[^}]+)\}',tex):files.append(p.parent/(include+'.tex'))
 combined='\n'.join(f.read_text() for f in files)
 used=set()
 for c in re.findall(r'\\cite\w*(?:\[[^]]*\])*(?:\{([^}]+)\})',combined):used.update(c.split(','))
 assert used<=bibkeys,(p,used-bibkeys)
 assert not re.search(r'\\cite\w*\{\s*\}',combined)
 for phrase in [r'\bthe one structural quantity\b',r'\bthe only structural quantity\b',r'\bthe classifier achieves\b',r'\bproves\b']:
  assert not re.search(phrase,combined,re.I),(p,phrase)
 for f in files:
  for ln,line in enumerate(f.read_text().splitlines(),1):
   if line.lstrip().startswith('%'):continue
   # Captions/prose only; commands and mathematical/typographic literals are separate.
   if line.startswith(('\\documentclass','\\usepackage','\\newcommand','\\expandafter','\\set','\\title','\\author','\\hypersetup','\\renewcommand','\\makeatletter')):continue
   if line.startswith(('\\begin{','\\end{','\\input{','\\include{','\\label{','\\hspace','\\vspace')):continue
   clean=re.sub(r'\\cite\w*(?:\[[^]]*\])*\{[^}]*\}','',line)
   clean=re.sub(r'\\(?:ref|label|path|texttt)\{[^}]*\}','',clean)
   clean=re.sub(r'\\fig\{[^}]+\}\{[^}]+\}','',clean)
   # TeX en-dash ranges are not negative measurements (e.g. 1.60--2.87).
   clean=re.sub(r'(?<=\d)--(?=\d)', ' to ', clean)
   nums=re.findall(r'(?<![A-Za-z0-9_])[-+]?\d*\.\d+|(?<![A-Za-z0-9_])\d+(?![A-Za-z0-9_])',clean)
   if not nums:continue
   candidates={};unknown=[]
   for n in nums:
    normalized=n.lstrip('+').replace(',','')
    if normalized in number_sources:candidates[n]=sorted(number_sources[normalized])[:5]
    elif '.' in normalized:unknown.append(n)
   context='typographic/notation' if '\\' in line and not any(w in line for w in ['MAE','specimen','fold','rust','mean','load','corrosion','threshold','label','model','observation','R^2','caption']) else 'scientific prose/table/caption'
   if unknown and context.startswith('scientific'):issues.append(dict(file=str(f.relative_to(ROOT)),line=ln,unknown=unknown,text=line))
   rows.append(dict(document=str(p.relative_to(ROOT)),file=str(f.relative_to(ROOT)),line=ln,kind=context,numbers=' | '.join(nums),numeric_matches=json.dumps(candidates),text=line))
 pdf=p.with_suffix('.pdf');reader=PdfReader(pdf);text='\n'.join(page.extract_text() or '' for page in reader.pages)
 assert '?'*2 not in text,(pdf,'unresolved marker')
 log=p.with_suffix('.log').read_text(errors='replace')
 assert not re.search(r'Overfull|Missing character|undefined|Warning:|pdfTeX warning|Rerun to get cross-references right|^!',log,re.I|re.M),(pdf,'compile issue')
 pdfs.append(dict(pdf=str(pdf.relative_to(ROOT)),pages=len(reader.pages),citations=len(used),sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),overfull_boxes=0))
with (QA/'numeric_claim_inventory.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
(QA/'numeric_lint_exceptions.json').write_text(json.dumps(issues,indent=2)+'\n')
assert not issues,issues
frozen=json.loads((OUT/'evidence/frozen_report_hashes.json').read_text())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in frozen.items())
for row in pd.read_csv(OUT/'tables/source_hashes.csv').itertuples():
 assert hashlib.sha256((ROOT/row.path).read_bytes()).hexdigest()==row.sha256,row.path
for path,expected in paired['sources'].items():
 assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
# Verify every generated vector figure against its own provenance record.
figs=json.loads((OUT/'figures/PROVENANCE.json').read_text())+[json.loads((OUT/'figures/PAIRED_PROVENANCE.json').read_text())]
for fig in figs:
 assert hashlib.sha256((ROOT/fig['figure']).read_bytes()).hexdigest()==fig['sha256']
 for source in fig['source_files']:assert (ROOT/source).exists()
 for source,expected in fig.get('source_sha256',{}).items():
  assert hashlib.sha256((ROOT/source).read_bytes()).hexdigest()==expected,source
 if 'png_sha256' in fig:
  assert hashlib.sha256((ROOT/fig['figure']).with_suffix('.png').read_bytes()).hexdigest()==fig['png_sha256']
preservation={}
if (OUT/'evidence/v3/preserved_files.json').exists():
 saved=json.loads((OUT/'evidence/v3/preserved_files.json').read_text())
 ledger_paths={'report_v2/figures/PROVENANCE.json','report_v2/figures/PROVENANCE.md'}
 for path,expected in saved.items():
  if path not in ledger_paths:
   assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,('changed earlier artifact',path)
 # Provenance is the only authorized extension of an earlier shared file.
 baseline_json=subprocess.check_output(['git','show','c5a4f1a:report_v2/figures/PROVENANCE.json'],cwd=ROOT)
 baseline_md=subprocess.check_output(['git','show','c5a4f1a:report_v2/figures/PROVENANCE.md'],cwd=ROOT)
 assert json.loads((OUT/'figures/PROVENANCE.json').read_text())[:7]==json.loads(baseline_json)
 assert (OUT/'figures/PROVENANCE.md').read_bytes().startswith(baseline_md)
 # Check every earlier tracked manuscript too, beyond the pre-edit manifest.
 tracked=subprocess.check_output(['git','ls-tree','-r','--name-only','c5a4f1a','report_v2/thesis','report_v2/article'],cwd=ROOT,text=True).splitlines()
 for path in tracked:
  assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',f'c5a4f1a:{path}'],cwd=ROOT),path
 for row in json.loads((OUT/'evidence/v3/candidate_inventory.json').read_text()):
  assert hashlib.sha256((ROOT/row['candidate']).read_bytes()).hexdigest()==row['sha256'],row['candidate']
 preservation=dict(preexisting_files_verified=len(saved)-2,earlier_tracked_manuscripts_verified=len(tracked),original_provenance_entries_unchanged=True,candidate_files_unchanged=30)
 (QA/'preservation_check.json').write_text(json.dumps(preservation,indent=2)+'\n')
result=dict(documents=pdfs,figure_count=len(figs),numeric_lines=len(rows),numeric_lint_exceptions=0,frozen_report_unchanged=True,scope='Numeric matching is supplemented by manual scientific and grammar review in FINAL_VERIFICATION.md.')
result['preservation']=preservation
if v3checks.exists():result['scope']+=' V3 additions are reviewed in thesis/v3/FIGURE_AUDIT.md and qa/v3/VERIFICATION.md.'
(QA/'final_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
