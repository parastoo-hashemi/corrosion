from pathlib import Path
import subprocess,os,json,sys,concurrent.futures
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent;m=json.loads((O/'git_before.json').read_text())['mapping'];mode=sys.argv[1]
assert mode == 'after', 'The before record is frozen; only after checks may be rerun.'
paths=json.loads((O/'model_paths.json').read_text());env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
def probe(old):
 parts=Path(old).parts;new=str(Path(m.get(parts[0],parts[0]),*parts[1:])) if mode=='after' else old
 run=subprocess.run([sys.executable,'-B',str(O/'model_check_one.py'),str(R),new],text=True,capture_output=True,env=env,timeout=60)
 try:out=json.loads(run.stdout.splitlines()[-1])
 except Exception:out={'loaded':False,'error':'Process exit '+str(run.returncode),'stderr':run.stderr[-1200:]}
 return dict(original_path=old,path=new,exit_code=run.returncode,**out)
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for i,r in enumerate(pool.map(probe,paths)):
  rows.append(r)
  (O/f'models_{mode}.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({'count':len(rows),'loaded':sum(r['loaded'] for r in rows),'failures':[{'path':r['original_path'],'error':r.get('error')} for r in rows if not r['loaded']]},indent=2))
