from pathlib import Path
import json,sys,warnings
R=Path(sys.argv[1]); p=R/sys.argv[2];sys.path.insert(0,str(R.parent))
if '/src/' not in str(p):
 for folder in ['main_4/src','main_3']:
  if (R/folder).exists():sys.path.append(str(R/folder))
r={}
with warnings.catch_warnings(record=True) as ws:
 warnings.simplefilter('always')
 try:
  if p.suffix=='.pt':
   import torch
   obj=torch.load(p,map_location='cpu',weights_only=True)
  else:
   import joblib
   obj=joblib.load(p)
  r.update(loaded=True,type=type(obj).__module__+'.'+type(obj).__qualname__)
  if isinstance(obj,dict):r['keys']=sorted(str(k) for k in obj)
 except Exception as e:r.update(loaded=False,error=type(e).__name__+': '+str(e))
 r['warnings']=sorted(set(str(w.message) for w in ws))
print(json.dumps(r))
