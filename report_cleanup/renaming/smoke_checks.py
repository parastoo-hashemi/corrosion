"""Read-only runtime checks for the renamed entry points; no training or builds."""
from pathlib import Path
import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
PYTHON = sys.executable
CASES = []

def case(name, args, cwd=ROOT):
    CASES.append((name, [PYTHON, '-B', *args], cwd))

for tests in ['tests', 'condition_assessment/tests']:
    case(tests, ['-m', 'unittest', 'discover', '-s', tests])
for name in ['classical_corrosion']:
    case(name + ' imports and classical artifact bundle', ['-c',
        f'from corrosion.{name}.api import health; result=health(); print(result); assert result["models_loaded"]'])
    CASES[-1] = (*CASES[-1][:2], ROOT.parent)
for name in ['image_embeddings']:
    case(name + ' module imports', ['-c',
        f'import corrosion.{name}.api; import corrosion.{name}.train_phase2; print("imports OK; no backbone loading")'], ROOT.parent)
for name in ['corrosion.classical_corrosion.train_models','corrosion.image_embeddings.train_phase2']:
    case(name + ' help', ['-m', name, '--help'], ROOT.parent)
for name in ['augment_dataset.py','make_splits.py','create_dataset_variants.py',
             'scripts/measure_image_statistics.py','scripts/plot_augmentation_examples.py',
             'scripts/plot_luminance_extremes.py','scripts/plot_luminance_histogram.py']:
    case(name + ' help', ['classification_data_preparation/'+name,'--help'])
case('condition assessment configured roots', ['-c', '''
import sys
from pathlib import Path
root=Path.cwd(); sys.path.insert(0,str(root/'condition_assessment'))
from src.config import load_settings
s=load_settings(); assert s.project_root==root/'condition_assessment'
assert s.repo_root==root; assert s.paths.excel_path.is_file()
assert s.paths.outputs_dir==root/'condition_assessment/outputs'
print('configured roots OK; no output initialization')
'''])
for folder in ['structural_capacity','archive/structural_baseline_snapshot']:
    case(folder + ' configured roots', ['-c', '''
import sys
from pathlib import Path
root=Path.cwd(); sys.path.insert(0,str(root/'src'))
from corrosion_proxy_rul.utils_paths import ROOT_DIR,CONFIG_DIR,DATA_DIR,OUTPUT_DIR
from corrosion_proxy_rul.config import load_configs
assert ROOT_DIR==root; assert all(p.is_dir() for p in [CONFIG_DIR,DATA_DIR,OUTPUT_DIR])
x=load_configs(); print('config keys:', sorted(x)); assert 'dataset' in x
'''], ROOT/folder)
case('six relocated artifact lookups', ['-c', '''
from pathlib import Path
import json
from corrosion.research_paths import resolve_artifact_path
root=Path.cwd()/'corrosion'
a=root/'classical_corrosion/artifacts'
records=[(v['model_path'],a) for v in json.loads((a/'manifest.json').read_text())['models'].values()]
b=root/'image_embeddings/artifacts'
records += [(v,b) for v in json.loads((b/'run_info.json').read_text())['phase2_model']['artifacts'].values()]
for value,bundle in records:
 p=resolve_artifact_path(value,bundle); assert p.parent==bundle; assert p.is_file()
print('resolved',len(records),'recorded paths inside canonical bundles')
'''], ROOT.parent)

with tempfile.TemporaryDirectory(prefix='corrosion_check_') as temp:
    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1',
             OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', MPLCONFIGDIR=temp)
    def run(item):
        name, cmd, cwd=item
        try:
            p=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,timeout=60)
            return dict(name=name,command=cmd,cwd=str(cwd),exit_code=p.returncode,
                        stdout=p.stdout,stderr=p.stderr)
        except subprocess.TimeoutExpired as e:
            return dict(name=name,command=cmd,cwd=str(cwd),exit_code=-1,error=str(e))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(run,CASES))
(OUT/'smoke_after.json').write_text(json.dumps(results,indent=2)+'\n')
failed=[r['name'] for r in results if r['exit_code']]
print(json.dumps(dict(checks=len(results),passed=len(results)-len(failed),failed=failed),indent=2))
raise SystemExit(bool(failed))
