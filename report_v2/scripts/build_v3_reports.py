"""Compile only v3; preserve every earlier manuscript/build artifact."""
from pathlib import Path
import re,subprocess
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'report_v2'
for kind in ['thesis','article']:
 p=OUT/kind/'v3'/f'{kind}.tex'
 run=subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error',p.name],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (OUT/'qa/v3'/f'{kind}_build.txt').write_text(run.stdout)
 if run.returncode:raise RuntimeError(run.stdout[-6000:])
 log=p.with_suffix('.log').read_text(errors='replace')
 issues=re.findall(r'^.*(?:Overfull|Missing character|undefined|Warning:|pdfTeX warning|Rerun to get cross-references right|^!).*$',log,re.I|re.M)
 if issues:raise RuntimeError('\n'.join(issues))
 print(f'{kind}: compiled, no errors, unresolved references, warnings or overfull boxes')
