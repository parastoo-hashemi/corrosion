"""Descriptive paired reanalysis of existing held-out predictions; no fitting."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'report_v2';ref=ROOT/'structural_capacity/outputs/ultimate_load_refocus'
paths={name:ref/f'pooled_all_weeks/grouped_cv/experiments/{name}/Ridge/terminal_fold_predictions.csv' for name in ['metadata_only','metadata_hsv']}
a,b=[pd.read_csv(p) for p in paths.values()]
key=['specimen_id','split_id'];pairs=a.merge(b,on=key,suffixes=('_metadata','_hsv'),validate='one_to_one')
assert len(pairs)==96 and pairs.specimen_id.nunique()==48
assert np.allclose(pairs.terminal_ultimate_load_kn_target_metadata,pairs.terminal_ultimate_load_kn_target_hsv)
pairs['error_metadata']=np.abs(pairs.predicted_ultimate_load_kn_metadata-pairs.terminal_ultimate_load_kn_target_metadata)
pairs['error_hsv']=np.abs(pairs.predicted_ultimate_load_kn_hsv-pairs.terminal_ultimate_load_kn_target_hsv)
paired=pairs.groupby('specimen_id').agg(metadata_mae=('error_metadata','mean'),metadata_hsv_mae=('error_hsv','mean'),evaluations=('split_id','size')).reset_index()
assert (paired.evaluations==2).all()
paired['delta_mae_kn']=paired.metadata_hsv_mae-paired.metadata_mae
paired=paired.sort_values('delta_mae_kn').reset_index(drop=True)
paired.to_csv(OUT/'tables/paired_specimen_errors.csv',index=False)
stats=dict(specimens=len(paired),evaluations_per_specimen=2,mean_delta_kn=float(paired.delta_mae_kn.mean()),median_delta_kn=float(paired.delta_mae_kn.median()),improved=int((paired.delta_mae_kn<0).sum()),worsened=int((paired.delta_mae_kn>0).sum()),unchanged=int((paired.delta_mae_kn==0).sum()),min_delta_kn=float(paired.delta_mae_kn.min()),max_delta_kn=float(paired.delta_mae_kn.max()),metadata_specimen_mae=float(paired.metadata_mae.mean()),metadata_hsv_specimen_mae=float(paired.metadata_hsv_mae.mean()))
# Actual held-out group sizes, from saved metadata-only selected fold metrics.
ranges=[]
for analysis,path in [('Four meshes','mesh_stratified/mesh_4'),('Seven meshes','mesh_stratified/mesh_7'),('Post onset','pooled_post_onset')]:
 p=ref/path/'grouped_cv/selected_best_models/experiments/metadata_only/Ridge/fold_metrics.csv';f=pd.read_csv(p)
 ranges.append(dict(analysis=analysis,folds=len(f),test_min=int(f.test_specimens.min()),test_max=int(f.test_specimens.max()),source=str(p.relative_to(ROOT))))
# Classical group size reconstructed, without loading or fitting its models.
legacy=pd.read_csv(ROOT/'condition_assessment/outputs/canonical_dataset.csv')
tr,te=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42).split(legacy,groups=legacy.specimen_id))
classical=dict(total_rows=len(legacy),total_specimens=legacy.specimen_id.nunique(),test_rows=len(te),test_specimens=legacy.iloc[te].specimen_id.nunique(),train_specimens=legacy.iloc[tr].specimen_id.nunique(),method='Reconstruct GroupShuffleSplit(test_size=0.2, random_state=42) from classical_corrosion/modeling.py using saved legacy specimen IDs; not a saved holdout prediction manifest.')
result=dict(paired=stats,fold_sizes=ranges,classical_reconstructed=classical,sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths.values()})
(OUT/'evidence/paired_diagnostics.json').write_text(json.dumps(result,indent=2,default=int)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(7.2,3.2));colors=np.where(paired.delta_mae_kn<0,'#15847B','#C16B29')
ax.vlines(np.arange(1,49),0,paired.delta_mae_kn,color=colors,linewidth=1.2);ax.scatter(np.arange(1,49),paired.delta_mae_kn,c=colors,s=15)
ax.axhline(0,color='#647583',lw=.8);ax.axhline(stats['mean_delta_kn'],color='#236192',lw=1,ls='--',label='Specimen-weighted mean')
ax.set(xlabel='Specimens sorted by paired error difference (n = 48)',ylabel='Change in absolute error (kN)\nmetadata+HSV minus metadata',xlim=(0,49),ylim=(-.2,.16))
assert paired.delta_mae_kn.between(*ax.get_ylim()).all()
ax.text(.02,.93,f"{stats['improved']} improve",transform=ax.transAxes,color='#15847B',weight='bold');ax.text(.98,.93,f"{stats['worsened']} worsen",transform=ax.transAxes,ha='right',color='#C16B29',weight='bold')
ax.grid(axis='y',alpha=.15);ax.legend(loc='lower right',frameon=False,fontsize=8);fig.tight_layout()
p=OUT/'figures/paired_specimen_errors.pdf';fig.savefig(p,bbox_inches='tight',pad_inches=.08);fig.savefig(p.with_suffix('.png'),dpi=160,bbox_inches='tight',pad_inches=.08);plt.close(fig)
prov={'figure':str(p.relative_to(ROOT)),'script':'report_v2/scripts/paired_diagnostics.py','source_files':[str(p.relative_to(ROOT)) for p in paths.values()],'description':'Ridge metadata+HSV minus Ridge metadata mean absolute terminal error per specimen; two held-out evaluations averaged before equal-specimen aggregation. Descriptive after model selection, no significance claim.','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generated_utc':datetime.now(timezone.utc).isoformat()}
(OUT/'figures/PAIRED_PROVENANCE.json').write_text(json.dumps(prov,indent=2)+'\n')
(OUT/'figures/PAIRED_PROVENANCE.md').write_text('# Paired error figure provenance\n\nGenerated by `report_v2/scripts/paired_diagnostics.py` on 2026-09-16 from:\n\n'+''.join('- `'+str(p.relative_to(ROOT))+'`\n' for p in paths.values())+'\n'+prov['description']+'\n')
(OUT/'tables/paired_statistics.tex').write_text('\\newcommand{\\pairedMean}{'+f"{stats['mean_delta_kn']:.4f}"+'}\n'+'\\newcommand{\\pairedMedian}{'+f"{stats['median_delta_kn']:.4f}"+'}\n'+'\\newcommand{\\pairedImproved}{'+str(stats['improved'])+'}\n'+'\\newcommand{\\pairedWorsened}{'+str(stats['worsened'])+'}\n')
print(json.dumps(result,indent=2,default=int))
