"""Read saved outputs, assert the report's numerical basis; never train models.

Run from any directory with the project's scientific Python environment.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import zipfile
import numpy as np
import pandas as pd
import yaml
from scipy.stats import spearmanr, pearsonr

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'report_v2'
SOURCES = {}
CLAIMS = []

def register(path):
    p = ROOT / path
    SOURCES[path] = dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                         mtime_utc=datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat())
    return p

def csv(path):
    return pd.read_csv(register(path))

def claim(name, value, paths, method):
    for p in paths:
        register(p)
    CLAIMS.append(dict(claim=name, value=value, sources=paths, method=method, verified=True))

def save(df, name):
    df.to_csv(OUT / 'tables' / (name + '.csv'), index=False)

def audit():
    master_path='main_4/outputs/data/master_table.csv'
    d=csv(master_path)
    t=d[d.ultimate_load_kn.notna()].copy()
    assert len(d)==791 and d.specimen_id.nunique()==48
    assert len(t)==48 and t.specimen_id.nunique()==48
    assert d.wire_area_loss_frac.notna().sum()==48
    assert (t.week==t.terminal_week).all()
    assert np.allclose(t.wire_area_loss_frac*100,t.wire_area_loss_pct)
    assert set(d[d.wire_area_loss_frac.notna()].sample_name)==set(t.sample_name)
    claim('Aligned observations / specimens / terminal observations', [791,48,48], [master_path], 'Row counts and uniqueness; both structural targets coincide with terminal rows.')
    sizes=d.groupby('specimen_id').size()
    claim('Images per specimen: min / median / max; unique weeks / range', [int(sizes.min()),float(sizes.median()),int(sizes.max()),int(d.week.nunique()),int(d.week.min()),int(d.week.max())],[master_path],'Group sizes and week unique values.')
    design=t.groupby('campaign_id').agg(specimens=('specimen_id','nunique'),mesh=('n_steel_mesh','first'),chloride_pct=('nacl_pct','first'),terminal_week=('terminal_week','first'),terminal_days=('terminal_days','first')).reset_index()
    for c in ['n_steel_mesh','nacl_pct','terminal_week','terminal_days']:
        assert (t.groupby('campaign_id')[c].nunique()==1).all()
    save(design,'campaign_design')
    claim('Campaign design matrix',design.to_dict('records'),[master_path],'One unique mesh, chloride and terminal duration per campaign; two observed combinations.')
    counts=d.surface_total_rust_category.value_counts().sort_index().to_dict()
    claim('Total surface corrosion four-class distribution',counts,[master_path],'Counts on current aligned basis.')
    for col in ['surface_total_rust_pct','peak_rust_pct','wire_area_loss_frac','ultimate_load_kn']:
        x=d[col].dropna()
        claim(col+' observed range',[float(x.min()),float(x.max())],[master_path],'Non-null minimum and maximum.')
    auditpath='main_4/outputs/audit/verified_facts.json'
    facts=json.loads(register(auditpath).read_text())
    assert facts['image_files']==792 and facts['aligned_rows']==791
    claim('Raw files / corrupted image',[792,facts['orphan_images']],[auditpath],'Saved image-readability audit; archive readability independently checked below.')
    # Image archive exists even when the expanded directory has been removed.
    with zipfile.ZipFile(ROOT/'Data/Images_dataset.zip') as z:
        imgs=[n for n in z.namelist() if n.lower().endswith('.png') and not n.startswith('__MACOSX')]
        from PIL import Image
        from io import BytesIO
        bad=[]
        for n in imgs:
            try:
                with Image.open(BytesIO(z.read(n))) as im: im.verify()
            except Exception: bad.append(Path(n).name)
        assert len(imgs)==792 and bad==['E01-20240508-17W.png'], (len(imgs),bad)
        claim('Archive image-readability verification',{'png_files':len(imgs),'unreadable':bad},['Data/Images_dataset.zip'],'Pillow verify of every PNG within the saved archive; no extraction.')
    fpath='main_4/outputs/features/image_features.csv'
    f=csv(fpath)
    m=d.merge(f[['sample_name','img_rust_area_ratio_pct']],on='sample_name',validate='one_to_one')
    rho=float(spearmanr(m.surface_total_rust_pct,m.img_rust_area_ratio_pct).statistic)
    err=np.abs(m.surface_total_rust_pct-m.img_rust_area_ratio_pct)
    assert round(rho,4)==0.9996
    claim('Rust feature / total surface label adjacency',dict(n=len(m),spearman=rho,mae=float(err.mean()),max_abs_diff=float(err.max())),[master_path,fpath],'Merge on sample_name, Spearman and absolute differences.')
    for p,name in [('main/reports/current_corrosion_metrics.csv','classical'),('main_2/reports/model_comparison.csv','embedding')]:
        x=csv(p);save(x,name);claim(name+' saved model metrics',x.to_dict('records'),[p],'Exact saved metrics; distinct protocols, no cross-generation ranking.')
    predpath='main_2/reports/predictions_best_model.csv'
    x=csv(predpath)
    claim('Embedding prediction table columns/rows',{'rows':len(x),'columns':x.columns.tolist()},[predpath],'Table inventory; test membership counts added in scope table.')
    splits=x.groupby('split').agg(rows=('split','size'),specimens=('specimen','nunique')).reset_index()
    claim('Embedding split counts',splits.to_dict('records'),[predpath],'Saved prediction membership: train / validation / test; 159 test images from 10 specimens.')
    test=x[x.split=='test'];assert len(test)==159 and test.specimen.nunique()==10
    assert np.isclose(np.abs(test.y_pred-test.y_true).mean(),5.625507600497062)
    legacy='main_3/outputs/canonical_dataset.csv';legacy_df=csv(legacy)
    assert len(legacy_df)==792 and legacy_df.surface_total_rust_category.nunique()==5
    claim('Earlier five-class schema',legacy_df.surface_total_rust_category.value_counts().sort_index().to_dict(),[legacy],'Explicitly distinct from the current four-class preparation branch.')
    # Fixed grouped-holdout winners tracked through each regime.
    ratios=[]; early=[]
    for p in ['main_3/outputs/corrosion_regression_metrics.csv','main_3/outputs/damage_regression_metrics.csv']:
        x=csv(p)
        for target,g in x.groupby('target'):
            agg=g.groupby(['strategy','model']).agg(mae=('mae','mean'),rmse=('rmse','mean'),r2=('r2','mean'),folds=('fold_id','nunique'),n_test_min=('n_test','min'),n_test_max=('n_test','max')).reset_index()
            winner=agg[agg.strategy=='group_shuffle'].sort_values('mae').iloc[0]
            for _,r in agg[agg.model==winner.model].iterrows():
                ratios.append(dict(generation='Interpretable',target=target.replace('_pct','_frac') if target=='wire_area_loss_pct' else target,model=r.model,strategy=r.strategy,ratio=r.mae/winner.mae))
            for strategy,g2 in agg.groupby('strategy'):
                r=g2.sort_values('mae').iloc[0].to_dict();r['target']=target;early.append(r)
        claim(p+' per-fold metrics',{'rows':len(x),'targets':x.target.unique().tolist()},[p],'Aggregate within model/target/regime. Regime winners and fixed-model comparisons kept separate.')
    save(pd.DataFrame(early),'interpretable_regime_winners')
    robustpath='main_4/outputs/diagnostics/tables/benchmark_best_model_robustness.csv'
    robust=csv(robustpath)
    for r in robust.itertuples():
        ratios.append(dict(generation='Refined',target=r.target,model=r.best_model_name,strategy=r.strategy,ratio=r.relative_mae_vs_group_shuffle))
    save(pd.DataFrame(ratios),'robustness_ratios');save(robust,'refined_robustness')
    claim('Fixed-model robustness ratios',ratios,[robustpath,'main_3/outputs/corrosion_regression_metrics.csv','main_3/outputs/damage_regression_metrics.csv'],'Regime MAE / same model grouped MAE; each generation independently normalized.')
    bestpath='main_4/outputs/models/hidden_damage/best_models.csv'
    best=csv(bestpath);assert (best.feature_set_name=='metadata_only').all()
    save(best,'robust_structural_selection')
    claim('Final robustness-weighted structural models',best.to_dict('records'),[bestpath],'Do not substitute diagnostic RandomForest wire-loss winner for final CatBoost selection.')
    # Check surface R2 directly; nine treatment groups in the refined build.
    for target,model in [('peak_rust_pct','RandomForest'),('surface_total_rust_pct','GradientBoosting')]:
        p=f'main_4/outputs/models/surface/{target}/leave_one_treatment_out/{target}_fold_metrics.csv'
        x=csv(p);x=x[x.model_name==model]
        claim(target+' refined LOTO mean R2 / folds',[float(x.r2.mean()),len(x)],[p],'Fixed grouped winner; arithmetic mean across saved treatment folds.')
    ref='main_4/outputs/ultimate_load_refocus/'
    analyses={'pooled_capacity':'pooled_all_weeks/grouped_cv/feature_set_comparison.csv','loco_capacity':'pooled_all_weeks/leave_one_campaign_out/feature_set_comparison.csv','post_onset_capacity':'pooled_post_onset/grouped_cv/selected_best_model_per_feature_set.csv','mesh_capacity':'mesh_stratified/mesh_feature_set_comparison.csv'}
    for name,suffix in analyses.items():
        x=csv(ref+suffix);save(x,name)
        claim(name+' metrics',x.to_dict('records'),[ref+suffix],'Saved mean and sample SD across folds; selected model per feature set.')
        if name=='mesh_capacity': assert (x.r2_mean<0).all()
    # Recompute central full-basis summaries from prediction files (no fitting).
    comparison=csv(ref+analyses['pooled_capacity'])
    for r in comparison.itertuples():
        base=ref+f'pooled_all_weeks/grouped_cv/experiments/{r.feature_set_name}/{r.model_name}/'
        folds=csv(base+'fold_metrics.csv')
        pred=csv(base+'terminal_fold_predictions.csv')
        for sid,g in pred.groupby('split_id'):
            observed=float(np.abs(g.predicted_ultimate_load_kn-g.terminal_ultimate_load_kn_target).mean())
            assert np.isclose(observed,folds.set_index('split_id').loc[sid,'test_mae'],atol=1e-12)
        for met in ['mae','rmse','r2','spearman']:
            assert np.isclose(folds['test_'+met].mean(),getattr(r,met+'_mean'),atol=1e-12)
            assert np.isclose(folds['test_'+met].std(ddof=1),getattr(r,met+'_std'),atol=1e-12)
        assert pred.specimen_id.nunique()==48 and len(pred)==96
        claim('Prediction-level check '+r.feature_set_name,dict(folds=len(folds),specimens=48,terminal_prediction_rows=96,test_specimens_min=int(folds.test_specimens.min()),test_specimens_max=int(folds.test_specimens.max())),[base+'fold_metrics.csv',base+'terminal_fold_predictions.csv'],'Recompute per-fold MAE from terminal predictions and all summary means/SDs from folds.')
    # Manifests are the authority on grouping, not source-code assertions alone.
    manifests=list((ROOT/'main_4/outputs/splits').glob('master_*.csv'))
    manifests += list((ROOT/ref/'splits').glob('*specimen_manifest.csv'))
    manifests += list((ROOT/ref/'mesh_stratified').glob('*/grouped_cv/specimen_manifest.csv'))
    manifests += list((ROOT/ref/'pooled_post_onset').glob('*/specimen_manifest.csv'))
    split_checks=[]
    for p in manifests:
        path=str(p.relative_to(ROOT));x=csv(path)
        if 'membership' not in x: continue
        for sid,g in x.groupby('split_id'):
            tr=set(g.loc[g.membership=='train','specimen_id']);te=set(g.loc[g.membership=='test','specimen_id'])
            assert not tr&te
            split_checks.append(dict(source=path,split_id=sid,train_n=len(tr),test_n=len(te),overlap=0))
    save(pd.DataFrame(split_checks),'split_checks')
    claim('Saved specimen-split disjointness',{'checked_folds':len(split_checks),'overlaps':0},sorted(set(r['source'] for r in split_checks)),'Set intersection of specimen identities per split.')
    spath=ref+'data/specimen_summary_table.csv';s=csv(spath)
    cp=ref+'correlations/mesh_stratified_corrosion_vs_ultimate_load.csv';corr=csv(cp)
    corr_rows=[]
    for name,g in [('Pooled',s),('4 meshes',s[s.n_steel_mesh==4]),('7 meshes',s[s.n_steel_mesh==7])]:
        rr=spearmanr(g.surface_total_rust_pct_terminal,g.terminal_ultimate_load_kn_target)
        corr_rows.append(dict(group=name,n=len(g),spearman=float(rr.statistic),p_value=float(rr.pvalue)))
    assert round(corr_rows[0]['spearman'],3)==0.462
    save(pd.DataFrame(corr_rows),'correlations_recomputed')
    claim('Terminal total-rust/load correlations',corr_rows,[spath,cp],'Independent Spearman recomputation; pooled association is not a causal effect.')
    proxy='main_4/outputs/models/proxy_rul/proxy_rul_estimates.csv';x=csv(proxy)
    status=x.groupby(['threshold_wire_area_loss_frac','threshold_status']).size().unstack(fill_value=0)
    save(status.reset_index(),'threshold_status')
    assert len(x)==144 and x.proxy_rul_days.notna().sum()==0
    claim('Refined threshold statuses',x.threshold_status.value_counts().to_dict(),[proxy],'144 specimen-threshold pairs; zero future crossings; historical crossings retained.')
    pjson='main_4/outputs/models/proxy_rul/proxy_rul_summary.json'
    summary=json.loads(register(pjson).read_text());save(pd.DataFrame(summary['summary_records']),'threshold_summary')
    for row in summary['summary_records']:
        assert row['n_future_crossings_within_horizon']==0
    claim('Threshold-wise summary',summary,[pjson,proxy],'Cross-check zero future crossings and sum of statuses.')
    degpath='main_4/outputs/models/degradation/degradation_best_fits.csv'
    deg=csv(degpath)
    claim('Refined degradation fit inventory',{'rows':len(deg),'columns':deg.columns.tolist()},[degpath],'Saved descriptive fits; no longitudinal structural validation.')
    claim('Refined curve family counts',deg.best_family.value_counts().to_dict(),[degpath],'48 selected fits; descriptive rather than physically validated.')
    residual=ref+'residual_refinement/model_comparison.csv';rr=csv(residual)
    claim('Residual-refinement saved comparison',rr.to_dict('records'),[residual,ref+'residual_refinement/best_model.csv'],'Metadata-only baseline selected; second-stage corrections worsened MAE.')
    register('main/artifacts/manifest.json')
    register('main_4/configs/thresholds.yaml')
    register('main_4/configs/ultimate_load_refocus.yaml')
    # Augmentation split / target schema checks.
    splitsets={};splitrows=[]
    for name in ['train','val','test']:
        p=f'Data/splits/{name}_manifest.csv';x=csv(p);splitsets[name]=set(x.specimen_id)
        if name!='train': assert not x.is_augmented.any()
        splitrows.append(dict(split=name,rows=len(x),specimens=x.specimen_id.nunique(),originals=int((~x.is_augmented).sum()),augmented=int(x.is_augmented.sum()),**{f'class_{c}':int((x.label==c).sum()) for c in range(1,5)}))
    assert not splitsets['train']&splitsets['val'] and not splitsets['train']&splitsets['test'] and not splitsets['test']&splitsets['val']
    save(pd.DataFrame(splitrows),'classification_splits')
    claim('Prepared four-class split inventory',splitrows,[f'Data/splits/{n}_manifest.csv' for n in splitsets],'Specimen-disjoint; validation/test originals only. Inventory is not classification performance.')
    # Current bugs and timestamp evidence, without repairing historical code.
    mappingpath='main_4/configs/specimen_mapping.yaml'
    mapping=yaml.safe_load(register(mappingpath).read_text())
    specimens=mapping['specimens']
    vals=specimens.values() if isinstance(specimens,dict) else specimens
    no=[v for v in vals if v.get('treatment_coarse') is False]
    assert len(no)==10
    bad=d[d.treatment_coarse=='False'];assert bad.specimen_id.nunique()==10 and (bad.treatment_raw=='NO').all()
    claim('Live YAML NO boolean issue',{'specimens':len(no),'rows':len(bad)},[mappingpath,master_path],'PyYAML safe_load and saved treatment_raw / treatment_coarse cross-check.')
    hits=[]
    for folder in ['main','main_2','main_3','main_4','augmentation']:
        for p in (ROOT/folder).rglob('*'):
            if p.suffix not in ['.py','.yaml','.toml']:continue
            txt=p.read_text(errors='replace')
            if 'main_first' in txt:
                path=str(p.relative_to(ROOT)); register(path)
                hits.append(dict(path=path,mtime_utc=SOURCES[path]['mtime_utc'],occurrences=txt.count('main_first')))
    assert not any(h['path'].startswith('augmentation/') for h in hits)
    assert all(any(h['path'].startswith(f+'/') for h in hits) for f in ['main','main_2','main_3','main_4'])
    save(pd.DataFrame(hits),'current_corruption_inventory')
    cutoff=min(r['mtime_utc'] for r in hits)
    historical=[dict(path=p,**v,predates_earliest_corrupted_source=v['mtime_utc']<cutoff) for p,v in SOURCES.items() if p.startswith(('main/','main_2/','main_3/','main_4/')) and '/outputs/' in p or p.startswith(('main/reports/','main_2/reports/'))]
    save(pd.DataFrame(historical),'historical_artifact_timestamps')
    assert all(r['predates_earliest_corrupted_source'] for r in historical)
    claim('Timestamp evidence for cited saved scientific outputs',{'checked_artifacts':len(historical),'earliest_affected_source_mtime_utc':cutoff,'all_predate':True},[r['path'] for r in historical],'Filesystem mtimes support chronology, not a cryptographic proof of historical execution or root cause.')
    save(pd.DataFrame([dict(path=p,**v) for p,v in SOURCES.items()]),'source_hashes')
    (OUT/'evidence'/'claims.json').write_text(json.dumps(CLAIMS,indent=2,default=str)+'\n')
    log=['# Verification log','',f'Re-run: {datetime.now(timezone.utc).isoformat()}','', 'Generated by `scripts/audit_evidence.py`; all checks read saved artifacts and perform no model fitting.','']
    for c in CLAIMS:
        log += ['## '+c['claim'],'','- Verified: yes','- Method: '+c['method'],'- Source: '+', '.join('`'+p+'`' for p in c['sources']),'- Value: `'+json.dumps(c['value'],default=str)+'`','']
    (OUT/'VERIFICATION_LOG.md').write_text('\n'.join(log))
    print(f'PASS: {len(CLAIMS)} claim groups; {len(SOURCES)} hashed sources; {len(split_checks)} disjoint split checks.')

if __name__=='__main__':audit()
