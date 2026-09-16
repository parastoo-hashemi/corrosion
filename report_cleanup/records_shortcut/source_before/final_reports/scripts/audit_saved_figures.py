"""Verify saved figure inputs and replay only pure plotting functions; never fit models.

Extracting explicitly named AST function definitions avoids importing pipeline
orchestration or invoking today's corrupted `main_first` aggregation paths.
All replay outputs stay in qa/v3, never in the source generations.
"""
from pathlib import Path
from _project_paths import resolve_project_path
import ast, hashlib, json, re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'final_reports'; QA=OUT/'records/qa/v3'; EV=OUT/'records/evidence/v3'
QA.mkdir(exist_ok=True); EV.mkdir(exist_ok=True)
P=ROOT/'structural_capacity/outputs/ultimate_load_refocus'
R=P/'pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge'
sources={}
def read(path):
 path=Path(path); sources[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
 return pd.read_parquet(path) if path.suffix=='.parquet' else pd.read_csv(path)
def funcs(path,names):
 sources[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
 nodes=[n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names]
 assert {n.name for n in nodes}==set(names)
 ns=dict(Path=Path,pd=pd,np=np,plt=plt,sns=sns,ensure_dir=lambda p:p.mkdir(parents=True,exist_ok=True))
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
 return ns
inv=json.loads((EV/'candidate_inventory.json').read_text()); replays={}
def replay(cid,fn,*args,**kwargs):
 dest=QA/(cid+'_replay.png')
 fn(*args,**kwargs,**({'out_path':dest} if cid.startswith('M3') else {'path':dest}))
 candidate=resolve_project_path(next(x['candidate'] for x in inv if x['id']==cid))
 a,b=Image.open(candidate).convert('RGB'),Image.open(dest).convert('RGB')
 replays[cid]={'replayed_pure_plot':True,'original_size':a.size,'replayed_size':b.size,
 'pixels_identical':a.size==b.size and np.array_equal(np.asarray(a),np.asarray(b)),
 'output':str(dest.relative_to(ROOT))}
# Historical main_3 data: no model fitting, no feature extraction.
D=ROOT/'condition_assessment/outputs'
c=read(D/'canonical_dataset.csv'); f=read(D/'image_features.csv'); m=c.merge(f,on='record_id',validate='one_to_one')
reg=read(D/'corrosion_regression_metrics.csv'); dmg=read(D/'damage_regression_metrics.csv'); cl=read(D/'corrosion_classification_metrics.csv')
cp=read(D/'corrosion_regression_predictions.parquet'); dp=read(D/'damage_regression_predictions.parquet')
rul=read(D/'rul_estimates.csv'); traj=read(D/'degradation_forecasts.parquet')
names=['_save','plot_regression_predictions','plot_metric_bars','plot_risk_distribution','plot_rul_histogram','plot_trajectory_examples']
ns=funcs(ROOT/'condition_assessment/src/visualization/plots.py',names); sns.set_theme(style='whitegrid',context='talk')
for cid,frame,metric,title in [('M3-04',cl,'macro_f1','Corrosion classification comparison'),('M3-05',reg,'mae','Corrosion model comparison'),('M3-07',dmg,'mae','Damage model comparison')]:
 replay(cid,ns['plot_metric_bars'],frame[frame.strategy=='group_shuffle'],metric_col=metric,title=title)
for cid,frame,title in [('M3-06',cp,'Corrosion regression parity'),('M3-08',dp,'Damage regression parity')]:
 replay(cid,ns['plot_regression_predictions'],frame[frame.strategy=='group_shuffle'],title=title)
replay('M3-15',ns['plot_risk_distribution'],rul)
replay('M3-16',ns['plot_rul_histogram'],rul)
ids=rul.sort_values(['failure_probability','estimated_rul_weeks'],ascending=[False,True]).specimen_id.head(6).tolist()
replay('M3-11',ns['plot_trajectory_examples'],traj,target='peak_rust_pct',specimen_ids=ids)
# Verify all Ridge aggregation semantics directly from saved per-fold predictions.
fold=read(R/'terminal_fold_predictions.csv'); oof=read(R/'terminal_oof_predictions.csv')
metrics=read(R/'fold_metrics.csv'); importance=read(R/'feature_importance_full_fit.csv')
lc=read(R/'learning_curve_raw.csv'); summary=read(R/'learning_curve_summary.csv'); pdp=read(R/'partial_dependence.csv')
assert len(fold)==96 and len(oof)==48 and len(metrics)==10 and len(lc)==50 and len(importance)==11
assert fold.groupby('specimen_id').size().eq(2).all() and oof.prediction_count.eq(2).all()
assert fold.is_measured_ultimate_load.all() and oof.is_measured_ultimate_load.all()
g=fold.groupby('sample_name').predicted_ultimate_load_kn.agg(['mean','std','count']); o=oof.set_index('sample_name').loc[g.index]
np.testing.assert_allclose(g['mean'],o.predicted_ultimate_load_kn,atol=1e-12)
np.testing.assert_allclose(g['std'],o.predicted_ultimate_load_kn_std,atol=1e-12)
np.testing.assert_allclose(o.residual,o.predicted_ultimate_load_kn-o.ultimate_load_kn,atol=1e-12)
np.testing.assert_allclose(o.abs_error,o.residual.abs(),atol=1e-12)
for col in ['n_train_specimens','n_train_rows','train_mae','test_mae','train_rmse','test_rmse','train_spearman','test_spearman']:
 a=lc.groupby('fraction')[col].agg(['mean','std']); b=summary.set_index('fraction').loc[a.index]
 for stat in ['mean','std']:np.testing.assert_allclose(a[stat],b[col+'_'+stat],atol=1e-12)
np.testing.assert_allclose(lc[lc.fraction==1].sort_values('split_id').test_mae,metrics.sort_values('split_id').test_mae,atol=1e-12)
manifest=read(P/'splits/grouped_cv_specimen_manifest.csv')
for sid,part in manifest.groupby('split_id'):
 train=set(part.loc[part.membership=='train','specimen_id']); test=set(part.loc[part.membership=='test','specimen_id'])
 assert not train&test and len(train|test)==48
 assert set(fold.loc[fold.split_id==sid,'specimen_id'])==test
# Check source table reproduces every plotted top-level bar/heatmap value.
best=read(P/'pooled_all_weeks/grouped_cv/feature_set_comparison.csv'); allm=read(P/'pooled_all_weeks/grouped_cv/model_comparison.csv')
assert len(best)==7 and len(allm)==35
balance={}
for regime in ['grouped_cv','leave_one_campaign_out']:
 b=read(P/f'splits/{regime}_balance_summary.csv'); man=read(P/f'splits/{regime}_specimen_manifest.csv')
 for row in b.itertuples():
  part=man[(man.split_id==row.split_id)&(man.membership=='test')]
  assert part.specimen_id.nunique()==row.test_specimens
  assert part.groupby('n_steel_mesh').specimen_id.nunique().to_dict()=={int(k):v for k,v in json.loads(row.test_mesh_counts).items()}
 balance[regime]=b[['split_id','test_specimens','test_mesh_counts']].to_dict('records')
names=['plot_prediction_vs_truth','plot_residuals','plot_error_histogram','plot_feature_importance','plot_partial_dependence','plot_cv_stability','plot_uncertainty','plot_learning_curve','plot_model_metric_heatmap','plot_best_feature_set_bars']
ns=funcs(ROOT/'structural_capacity/src/corrosion_proxy_rul/ultimate_load_refocus.py',names); sns.set_theme(style='whitegrid')
base='pooled_all_weeks | metadata-only | Ridge'
for cid,fn,frame,suffix in [('R-01','plot_cv_stability',metrics,'Fold-to-fold stability'),('R-02','plot_error_histogram',oof,'Error distribution'),('R-03','plot_feature_importance',importance,'Feature importance'),('R-04','plot_learning_curve',summary,'Learning curve'),('R-05','plot_partial_dependence',pdp,'Partial dependence'),('R-06','plot_prediction_vs_truth',oof,'Prediction vs ground truth'),('R-07','plot_residuals',oof,'Residual analysis'),('R-08','plot_uncertainty',oof,'Approximate uncertainty')]:
 replay(cid,ns[fn],frame,title=base+'\n'+suffix,**({'top_n':20} if cid=='R-03' else {}))
replay('M4-01',ns['plot_best_feature_set_bars'],best,title='pooled_all_weeks | grouped_cv | Best model per feature set')
replay('M4-05',ns['plot_model_metric_heatmap'],allm,title='pooled_all_weeks | grouped_cv | Model and feature-set comparison')
# PDF identity is assessed separately from PNG copying; no claim of identical drafts.
pdfs={}
for cid,path in [('M3-01',ROOT/'condition_assessment/reports/corrosion_condition_pipeline_ieee.pdf'),('M4-06',ROOT/'structural_capacity/outputs/reports/ultimate_load_refocus_ieee.pdf')]:
 cand=resolve_project_path(next(x['candidate'] for x in inv if x['id']==cid))
 a,b=PdfReader(cand),PdfReader(path)
 norm=lambda doc:re.sub(r'\s+','', ''.join(p.extract_text() or '' for p in doc.pages))
 pdfs[cid]={'candidate_pages':len(a.pages),'canonical_pages':len(b.pages),'normalized_text_identical':norm(a)==norm(b),'canonical_pdf':str(path.relative_to(ROOT))}
# Record inspected numeric ranges and diagnostics, with no new estimate of model performance.
correlations={}
for x,y in [('surface_total_rust_pct','rust_area_pct_feature'),('peak_rust_pct','peak_rust_pct_feature'),('peak_rust_location_cm','peak_rust_location_cm_feature')]:
 correlations[x]={'pearson':float(m[[x,y]].corr().iloc[0,1]),'complete_pairs':int(m[[x,y]].dropna().shape[0])}
result={'sources':sources,'plot_replays':replays,'pdf_comparison':pdfs,'main3':{
 'rows':len(c),'specimens':c.specimen_id.nunique(),'feature_alignment':correlations,
 'risk_counts':rul.risk_class.value_counts().to_dict(),'rul_finite':int(rul.estimated_rul_weeks.notna().sum()),'rul_zero':int(rul.estimated_rul_weeks.eq(0).sum()),
 'rul_max':float(rul.estimated_rul_weeks.max()),'trajectory_selection':ids,
 'corrosion_parity_targets':cp.loc[cp.strategy=='group_shuffle','target'].unique().tolist(),
 'damage_parity_targets':dp.loc[dp.strategy=='group_shuffle','target'].unique().tolist()},
 'ridge':{'specimens':48,'per_fold_predictions':96,'prediction_count_per_specimen':2,
 'observed_range':o.ultimate_load_kn.agg(['min','max']).tolist(),'predicted_mean_range':o.predicted_ultimate_load_kn.agg(['min','max']).tolist(),
 'residual_range':o.residual.agg(['min','max']).tolist(),'averaged_prediction_mae':float(o.abs_error.mean()),
 'fold_mean_mae':float(metrics.test_mae.mean()),'mean_absolute_error_over_96_predictions':float(fold.abs_error.mean()),
 'mesh_counts':o.n_steel_mesh.value_counts().to_dict(),'learning_curve':summary.to_dict('records'),
 'training_specimens_per_fraction':{str(k):sorted(v.unique().tolist()) for k,v in lc.groupby('fraction').n_train_specimens},
 'coefficients':importance.to_dict('records')},'split_balance':balance,
 'limitations':['Plot-only replays do not validate the historical fitted models.','Current source aggregation contains main_first corruption; no pipeline was imported, repaired, or refitted.','Meeting-report panel generators were not located; checked saved data and canonical PNG identities where possible.','Pixel identity is recorded explicitly and never assumed from numerical agreement.']}
(EV/'figure_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'replayed':len(replays),'pixel_identical':[k for k,v in replays.items() if v['pixels_identical']],'pdfs':pdfs,'main3_alignment':correlations,'ridge_mae_of_mean_predictions':result['ridge']['averaged_prediction_mae']},indent=2))
