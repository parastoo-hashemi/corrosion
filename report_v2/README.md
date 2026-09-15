# Ferrocement report rebuild

Start with the revised IEEE article, `article/v2/article.pdf` (5 pages), then
`thesis/v2/thesis.pdf` (37 pages). Both are research manuscripts for review.
No venue acceptance or institution-specific thesis approval is implied.

## Package map

| Material | Path within this directory |
|---|---|
| Revised thesis / modular source | `thesis/v2/thesis.pdf`, `thesis/v2/thesis.tex`, `thesis/v2/chapters/` |
| Revised IEEE article / source | `article/v2/article.pdf`, `article/v2/article.tex` |
| First drafts retained for comparison | `thesis/thesis.pdf` (44 pages), `article/article.pdf` (5 pages), adjacent sources |
| Scientific-writing rubric / literature verification | `RESEARCH_NOTES.md`, `references/SOURCES.md` |
| First-draft critique / response | `critique/V1_REVIEW.md`, `critique/V2_RESPONSE.md` |
| Decisions / delivery guide | `DECISIONS.md`, `MORNING_SUMMARY.md` |
| Claim-to-source audit / final checks | `VERIFICATION_LOG.md`, `FINAL_VERIFICATION.md`, `qa/` |
| Shared figures and provenance | `figures/PROVENANCE.md`, `figures/PAIRED_PROVENANCE.md` |
| Full-precision result tables | `tables/*.csv` |
| Shared bibliography | `references/references.bib` |

The v1 prose remains a first draft. Shared figure correctness fixes also appear
in its rebuilt PDF; see decision 19 and the critique-response addendum. The
original v1 checkpoint is retained in Git.

## Compile all four documents

These commands use the environment verified on this computer. TeX Live 2026
provides `latexmk`, `pdflatex`, BibTeX, IEEEtran, titlesec, and flushend.

```bash
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion
/opt/anaconda3/envs/env/bin/python report_v2/scripts/build_reports.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/validate_documents.py
```

Each document can also be compiled separately:

```bash
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion/report_v2/thesis
latexmk -pdf -interaction=nonstopmode -halt-on-error thesis.tex
```

```bash
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion/report_v2/thesis/v2
latexmk -pdf -interaction=nonstopmode -halt-on-error thesis.tex
```

```bash
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion/report_v2/article
latexmk -pdf -interaction=nonstopmode -halt-on-error article.tex
```

```bash
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion/report_v2/article/v2
latexmk -pdf -interaction=nonstopmode -halt-on-error article.tex
```

`latexmk` runs the required BibTeX and cross-reference passes. Existing vector
figures, tables, and bibliography suffice for compilation; no training is needed.

## Reproduce the saved-output analysis and figures

Requires this complete repository, including the local `Data/Images_dataset.zip`
and saved modelling outputs. Run in the stated order:

```bash
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion
/opt/anaconda3/envs/env/bin/python report_v2/scripts/audit_evidence.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/make_figures.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/paired_diagnostics.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/build_reports.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/validate_documents.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/render_review.py
```

No script above fits a model. The audit checks all archived PNGs without
extracting them, so it performs more I/O than a PDF-only build. Plot generation
uses the saved CSVs. `render_review.py` uses Poppler and produces ignored page
PNGs/contact sheets under `qa/`; its JSON records which PDF hashes were rendered.
Those images still require manual inspection after any future edit.

`scripts/revise_drafts.py` reconstructs the delivered v2 source trees from v1
and the recorded revision operations. It is not part of routine compilation:
running it after manually editing v2 would replace those edits. Similarly,
`make_bibliography.py` rebuilds the shared bibliography from the verified records.

## Environment and reproduction limits

Exact report-runtime versions are in `evidence/report_environment.json`:
Python 3.13.12, NumPy 2.4.3, pandas 3.0.1, SciPy 1.17.0, matplotlib 3.10.8,
Pillow 12.1.1, PyYAML 6.0.3, scikit-learn 1.8.0, and pypdf 6.9.0.
On another computer, use a Python environment with those packages and a TeX
installation with the named packages; replace the absolute paths accordingly.

This environment reproduces reporting and aggregation. It does not recover the
original historical training environment. Current modelling-source corruption
and the YAML category defect are documented, not repaired. Generated PDFs may
have different binary hashes after rebuilding because build timestamps change;
the checks record the actual output hashes rather than claim bit-for-bit
determinism.
