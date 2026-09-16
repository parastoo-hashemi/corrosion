"""Render three additional v3 diagnostics from saved tables; no fitting.

Only ridge_* figure files and v3 evidence are written. Existing figure binaries
and the original provenance entries are preserved. Re-running is idempotent.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'final_reports'
P=ROOT/'structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge'
BLUE='#236192'; ORANGE='#C16B29'; TEAL='#15847B'; GREY='#647583'; INK='#1C2F40'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
ledger=[]; checks={}
def read(name):return pd.read_csv(P/name)
def finish(fig,name,files,description):
 path=OUT/'figures'/f'{name}.pdf'
 fig.savefig(path,pad_inches=.08,metadata={'CreationDate':datetime(2026,9,16,tzinfo=timezone.utc),'ModDate':datetime(2026,9,16,tzinfo=timezone.utc)})
 fig.savefig(path.with_suffix('.png'),dpi=180,pad_inches=.08);plt.close(fig)
 source_files=[str((P/f).relative_to(ROOT)) for f in files]
 ledger.append(dict(figure=str(path.relative_to(ROOT)),script='final_reports/scripts/make_v3_figures.py',source_files=source_files,source_sha256={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in source_files},description=description,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),png_sha256=hashlib.sha256(path.with_suffix('.png').read_bytes()).hexdigest(),generated_utc='2026-09-16T00:00:00+00:00',generation_note='Date fixed for deterministic PDF metadata; not a historical training timestamp.'))
# Baseline parity and error direction, NOT incremental HSV effects.
d=read('terminal_oof_predictions.csv'); assert len(d)==48 and d.prediction_count.eq(2).all()
x=d.ultimate_load_kn; y=d.predicted_ultimate_load_kn; residual=y-x
np.testing.assert_allclose(residual,d.residual,atol=1e-12)
lo=min(x.min(),y.min()); hi=max(x.max(),y.max()); pad=.08*(hi-lo); limits=(lo-pad,hi+pad)
rmax=float(residual.abs().max())*1.12
fig,axes=plt.subplots(1,2,figsize=(7.2,3.15),gridspec_kw={'wspace':.35})
for mesh,col,marker in [(4,ORANGE,'o'),(7,BLUE,'^')]:
 g=d.n_steel_mesh.eq(mesh); assert g.sum()==24
 axes[0].scatter(x[g],y[g],s=27,c=col,marker=marker,alpha=.85,edgecolors='white',linewidths=.4,label=f'{mesh} meshes (n = 24)')
 axes[1].scatter(y[g],residual[g],s=27,c=col,marker=marker,alpha=.85,edgecolors='white',linewidths=.4)
axes[0].plot(limits,limits,'--',color=GREY,lw=1,zorder=0)
axes[0].set(xlim=limits,ylim=limits,xlabel='Observed terminal load (kN)',ylabel='Mean held-out prediction (kN)',title='(a) Terminal parity');axes[0].set_aspect('equal',adjustable='box')
axes[1].axhline(0,color=GREY,ls='--',lw=1,zorder=0)
axes[1].set(xlim=limits,ylim=(-rmax,rmax),xlabel='Mean held-out prediction (kN)',ylabel='Prediction − observed (kN)',title='(b) Signed error')
for ax in axes:ax.grid(alpha=.15)
fig.legend(*axes[0].get_legend_handles_labels(),loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.52,1.11))
fig.subplots_adjust(bottom=.18,top=.88)
assert x.between(*limits).all() and y.between(*limits).all() and residual.between(-rmax,rmax).all()
checks['ridge_terminal_diagnostics']={'source_specimens':48,'points_per_panel':[sum(len(c.get_offsets()) for c in ax.collections) for ax in axes], 'parity_limits':limits,'residual_limits':[-rmax,rmax],'all_points_within_axes':True,'mean_absolute_error_of_mean_predictions':float(residual.abs().mean()),'aggregation':'Two held-out predictions averaged per specimen before residual calculation; no interval bars.'}
assert checks['ridge_terminal_diagnostics']['points_per_panel']==[48,48]
finish(fig,'ridge_terminal_diagnostics',['terminal_oof_predictions.csv','terminal_fold_predictions.csv'],'48 terminal specimens; mean of two held-out predictions per specimen, parity and signed residual. Full-range axes; no calibrated uncertainty claim. R-06 and R-07 consolidated.')
# Absolute standardized encoded coefficients, grouped by source field.
f=read('feature_importance_full_fit.csv').sort_values('importance_abs'); assert len(f)==11
labels={'split_group_treatment':'Treatment group (sum)','series_id':'Series (sum)','treatment_protocol':'Treatment protocol (sum)','campaign_id':'Campaign (sum)','treatment_coarse':'Coarse treatment (sum)','n_steel_mesh':'Mesh count','nacl_pct':'Chloride concentration','treatment_label_coarse':'Coarse treatment label (sum)','cover_mm':'Cover','week':'Observation week','ageing_days':'Ageing days'}
fig,ax=plt.subplots(figsize=(7.2,3.65)); bars=ax.barh([labels[s] for s in f.feature],f.importance_abs,color=BLUE,height=.68)
for bar,value in zip(bars,f.importance_abs):
 label=f'{value:.3f}' if value>=.001 else f'{value:.6f}'
 ax.text(value+.002,bar.get_y()+bar.get_height()/2,label,va='center',fontsize=8.5,color=INK)
ax.set(xlim=(0,float(f.importance_abs.max())*1.28),xlabel='Sum of absolute standardized coefficients (kN)',title='Metadata-only Ridge • full-data descriptive fit')
ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True)
fig.subplots_adjust(left=.31,bottom=.17,top=.9)
assert len(bars)==11 and all(0<=b.get_width()<ax.get_xlim()[1] for b in bars)
checks['ridge_coefficients']={'source_fields':11,'bars':len(bars),'all_bars_within_axes':True,'near_zero_fields_labelled_not_omitted':f.loc[f.importance_abs<.001,'feature'].tolist(),'interpretation':'Numeric and one-hot encoded columns standardized; absolute coefficients summed within source field. Category counts and collinearity affect ranking; full fit, not held-out importance.'}
finish(fig,'ridge_coefficients',['feature_importance_full_fit.csv'],'All 11 saved field-level absolute standardized Ridge coefficient sums from the full-data fit. Categorical sums explicitly labelled, near-zero fields retained, no feature-level causal direction.')
# Existing learning-curve runs: render all fold values plus descriptive mean±SD.
raw=read('learning_curve_raw.csv'); summ=read('learning_curve_summary.csv'); assert len(raw)==50 and len(summ)==5
counts=raw.groupby('fraction').n_train_specimens.agg(['min','max'])
x=summ.fraction.to_numpy(); fig,ax=plt.subplots(figsize=(7.2,3.55))
for j,(split,col,label) in enumerate([('train',TEAL,'Training terminals'),('test',ORANGE,'Held-out terminals')]):
 means=summ[split+'_mae_mean'].to_numpy(); sd=summ[split+'_mae_std'].to_numpy()
 offset=-.01 if j==0 else .01
 for frac,group in raw.groupby('fraction'):
  jitter=np.linspace(-.007,.007,len(group))
  ax.scatter(frac+offset+jitter,group[split+'_mae'],s=13,c=col,alpha=.30,edgecolors='none',zorder=2)
 ax.errorbar(x+offset,means,yerr=sd,marker='o',markersize=5,lw=1.5,capsize=3,color=col,label=label,zorder=3)
 ticklabels=[f'{int(r.min)}' if r.min==r.max else f'{int(r.min)}–{int(r.max)}' for r in counts.itertuples()]
upper=max(float(raw[['train_mae','test_mae']].max().max()),float((summ.test_mae_mean+summ.test_mae_std).max()))*1.08
ax.set(xlim=(.15,1.05),ylim=(0,upper),xticks=x,xticklabels=ticklabels,xlabel='Training specimens per split (observed count range)',ylabel='Terminal MAE (kN)',title='Metadata-only Ridge • saved training-subset diagnostic')
ax.legend(frameon=False,loc='upper right');ax.grid(alpha=.15);fig.subplots_adjust(bottom=.2,top=.87)
assert (raw[['train_mae','test_mae']]>=0).all().all() and (raw[['train_mae','test_mae']]<=upper).all().all()
checks['ridge_learning_curve']={'source_runs':50,'displayed_training_points':50,'displayed_test_points':50,'all_points_and_errorbars_within_axes':True,'ylim':[0,upper],'fraction_to_count_range':{str(k):[int(v['min']),int(v['max'])] for k,v in counts.iterrows()},'summary_verified_by':'audit_saved_figures.py','interval':'Sample SD across 10 dependent splits, not confidence intervals.'}
finish(fig,'ridge_learning_curve',['learning_curve_raw.csv','learning_curve_summary.csv','fold_metrics.csv'],'50 saved runs over five training fractions and ten grouped splits. All individual train/test MAEs visible; means and sample SD descriptive. Training-count ranges labelled. No model refit.')
# Retain original records and append only the named v3 extension.
p=OUT/'figures/PROVENANCE.json'; old=json.loads(p.read_text()); original=[r for r in old if not Path(r['figure']).stem.startswith('ridge_')]
assert len(original)==7
p.write_text(json.dumps(original+ledger,indent=2)+'\n')
p=OUT/'figures/PROVENANCE.md'; old=p.read_text().split('\n# v3 diagnostic extension\n')[0]
text='\n# v3 diagnostic extension\n\nThe original seven records above and the separate paired ledger remain unchanged. The three additions below use `final_reports/scripts/make_v3_figures.py`; the introductory v1 generation statement above does not apply to this extension. Numerical checks and source hashes are in `final_reports/records/evidence/v3/figure_checks.json` and `final_reports/records/evidence/v3/new_figure_checks.json`.\n'
for r in ledger:text+='\n## '+Path(r['figure']).name+'\n\n'+r['description']+'\n\nSources: '+', '.join('`'+s+'`' for s in r['source_files'])+'\n'
p.write_text(old+text)
(OUT/'records/evidence/v3/new_figure_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
