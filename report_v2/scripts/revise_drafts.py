"""Create v2 as a separate revision of the preserved, reviewed v1 sources."""
from pathlib import Path
import shutil,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'report_v2'
for kind,master in [('thesis','thesis.tex'),('article','article.tex')]:
 dst=OUT/kind/'v2';dst.mkdir(exist_ok=True)
 if kind=='thesis':shutil.copytree(OUT/kind/'chapters',dst/'chapters',dirs_exist_ok=True)
 text=(OUT/kind/master).read_text().replace(r'\newcommand{\shared}{..}',r'\newcommand{\shared}{../..}').replace('Version 1','Version 2')
 if kind=='thesis':
  text=text.replace(r'\usepackage{enumitem,placeins,xcolor,fancyhdr,xurl}',r'''\usepackage{enumitem,placeins,xcolor,fancyhdr,xurl,titlesec}
\titleformat{\chapter}[display]{\normalfont\bfseries}{\large\chaptertitlename\ \thechapter}{7pt}{\LARGE}
\titlespacing*{\chapter}{0pt}{8pt}{18pt}''')
  text=text.replace(r'\caption{#3}',r'\caption[\csname short#1\endcsname]{#3}')
  short={'dataset_supervision':'Dataset and supervision structure','evaluation_regimes':'Specimen grouping and evaluation regimes','label_adjacency':'Near reconstruction of the total-rust label','robustness_synthesis':'Fixed-model robustness across evaluation regimes','capacity_ablation':'Pooled terminal-load feature-family comparison','confounding':'Campaign confounding and terminal associations','threshold_status':'Model-derived threshold status','paired_specimen_errors':'Paired specimen errors for adding HSV features'}
  text=text.replace(r'\setlength{\parskip}', '\n'.join(r'\expandafter\def\csname short'+k+r'\endcsname{'+v+'}' for k,v in short.items())+'\n'+r'\input{\shared/tables/paired_statistics.tex}'+'\n'+r'\setlength{\parskip}')
  text=text.replace(r'\begin{figure}[htbp]',r'\begin{figure}[!htbp]')
  text=text.replace(r'\setlength{\parskip}{3pt}',r'''\setlength{\parskip}{3pt}
\renewcommand{\topfraction}{.9}\renewcommand{\bottomfraction}{.8}
\renewcommand{\textfraction}{.08}\renewcommand{\floatpagefraction}{.75}
\makeatletter\setlength{\@fptop}{0pt}\setlength{\@fpsep}{16pt}\setlength{\@fpbot}{0pt plus 1fil}\makeatother''')
  text=text.replace(r'\tableofcontents\listoffigures\listoftables',r'''{\small\setlength{\parskip}{0pt}\tableofcontents}
\clearpage
\listoffigures
\clearpage
\listoftables''')
 else:
  text=text.replace(r'\usepackage{cite}',r'\usepackage{cite,flushend}')
  text=text.replace(r'\title{Surface',r'\input{\shared/tables/paired_statistics.tex}'+'\n'+r'\title{Surface')
 (dst/master).write_text(text)

base=OUT/'thesis/v2/chapters'
def edit(name,old,new):
 p=base/name;t=p.read_text();assert old in t, (name,old[:80]);p.write_text(t.replace(old,new))
