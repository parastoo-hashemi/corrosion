from pathlib import Path
import sys,json,joblib,warnings,hashlib
import numpy as np,pandas as pd
R=Path(__file__).resolve().parents[2];mode=sys.argv[1];folder='main' if mode=='before' else 'classical_corrosion';rows=[]
assert mode == 'after', 'The before record is frozen; only after checks may be rerun.'
with warnings.catch_warnings():
 warnings.simplefilter('ignore')
 for p in sorted((R/folder/'artifacts').glob('*_model.joblib')):
  model=joblib.load(p);cols=list(model.feature_names_in_)
  samples=[]
  for week in [4,12,28]:
   d={c:0.0 for c in cols};d.update(N_Steel_Mesh=7,Treatment='NO',**{'NaCl%':3.5,'Ageing_Days':196,'Cover_(Faliure_Surface)_[mm]':6.0,'week':week,'series':'S'})
   samples.append({c:d[c] for c in cols})
  x=pd.DataFrame(samples,columns=cols);a=np.asarray(model.predict(x))
  rows.append({'model':p.name,'input_columns':cols,'predictions':a.tolist(),'array_sha256':hashlib.sha256(a.tobytes()).hexdigest()})
 # Frozen neural head only; no image-backbone download or training.
 import torch,importlib
 sys.path.insert(0,str(R.parent));name='main_2' if mode=='before' else 'image_embeddings'
 cls=importlib.import_module('corrosion.'+name+'.models').RegressionMLP
 info=json.loads((R/name/'artifacts/run_info.json').read_text());n=int(info['phase2_model']['input_dim'])
 model=cls(n,dropout=0.0);model.load_state_dict(torch.load(R/name/'artifacts/best_model_state.pt',map_location='cpu',weights_only=True));model.eval()
 with torch.no_grad():pred=model(torch.zeros((3,n))).numpy()
 rows.append({'model':'embedding_neural_head','predictions':pred.tolist(),'array_sha256':hashlib.sha256(pred.tobytes()).hexdigest()})
(Path(__file__).resolve().parent / ('predictions_'+mode+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
print('Read-only synthetic-input prediction probes:',len(rows))
