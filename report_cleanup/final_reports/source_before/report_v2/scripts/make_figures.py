"""Generate vector scientific figures and LaTeX tables from verified saved data."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'report_v2'
BLUE='#236192';TEAL='#15847B';ORANGE='#C16B29';INK='#1C2F40';GREY='#647583'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'savefig.bbox':'tight'})
ledger=[]
def table(name):return pd.read_csv(OUT/'tables'/f'{name}.csv')
def raw(path):return pd.read_csv(ROOT/path)
def finish(fig,name,sources,description):
    p=OUT/'figures'/f'{name}.pdf';fig.savefig(p,pad_inches=.08);fig.savefig(p.with_suffix('.png'),dpi=160,pad_inches=.08);plt.close(fig)
    ledger.append({'figure':str(p.relative_to(ROOT)),'script':'report_v2/scripts/make_figures.py','source_files':sources,'description':description,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generated_utc':datetime.now(timezone.utc).isoformat()})
def box(ax,x,y,w,h,title,body,color=BLUE):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.015,rounding_size=0.025',facecolor=color+'10',edgecolor=color,lw=1.3))
    ax.text(x+w/2,y+h*.73,title,ha='center',va='center',weight='bold',color=color,fontsize=11)
    ax.text(x+w/2,y+h*.34,body,ha='center',va='center',fontsize=10,linespacing=1.45,color=INK)

master='structural_capacity/outputs/data/master_table.csv'
ref='structural_capacity/outputs/ultimate_load_refocus/'
d=raw(master);s=raw(ref+'data/specimen_summary_table.csv')

# Observation structure; arrows represent data acquisition, not causal pathways.
fig,ax=plt.subplots(figsize=(7.2,3.5));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
box(ax,.20,.72,.60,.24,'48 ferrocement specimens','Two campaigns; 24 specimens in each')
box(ax,.02,.13,.44,.42,'Surface observations','791 readable photographs\n15–18 per specimen\nTotal-rust and peak-rust labels',TEAL)
box(ax,.53,.13,.44,.42,'Terminal measurements','48 paired terminal records\nWire-area loss + ultimate load\nEach endpoint measured once',ORANGE)
ax.annotate('',(.24,.57),(.38,.70),arrowprops=dict(arrowstyle='->',color=GREY,lw=1.5))
ax.annotate('',(.75,.57),(.62,.70),arrowprops=dict(arrowstyle='->',color=GREY,lw=1.5))
ax.text(.5,.015,'No measured structural trajectories or lifetime-event labels',ha='center',color=INK,fontsize=10)
finish(fig,'dataset_supervision',[master],'Acquisition/supervision schematic; counts independently verified. Geometry is illustrative.')

fig,axes=plt.subplots(3,1,figsize=(7.2,4.3),gridspec_kw={'hspace':.8})
labels=['Grouped specimen holdout','Leave one treatment out','Leave one campaign out']
notes=['New specimens from the observed mixture','A treatment group absent from training','A campaign + mesh/chloride/duration combination absent from training']
for i,ax in enumerate(axes):
    ax.set(xlim=(-.2,12.2),ylim=(-.2,1.45));ax.axis('off')
    ax.text(0,1.22,labels[i],weight='bold',color=INK,fontsize=10)
    for j in range(12):
        test=(j in [2,7,10]) if i==0 else ((j in [2,3,8,9]) if i==1 else j>=6)
        ax.add_patch(Rectangle((j,.4),.8,.42,facecolor=ORANGE if test else BLUE,edgecolor='white'))
    ax.text(0,-.05,notes[i],fontsize=9,color=GREY)
axes[0].text(8.4,1.22,'Train',color=BLUE,weight='bold',fontsize=9);axes[0].text(10,1.22,'Test',color=ORANGE,weight='bold',fontsize=9)
fig.text(.5,.015,'Each tile is a whole specimen history. Tile counts are illustrative, not actual fold sizes.',ha='center',fontsize=9,color=GREY)
finish(fig,'evaluation_regimes',['structural_capacity/outputs/splits/master_group_shuffle.csv','structural_capacity/outputs/splits/master_leave_one_treatment_out.csv','structural_capacity/outputs/splits/master_leave_one_campaign_out.csv'],'Conceptual grouping schematic checked against saved specimen-disjoint manifests.')

fig=plt.figure(figsize=(7.2,4.7));gs=fig.add_gridspec(2,3,height_ratios=[.62,1],hspace=.55,wspace=.35)
ax=fig.add_subplot(gs[0,:]);ax.axis('off')
design=table('campaign_design')
cell=[[f'Campaign {i+1}',str(r.specimens),str(r.mesh),f'{r.chloride_pct:g}%',f'{r.terminal_week} weeks'] for i,r in enumerate(design.itertuples())]
tab=ax.table(cellText=cell,colLabels=['Observed combination','Specimens','Mesh layers','NaCl','Terminal exposure'],colWidths=[.28,.15,.17,.15,.25],loc='center',cellLoc='center',colColours=['#EAF0F4']*5);tab.auto_set_font_size(False);tab.set_fontsize(9);tab.scale(1,1.6)
all_x=s.surface_total_rust_pct_terminal;all_y=s.terminal_ultimate_load_kn_target
assert len(s)==48 and np.isfinite(all_x).all() and np.isfinite(all_y).all()
xpad=.04*(all_x.max()-all_x.min());ypad=.08*(all_y.max()-all_y.min())
xlimits=(float(all_x.min()-xpad),float(all_x.max()+xpad));ylimits=(float(all_y.min()-ypad),float(all_y.max()+ypad))
scatter_checks=[]
for j,(label,g) in enumerate([('Pooled',s),('4 meshes',s[s.n_steel_mesh==4]),('7 meshes',s[s.n_steel_mesh==7])]):
    ax=fig.add_subplot(gs[1,j]);x=g.surface_total_rust_pct_terminal;y=g.terminal_ultimate_load_kn_target
    for mesh,c in [(4,ORANGE),(7,BLUE)]:
        sel=g.n_steel_mesh==mesh;ax.scatter(x[sel],y[sel],color=c,s=22,alpha=.85,edgecolor='white',linewidth=.4)
    rho=spearmanr(x,y).statistic;ax.set_title(f'{label}: n = {len(g)}\nSpearman ρ = {rho:.3f}')
    ax.set(xlabel='Terminal total rust (%)',xlim=xlimits,ylim=ylimits);ax.grid(alpha=.15)
    assert x.between(*xlimits).all() and y.between(*ylimits).all()
    plotted=sum(len(c.get_offsets()) for c in ax.collections)
    assert plotted==len(g)
    scatter_checks.append(dict(panel=label,source_rows=len(g),plotted_points=plotted,all_points_within_axes=True,xlim=xlimits,ylim=ylimits))
    if j==0:ax.set_ylabel('Terminal load (kN)')
finish(fig,'confounding',[master,ref+'data/specimen_summary_table.csv',ref+'correlations/mesh_stratified_corrosion_vs_ultimate_load.csv'],'Observed design combinations plus terminal total-rust/load scatter; no causal regression line.')
(OUT/'figures/FIGURE_DATA_CHECKS.json').write_text(json.dumps({'confounding':scatter_checks},indent=2)+'\n')

cap=table('pooled_capacity');cap=cap.iloc[::-1].reset_index(drop=True)
fig,axes=plt.subplots(1,2,figsize=(7.2,3.5),sharey=True,gridspec_kw={'width_ratios':[1.5,1],'wspace':.17})
y=np.arange(len(cap))
for ax,col,sd,label in [(axes[0],'mae_mean','mae_std','MAE (kN)'),(axes[1],'spearman_mean','spearman_std','Spearman ρ')]:
    for i,r in cap.iterrows():
        c=TEAL if r.feature_set_name=='metadata_only' else BLUE
        ax.errorbar(r[col],i,xerr=r[sd],fmt='o',color=c,ecolor=c,elinewidth=1.2,capsize=2,markersize=5)
    ax.set(xlabel=label,yticks=y);ax.grid(axis='x',alpha=.18)
axes[0].set_yticklabels(cap.feature_set_label);axes[0].set_xlim(0,.34);axes[1].set_xlim(.15,1.02)
fig.suptitle('Terminal-load ablation • 48 specimens • 10 grouped folds',fontsize=11,y=1.02)
finish(fig,'capacity_ablation',[ref+'pooled_all_weeks/grouped_cv/feature_set_comparison.csv'],'Per-feature-set selected models; mean and sample SD of fold metrics; no inferential intervals.')

rat=table('robustness_ratios');targets=['surface_total_rust_pct','peak_rust_pct','wire_area_loss_frac','ultimate_load_kn'];nice=['Total rust','Peak rust','Wire-area loss','Ultimate load']
fig,axes=plt.subplots(1,2,figsize=(7.2,3.5),sharey=True)
for ax,generation in zip(axes,['Interpretable','Refined']):
    sub=rat[(rat.generation==generation)&(rat.strategy!='group_shuffle')]
    arr=np.array([[sub[(sub.target==t)&(sub.strategy==st)].ratio.iloc[0] for st in ['leave_one_treatment_out','leave_one_campaign_out']] for t in targets])
    im=ax.imshow(arr,cmap='YlOrBr',vmin=0,vmax=5.5,aspect='auto')
    for i in range(4):
        for j in range(2):ax.text(j,i,f'{arr[i,j]:.2f}×',ha='center',va='center',color='white' if arr[i,j]>3 else INK,fontsize=11,weight='bold')
    ax.set(xticks=[0,1],xticklabels=['Treatment out','Campaign out'],yticks=range(4),yticklabels=nice,title=generation)
    ax.tick_params(length=0);ax.axhline(1.5,color='white',lw=3)
fig.text(.5,-.01,'MAE / same model’s grouped-holdout MAE; 1× is unchanged error',ha='center',fontsize=9)
finish(fig,'robustness_synthesis',['condition_assessment/outputs/corrosion_regression_metrics.csv','condition_assessment/outputs/damage_regression_metrics.csv','structural_capacity/outputs/diagnostics/tables/benchmark_best_model_robustness.csv'],'Within-generation normalized MAE; fixed grouped-holdout winner tracked by target. Not a cross-generation raw-metric ranking.')

f=raw('structural_capacity/outputs/features/image_features.csv');m=d.merge(f[['sample_name','img_rust_area_ratio_pct']],on='sample_name')
fig,axes=plt.subplots(1,2,figsize=(7.2,3.1))
axes[0].scatter(m.surface_total_rust_pct,m.img_rust_area_ratio_pct,s=10,alpha=.45,color=TEAL);v=max(m.surface_total_rust_pct.max(),m.img_rust_area_ratio_pct.max());axes[0].plot([0,v],[0,v],color=GREY,lw=.8,ls='--')
axes[0].set(xlabel='Total surface-rust label (%)',ylabel='Rust-area image feature (%)',title='791 matched observations')
axes[1].hist((m.img_rust_area_ratio_pct-m.surface_total_rust_pct)*1e4,bins=30,color=BLUE,edgecolor='white');axes[1].set(xlabel='Feature minus label\n($10^{-4}$ percentage points)',ylabel='Observations',title='Near numerical reconstruction')
fig.tight_layout()
finish(fig,'label_adjacency',[master,'structural_capacity/outputs/features/image_features.csv'],'Scatter and residual histogram quantify near-identity without assuming identical label-generation code.')

ts=table('threshold_summary');fig,ax=plt.subplots(figsize=(7.2,2.7));left=np.zeros(len(ts))
for col,label,color in [('n_crossed_by_baseline','Crossed by baseline',ORANGE),('n_crossed_during_observation','Crossed during observation',TEAL),('n_right_censored','Not crossed within horizon','#CCD6DD')]:
    ax.barh(np.arange(len(ts)),ts[col],left=left,label=label,color=color,height=.58)
    for i,n in enumerate(ts[col]):
        if n:ax.text(left[i]+n/2,i,str(n),ha='center',va='center',fontsize=9,color=INK)
    left+=ts[col]
ax.set(yticks=range(3),yticklabels=[f'{v:.0%}' for v in ts.threshold_wire_area_loss_frac],xlabel='Specimens (n = 48 at each threshold)',ylabel='Wire-area-loss\nthreshold',xlim=(0,48));ax.invert_yaxis();ax.legend(loc='upper center',bbox_to_anchor=(.45,-.29),ncol=3,frameon=False,fontsize=8)
ax.set_title('Zero future crossings at every threshold; 365-day projection horizon')
finish(fig,'threshold_status',['structural_capacity/outputs/models/proxy_rul/proxy_rul_estimates.csv','structural_capacity/configs/thresholds.yaml'],'Statuses of model-derived wire-loss trajectories, not observed failure events.')

# Machine-generated publication tables, preserving unrounded CSVs alongside them.
def latex(name,columns,headers,formats=None):
    df=table(name);formats=formats or {}
    lines=['\\begin{tabular}{'+''.join('l' if i==0 else 'r' for i in range(len(columns)))+'}','\\toprule',' & '.join(headers)+r' \\',r'\midrule']
    for _,r in df.iterrows():
        vals=[]
        for c in columns:
            v=r[c]
            if c in formats:v=formats[c](v)
            else:v=str(v).replace('_',r'\_').replace('%',r'\%')
            vals.append(v)
        lines.append(' & '.join(vals)+r' \\')
    lines+=['\\bottomrule','\\end{tabular}']
    (OUT/'tables'/f'{name}.tex').write_text('\n'.join(lines)+'\n')
f3=lambda v:f'{v:.3f}'
for name in ['pooled_capacity','post_onset_capacity','mesh_capacity','loco_capacity']:
    if name=='mesh_capacity':cols=['analysis_name','feature_set_label','model_name','mae_mean','r2_mean','spearman_mean'];heads=['Subset','Features','Model','MAE',' $R^2$','$\\rho$']
    else:cols=['feature_set_label','model_name','mae_mean','mae_std','r2_mean','spearman_mean'];heads=['Features','Model','MAE','SD',' $R^2$','$\\rho$']
    latex(name,cols,heads,{c:f3 for c in cols if c.endswith(('_mean','_std'))})
latex('classification_splits',['split','specimens','originals','augmented','rows'],['Split','Specimens','Originals','Augmented','Total'],{k:lambda v:str(int(v)) for k in ['specimens','originals','augmented','rows']})
latex('threshold_summary',['threshold_wire_area_loss_frac','n_crossed_by_baseline','n_crossed_during_observation','n_future_crossings_within_horizon','n_right_censored'],['Threshold','Baseline','During','Future','Not crossed'],{'threshold_wire_area_loss_frac':lambda v:f'{v:.0%}'.replace('%',r'\%'),**{c:lambda v:str(int(v)) for c in ts.columns if c.startswith('n_')}})
for name in ['pooled_capacity','post_onset_capacity']:
    df=table(name);lines=[r'\begin{tabular}{lrrrr}',r'\toprule',r'Features & MAE & SD & $R^2$ & $\rho$ \\',r'\midrule']
    for _,r in df.iterrows():lines.append(f"{r.feature_set_label} & {r.mae_mean:.3f} & {r.mae_std:.3f} & {r.r2_mean:.3f} & {r.spearman_mean:.3f}"+r' \\')
    lines += [r'\bottomrule',r'\end{tabular}'];(OUT/'tables'/(name+'_article.tex')).write_text('\n'.join(lines)+'\n')
(OUT/'figures'/'PROVENANCE.json').write_text(json.dumps(ledger,indent=2)+'\n')
notes=['# Figure provenance','','All figures are generated by `report_v2/scripts/make_figures.py` from the exact source paths below. Run date: 2026-09-16. Every numerical input is checked by `audit_evidence.py`; schematic geometry is illustrative. PDF is the publication master; PNG is a viewing copy.','']
for row in ledger:notes+=['## '+Path(row['figure']).name,'',row['description'],'','Sources: '+', '.join('`'+s+'`' for s in row['source_files']),'']
(OUT/'figures'/'PROVENANCE.md').write_text('\n'.join(notes))
print(f'Generated {len(ledger)} verified vector figures and publication tables.')