edit('00_abstract.tex','A metadata-only Ridge model has mean terminal-test MAE','Scoring uses held-out terminal photographs, not a fixed early observation horizon. A metadata-only Ridge model has mean terminal-test MAE')
edit('02_background.tex','The study supplies a bounded empirical case, not a new general-purpose model.','The specific question is incremental terminal-capacity estimation after accounting for metadata, rather than visual corrosion detection alone. The study supplies a bounded empirical case, not a new general-purpose model; the focused literature search does not establish an exhaustive novelty claim.')
edit('04_methods.tex',r'\section{Three evaluation regimes}',r'''\begin{table}[htbp]\centering\small
\caption[Information available at prediction time]{Information availability in the focused capacity analysis. The primary evaluation is retrospective at the terminal image. A future early-image experiment must verify that every predictor is available before its chosen cutoff.}\label{tab:availability}
\begin{tabularx}{\textwidth}{p{.27\textwidth}X}\toprule
Quantity & Role and timing boundary\\\midrule
Image descriptors & Derived from the image at its observation time.\\
Design/treatment metadata & Recorded specimen context; availability is an assumption to check for a future deployment.\\
Week and ageing days & Exposure context at image acquisition.\\
Failure-surface cover & Included metadata; pre-test availability is not established by the saved feature definition.\\
Terminal ultimate load & Training target, repeated over image rows; evaluation uses terminal observations. Excluded from predictors.\\
Wire-area loss / visible labels & Excluded predictors in the focused capacity experiment; use in other phases is explicitly distinguished.\\\bottomrule
\end{tabularx}
\end{table}

\section{Three evaluation regimes}''')
edit('04_methods.tex','leaving 24 independent structural specimens per family.','leaving 24 independent structural specimens per family and only four or five terminal test specimens per fold.')
edit('04_methods.tex','leaving 43 specimens with eligible terminal observations.','leaving 43 specimens with eligible terminal observations and eight or nine terminal test specimens per fold.')
edit('05_surface_results.tex','the classical row is its selected current-corrosion model under grouped holdout;','the classical row is its selected current-corrosion model under grouped holdout, with 159 test observations from ten specimens reconstructed from the saved specimen IDs and original split definition;') if 'the classical row is' in (base/'05_surface_results.tex').read_text() else None
# Match capitalization in the actual caption.
p=base/'05_surface_results.tex';t=p.read_text().replace('The classical row is its selected current-corrosion model under grouped holdout;','The classical row is its selected current-corrosion model under grouped holdout, with 159 test observations from ten specimens reconstructed from the saved IDs and split definition;');p.write_text(t)
edit('06_structural_results.tex',r'\section{The limited post-onset result}',r'''\subsection{Paired specimen errors with the model family fixed}
The near-tie can be examined without retraining by pairing metadata-only Ridge and metadata+HSV Ridge predictions for the same specimen in the same fold. For each specimen, absolute terminal errors are averaged across its two held-out evaluations. The difference is defined as image-enhanced error minus metadata-only error, so a negative value favours adding HSV features.

Adding HSV improves \pairedImproved{} specimens and worsens \pairedWorsened{}. The mean paired difference is approximately $+\pairedMean$\,kN and the median is $+\pairedMedian$\,kN. Figure~\ref{fig:paired} shows that the near-zero mean combines improvements and worsenings. These quantities weight each specimen equally, whereas Table~\ref{tab:ablation} weights each fold equally; the small difference between the two mean-difference calculations is expected. This is a descriptive analysis of selected saved models, not a significance test or an equivalence analysis.

\fig{paired_specimen_errors}{1}{Paired effect of adding HSV descriptors to a Ridge metadata model for 48 specimens. Each point is the change in that specimen's mean absolute terminal error across two held-out evaluations, using the same specimen partitions for both configurations. Negative values favour metadata+HSV; positive values favour metadata alone. There are \pairedImproved{} improvements and \pairedWorsened{} worsenings. The dashed line is the specimen-weighted mean, approximately $+\pairedMean$\,kN. Specimens are sorted for readability. This descriptive comparison retains the original model-selection limitations.}{fig:paired}

\section{The limited post-onset result}''')
edit('09_limitations.tex','the availability and measurement timing of each field in a future deployment need independent assessment.','the availability and measurement timing of each field in a future deployment need independent assessment. In particular, cover is recorded as a failure-surface quantity; the saved feature definition does not establish that its value would have been known before destructive testing. No early-use claim should assume that availability without verification.')
edit('07_proxy_status.tex',r'\fig{threshold_status}{1}',r'\fig{threshold_status}{.90}')
edit('11_reproducibility.tex',r'\toprule Claim or output & Source',r'\caption[Evidence source map]{Saved repository sources for the report. Paths are relative to the repository root.}\label{tab:sourcemap}\\'+ '\n'+r'\toprule Claim or output & Source')
edit('11_reproducibility.tex','\n'+r'\section{Current software defects and chronology}',r'''
The paired diagnostic added after first-draft review reads the metadata-only Ridge and metadata+HSV Ridge terminal-fold prediction files under the same pooled experiment. It verifies matching specimen/split keys and equal target values, averages absolute errors over each specimen's two held-out evaluations, and then weights the 48 specimen differences equally. The complete paired data and source hashes are saved in \path{report_v2/tables/paired_specimen_errors.csv} and \path{report_v2/evidence/paired_diagnostics.json}. This is a new aggregation of saved predictions, not a model refit.

\section{Current software defects and chronology}''')
edit('11_reproducibility.tex',r'python report\_v2/scripts/make\_figures.py',r'python report\_v2/scripts/make\_figures.py\\'+'\n'+r'python report\_v2/scripts/paired\_diagnostics.py')
edit('11_reproducibility.tex',r'''latexmk -pdf -interaction=nonstopmode\\
\hspace*{1em}-halt-on-error thesis.tex''',r'latexmk -pdf -interaction=nonstopmode -halt-on-error thesis.tex')
edit('11_reproducibility.tex','The displayed command is one shell command, split here for readability. ','')
# Short list entries leave standalone figure/table captions intact in the body.
shorttabs={'tab:design':'Observed campaign design combinations','tab:surfacehistory':'Historical peak-rust results and protocol scope','tab:robustselection':'Final robustness-selected structural models','tab:ablation':'Pooled terminal-load feature-family results','tab:thresholds':'Threshold counts for model-derived wire loss','tab:classsplits':'Prepared four-class data splits','tab:postfull':'Complete post-onset sensitivity results','tab:meshfull':'Complete within-mesh results'}
for p in base.glob('*.tex'):
 t=p.read_text()
 t=re.sub(r'\\caption\{(.*?)\}\\label\{([^}]+)\}',lambda m:r'\caption['+shorttabs.get(m[2],m[2])+']{'+m[1]+r'}\label{'+m[2]+'}',t,flags=re.S)
 p.write_text(t)
# Article revisions: move design context early, add a paired diagnostic and compact controls.
p=OUT/'article/v2/article.tex';t=p.read_text()
t=t.replace('Metadata-only Ridge achieves','Scoring uses held-out terminal images, rather than a fixed early horizon. Metadata-only Ridge achieves')
t=t.replace('Accordingly, the selected feature-family comparisons below are exploratory;','The present question is incremental capacity estimation with a metadata control, which is distinct from detecting visible corrosion. This focused review does not establish an exhaustive novelty claim. Accordingly, the selected feature-family comparisons below are exploratory;')
t=t.replace('Within-mesh analyses repeat the comparison separately for the 24 specimens in each mesh group.','Within-mesh analyses repeat the comparison separately for the 24 specimens in each mesh group, with four or five terminal test specimens per fold.')
t=t.replace('leaving 43 terminal specimens.','leaving 43 terminal specimens and eight or nine terminal test specimens per fold.')
start=t.index(r'\begin{figure*}');end=t.index(r'\end{figure*}',start)+len(r'\end{figure*}')
fig=t[start:end];t=t[:start]+t[end:]
pos=t.index(r'\subsection{Target and information flow}');t=t[:pos]+fig+'\n\n'+t[pos:]
paired=r'''
\subsection{Paired errors with Ridge fixed}
Pairing saved metadata-only and metadata+HSV Ridge predictions by specimen and split makes their small average difference more interpretable. We average absolute errors over each specimen's two held-out evaluations and then compare the two configurations with equal specimen weights. Adding HSV improves \pairedImproved{} specimens and worsens \pairedWorsened{}. The mean change is approximately $+\pairedMean$\,kN and the median is $+\pairedMedian$\,kN, where positive values indicate worse error with HSV.

\begin{figure*}[t]\centering
\includegraphics[width=.89\textwidth]{\shared/figures/paired_specimen_errors.pdf}
\caption{Paired change in mean absolute terminal error when adding HSV descriptors to Ridge metadata inputs. The same specimen/split keys are paired, and two held-out evaluations are averaged for each of 48 specimens. Negative values favour the image-enhanced model. There are \pairedImproved{} improvements and \pairedWorsened{} worsenings; the dashed line is the specimen-weighted mean. This is descriptive analysis after selection, not a confidence interval, significance test, or equivalence analysis.}\label{fig:paired}
\end{figure*}
Figure~\ref{fig:paired} shows that a near-zero mean combines gains and losses. Its specimen weighting differs from Table~\ref{tab:ablation}'s equal weighting of folds, so the two average differences need not be identical. Fixing the model family sharpens the descriptive comparison but does not remove the original selection limitations.

'''
t=t.replace(r'\subsection{A limited post-onset improvement}',paired+r'\subsection{A limited post-onset improvement}')
compact=r'''
\begin{table}[t]\centering
\caption{Selected controls for terminal load. Each within-mesh row uses 24 specimens over ten folds. LOCO uses 48 specimens over two directions. The full within-mesh comparison has seven feature families per subset; all selected families have negative mean test $R^2$. MAE is in kN.}\label{tab:controls}
\footnotesize
\begin{tabular}{llrrr}\toprule
Subset & Features / model & MAE & $R^2$ & $\rho$\\\midrule
4 meshes & Metadata / Ridge & .208 & -1.476 & .301\\
4 meshes & All / CatBoost & .194 & -.998 & .081\\
7 meshes & Metadata / Ridge & .216 & -3.093 & -.050\\
7 meshes & HSV / CatBoost & .137 & -.386 & .460\\
LOCO & Metadata / GB & .465 & -4.639 & .217\\\bottomrule
\end{tabular}
\end{table}
Here ``All'' means metadata+RGB+HSV, and GB denotes GradientBoosting. The non-metadata row in each mesh group is that group's lowest-MAE selected feature family.

'''
t=t.replace(r'\subsection{Downstream and development status}',compact+r'\subsection{Downstream and development status}')
t=t.replace('Observation-weighted training also differs from equal specimen weighting.','Observation-weighted training also differs from equal specimen weighting. Cover is recorded as a failure-surface quantity; its availability before destructive testing is not established by the saved feature definition. An early-use experiment must verify that availability rather than assume it.')
p.write_text(t)
# Final layout and language refinements arising from full-page inspection.
for name,changes in {
 '03_dataset.tex':[(r'\fig{dataset_supervision}{1}',r'\fig{dataset_supervision}{.88}'),('The dataset supports a strong description of visible condition and a bounded evaluation of terminal endpoints. The next chapter explains how evaluation regimes preserve the specimen unit while changing the population being tested.','The following chapter defines specimen-disjoint evaluation and the population tested by each regime.')],
 '04_methods.tex':[(r'\fig{evaluation_regimes}{1}',r'\fig{evaluation_regimes}{.82}')],
 '06_structural_results.tex':[(r'\fig{capacity_ablation}{1}',r'\fig{capacity_ablation}{.90}'),(r'\fig{paired_specimen_errors}{1}',r'\fig{paired_specimen_errors}{.90}'),(r'\fig{confounding}{1}',r'\fig{confounding}{.92}'),('a clinically or mechanically meaningful gain','an engineering-relevant gain')],
 '11_reproducibility.tex':[(r'\begin{longtable}{p{.25\textwidth}p{.68\textwidth}}',r'\begin{longtable}{>{\raggedright\arraybackslash}p{.25\textwidth}>{\raggedright\arraybackslash}p{.68\textwidth}}')]
}.items():
 p=base/name;t=p.read_text()
 for old,new in changes:t=t.replace(old,new)
 p.write_text(t)
# Preserve the threshold table in the appendix; the main chapter uses the figure.
p=base/'07_proxy_status.tex';t=p.read_text();start=t.index(r'\begin{table}');end=t.index(r'\end{table}',start)+len(r'\end{table}')
threshold_table=t[start:end];t=t[:start]+t[end:];t=t.replace(r'Table~\ref{tab:thresholds} reports',r'Figure~\ref{fig:thresholds} reports')
t=t.replace(r'\section{Why this is not validated prognosis}',r'\FloatBarrier'+'\n'+r'\section{Why this is not validated prognosis}');p.write_text(t)
p=base/'11_reproducibility.tex';t=p.read_text().replace(r'\section{Current software defects and chronology}',threshold_table+'\n'+r'\FloatBarrier'+'\n'+r'\section{Current software defects and chronology}');p.write_text(t)
# Keep synthesis figures ahead of their conclusions and the ablation table ahead of interpretation.
p=base/'05_surface_results.tex';t=p.read_text().replace(r'\section{Answer to the surface question}',r'\FloatBarrier'+'\n'+r'\section{Answer to the surface question}');p.write_text(t)
p=base/'06_structural_results.tex';t=p.read_text();needle=r'\input{\shared/tables/pooled_capacity.tex}'+'\n'+r'\end{table}'
t=t.replace(needle,needle+'\n'+r'\FloatBarrier');p.write_text(t)
print('Created separate thesis and article v2 sources implementing C1–C8.')
