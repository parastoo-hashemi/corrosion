# Delivery cleanup plan

## Authorization, baseline, and decisions

The user explicitly requested execution of `CODEX_DELIVERY_CLEANUP_PROMPT.md`.
Work is confined to local branch `cleanup/delivery-prep`, created from
`report-rebuild-codex-v3` at `7e69d7a`. The original branch and `master` remain
untouched. No pushes, merges, rebases, tags, or history rewrites are authorized.

Initial state included a staged deletion of `activity_report/CODEX_AUTONOMOUS_PROMPT.md`
and an untracked cleanup prompt. The deleted prompt's original content will be
archived from the starting commit; its old working path will remain absent.
The cleanup prompt will be archived too. Neither is an instruction source beyond
what the user explicitly authorized in this session.

Full pre-cleanup backup (includes `.git`, ignored data/models, and the index state):
`/Users/parastoo/All_projects/Proj_corrosion/corrosion_pre_cleanup_backup_20260916_092925.tar.gz`.
Archive completion and readback verification must precede Stage 4. Stage 1 is
read-only; its records were prepared outside the repository under `/tmp`.

**No DELETE actions are planned.** Duplicate documentation still has historical
value. Caches, OS metadata and empty folders are left alone; ignore rules prevent
future additions. Existing tracked cache/editor material is not bulk-untracked.

## Stage 1: full inventory

The scan includes ignored/hidden files, excluding only `.git` internals from the
content inventory (they remain in the full backup). It covers 16,140 files,
48,923,586,786 bytes, 169 Python files and 122 Markdown files. Every Python source
was parsed for imports and path-bearing string literals; all parsed successfully.
Every Markdown file was read into the content review, with title, section content,
role, duplicates and conflicts assessed individually. No Markdown is deleted.
Byte-identical main_4_old/main_4 records retain both original identities.

Evidence: `report_cleanup/all_files_before.json`, `script_dependencies.json`,
`markdown_audit.json`, `reference_searches.json`, and `references/`.
The per-Markdown record identifies the actual title and content sections rather
than classifying by filename alone. Generated dataset/specification/experiment
Markdown remains attached to its scientific outputs; old planning is archived.

Inventory/search commands run from repository root:

```bash
git status --porcelain=v2
git ls-files
rg --files --hidden -g '!**/.git/**' -g '*.md' -g '*.py' -g '*.yaml' -g '*.toml'
find . -path './.git' -prune -o -maxdepth 2 -type d -print
git grep -n -E 'from corrosion\.(main|main_2)|from src\.|sys.path.insert|parents\[|"main_4"' -- '*.py'
rg --hidden --no-ignore -n -g '!.git/**' -g '*.yaml' -g '*.toml' -g '*.json' -g '*.csv' '/Users/|main_4/|main_3/|main_2/|main_first/'
```

The Git import/path search returned 129 lines; config/manifest path search returned
1,720 lines. Full results are retained. `rg --files` alone excludes ignored files;
the separate recursive filesystem/content scan deliberately includes those files.

## Top-level classification and important assets

| Path | Classification | Decision / future use |
|---|---|---|
| Data/ | GENERATED OUTPUT — PRESERVE (also raw input) | Keep all bytes, workbook versions, raw/augmented images, archives, variants and manifests |
| Documentation/ | Mixed PRESERVE / MOVE / ARCHIVE | Keep source PDFs and generated reports; curate code explanation; archive dated plans, with every action listed below |
| main_first/ | KEEP | Exploratory phase; physical name appears in code and history; no executable rename |
| main/ | KEEP | Classical phase; qualified imports and model paths depend on name |
| main_2/ | KEEP | Embedding phase; imports, path constants and saved artifacts depend on name |
| main_3/ | KEEP | Interpretable phase; src bootstrap, TOML paths and reports depend on layout |
| main_4/ | KEEP | Mature structural phase; relative src imports, package-relative Data/configs/outputs and saved manifests depend on layout |
| main_4_old/ | KEEP | Retained snapshot; not proven identical in scientific state; only reviewed historical Markdown relocated |
| augmentation/ | KEEP | Data preparation, code, figures and tables; preserve seed/splits/parameters |
| activity_report/ | GENERATED OUTPUT — PRESERVE | All manuscript/PDF/figures/tables/bib bytes fixed; archive notes behind a compatibility directory link |
| report_v2/ | Mixed KEEP / GENERATED OUTPUT — PRESERVE / ARCHIVE | Preserve all six PDFs, sources, tables, bibliography and figures; archive evidence/QA/reviews with compatibility links |
| emiling/ | GENERATED OUTPUT — PRESERVE | Historical exports; all candidate hashes remain unchanged |
| out/ | UNCERTAIN — DO NOT TOUCH | Mixed output/build copies; ownership/dependencies not sufficiently clear for removal |
| tmp/ | UNCERTAIN — DO NOT TOUCH | Empty local directory; no benefit warrants destruction |
| catboost_info/ | UNCERTAIN — DO NOT TOUCH | Training log/cache history may be useful; ignored, not deleted |
| .idea/ | UNCERTAIN — DO NOT TOUCH | Existing editor settings, some tracked; ignore future files without erasing user settings |
| .DS_Store and existing build/cache files | KEEP | Ignore future accumulation; retain pre-existing bytes rather than claim zero references |
| .git/ | KEEP | History and starting branch refs preserved; backup includes entire directory |
| .gitignore | KEEP / improve | Add scoped true build/cache rules; do not hide scientific CSV/JSON/PNG/PDF artifacts |
| __init__.py | KEEP | Package marker used by qualified imports |
| CLAUDE.md | KEEP / improve | Short accurate maintainer entry guide, original archived |
| AUGMENTATION_PLAN.md, REPORT_PLANNING.md, DECISIONS.md, MORNING_SUMMARY.md | ARCHIVE | Preserve dated planning/decisions away from front page; useful context summarized in docs |

All model files (`.joblib`, `.pkl`, `.pt`), PNG/PDF figures, CSV/JSON/parquet tables,
workbooks, split manifests, source TeX/Bib, generated Markdown and raw data are
included in the preservation snapshot. The full baseline also covers caches and
source files, so unplanned changes can be detected beyond the output subset.
Per-file classification in `file_classification.csv` expands this table.

## Stage 2 / 3: dependency decisions

### Why implementation directories will not be renamed

- `main` and `main_2` import `corrosion.main...` / `corrosion.main_2...`; saved
  manifests use their existing artifact paths. Renaming needs package/path surgery.
- `main_3/scripts/_bootstrap.py` and `src/config.py` resolve the current parent
  hierarchy; TOML binds local outputs and sibling data. Manuscripts cite the phase.
- `main_4/src/corrosion_proxy_rul/utils_paths.py` derives config, Data and output
  locations from its package directory. Entry scripts insert relative `src`.
  Config/manifests/report citations use those original paths.
- `main_first` is both a legitimate historical directory and a corruption token
  in unrelated source/config text. A cosmetic rename cannot fix those defects.
- `main_4_old`, copied local Data trees, and `out` are not proven redundant. They
  remain in place rather than merging or deduplicating scientific histories.

The graph is recorded in `script_dependencies.json` and the 129-line Git search.
Each name also has a whole-repository search below. This is an inspected graph,
not an assumption that Python directories can never be renamed.

### Archive strategy and compatibility

Use one archive, `archive/agent_working_notes/`, mirroring original paths. Directory
moves for QA/evidence/critique/notes retain relative symbolic links at old locations.
Individual records cited by immutable scripts, LaTeX, provenance or saved manifests
also retain links. Original text stays byte-identical. This avoids changing code
paths, scientific manifests, frozen manuscripts, or hash ledgers. Links are part of
the delivery and must survive copying. Pure internal references are historical;
interpret their original root from the mirrored tree and move manifest.

For README replacements, move the original into the archive and write a current
entry guide at the original path. Generated reports that use atomic replacement
remain in place. Do not turn source/data directories into symlinks or change import
roots. No changes to algorithms, execution flow, configs, or output values.

A future student may need every archived record to reconstruct decisions, so none
is deleted. Curated docs capture the current phase map, output locations, target
units, grouping/evaluation boundaries, augmentation state, and unresolved issues.

### Exact search results for each proposed action

Each action was searched by both full path and basename with `rg --hidden --no-ignore
-n -F -g '!.git/**' -- QUERY .`, covering ignored text, code, configs, LaTeX, Markdown,
JSON/CSV manifests and shell/notebook files if present. Binary payloads are not
interpreted as path instructions. The exact argument list, exit code, result count,
and full matching lines are in `reference_searches.json` and `references/`.

| Old path | Action / destination | Compatibility | Reason / evidence |
|---|---|---|---|
| `report_v2/evidence` | ARCHIVE → `archive/agent_working_notes/report_v2/evidence` | relative symlink | Historical evidence/review records; preserve bytes and original script/report lookup paths. Searches: `references/000.txt`, `references/001.txt`. |
| `report_v2/qa` | ARCHIVE → `archive/agent_working_notes/report_v2/qa` | relative symlink | Historical evidence/review records; preserve bytes and original script/report lookup paths. Searches: `references/002.txt`, `references/003.txt`. |
| `report_v2/critique` | ARCHIVE → `archive/agent_working_notes/report_v2/critique` | relative symlink | Historical evidence/review records; preserve bytes and original script/report lookup paths. Searches: `references/004.txt`, `references/005.txt`. |
| `activity_report/notes` | ARCHIVE → `archive/agent_working_notes/activity_report/notes` | relative symlink | Historical evidence/review records; preserve bytes and original script/report lookup paths. Searches: `references/006.txt`, `references/007.txt`. |
| `AUGMENTATION_PLAN.md` | ARCHIVE → `archive/agent_working_notes/AUGMENTATION_PLAN.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/008.txt`. |
| `CLAUDE.md` | ARCHIVE_REPLACE → `archive/agent_working_notes/CLAUDE.md` | none; original archived or entry guide replaced | Keep a concise current entry guide; preserve the original documentation and its claims in the archive. Searches: `references/009.txt`. |
| `DECISIONS.md` | ARCHIVE → `archive/agent_working_notes/DECISIONS.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/010.txt`. |
| `Documentation/augment_dataset_code_explanation.md` | MOVE → `docs/reference/augmentation_code.md` | none; original archived or entry guide replaced | Detailed function and preprocessing reference; useful to future maintainers. Limitations remain disclosed; original text unchanged. Searches: `references/011.txt`, `references/012.txt`. |
| `Documentation/augmentation_email_analysis.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_email_analysis.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/013.txt`, `references/014.txt`. |
| `Documentation/augmentation_independent_plan.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_independent_plan.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/015.txt`, `references/016.txt`. |
| `Documentation/augmentation_journal_plan.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_journal_plan.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/017.txt`, `references/018.txt`. |
| `Documentation/augmentation_methodology_final.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_methodology_final.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/019.txt`, `references/020.txt`. |
| `Documentation/augmentation_methodology_report.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_methodology_report.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/021.txt`, `references/022.txt`. |
| `Documentation/augmentation_methodology_review.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_methodology_review.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/023.txt`, `references/024.txt`. |
| `Documentation/augmentation_objective_decision.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_objective_decision.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/025.txt`, `references/026.txt`. |
| `Documentation/augmentation_phase1_intent.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_phase1_intent.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/027.txt`, `references/028.txt`. |
| `Documentation/augmentation_phase2_professor_plan.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_phase2_professor_plan.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/029.txt`, `references/030.txt`. |
| `Documentation/augmentation_readiness_assessment.md` | ARCHIVE → `archive/agent_working_notes/Documentation/augmentation_readiness_assessment.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/031.txt`, `references/032.txt`. |
| `Documentation/codex/make_splits_prompt.md` | ARCHIVE → `archive/agent_working_notes/Documentation/codex/make_splits_prompt.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/033.txt`, `references/034.txt`. |
| `Documentation/final_augmentation_strategy.md` | ARCHIVE → `archive/agent_working_notes/Documentation/final_augmentation_strategy.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/035.txt`, `references/036.txt`. |
| `Documentation/final_strategy.md` | ARCHIVE → `archive/agent_working_notes/Documentation/final_strategy.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/037.txt`, `references/038.txt`. |
| `Documentation/project_review.md` | ARCHIVE → `archive/agent_working_notes/Documentation/project_review.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/039.txt`, `references/040.txt`. |
| `Documentation/splitting_strategy.md` | ARCHIVE → `archive/agent_working_notes/Documentation/splitting_strategy.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/041.txt`, `references/042.txt`. |
| `Documentation/verification_audit.md` | ARCHIVE → `archive/agent_working_notes/Documentation/verification_audit.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/043.txt`, `references/044.txt`. |
| `MORNING_SUMMARY.md` | ARCHIVE → `archive/agent_working_notes/MORNING_SUMMARY.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/045.txt`. |
| `REPORT_PLANNING.md` | ARCHIVE → `archive/agent_working_notes/REPORT_PLANNING.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/046.txt`. |
| `activity_report/CODEX_DELIVERY_CLEANUP_PROMPT.md` | ARCHIVE → `archive/agent_working_notes/activity_report/CODEX_DELIVERY_CLEANUP_PROMPT.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/047.txt`, `references/048.txt`. |
| `augmentation/README.md` | ARCHIVE_REPLACE → `archive/agent_working_notes/augmentation/README.md` | none; original archived or entry guide replaced | Keep a concise current entry guide; preserve the original documentation and its claims in the archive. Searches: `references/049.txt`, `references/050.txt`. |
| `main/README.md` | ARCHIVE_REPLACE → `archive/agent_working_notes/main/README.md` | none; original archived or entry guide replaced | Keep a concise current entry guide; preserve the original documentation and its claims in the archive. Searches: `references/050.txt`, `references/051.txt`. |
| `main_2/README.md` | ARCHIVE_REPLACE → `archive/agent_working_notes/main_2/README.md` | none; original archived or entry guide replaced | Keep a concise current entry guide; preserve the original documentation and its claims in the archive. Searches: `references/050.txt`, `references/052.txt`. |
| `main_3/README.md` | ARCHIVE_REPLACE → `archive/agent_working_notes/main_3/README.md` | none; original archived or entry guide replaced | Keep a concise current entry guide; preserve the original documentation and its claims in the archive. Searches: `references/050.txt`, `references/053.txt`. |
| `main_3/reports/meeting_report/executive_summary.md` | ARCHIVE → `archive/agent_working_notes/main_3/reports/meeting_report/executive_summary.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/054.txt`, `references/055.txt`. |
| `main_3/reports/meeting_report/figures_explained.md` | ARCHIVE → `archive/agent_working_notes/main_3/reports/meeting_report/figures_explained.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/056.txt`, `references/057.txt`. |
| `main_3/reports/meeting_report/limitations_and_next_steps.md` | ARCHIVE → `archive/agent_working_notes/main_3/reports/meeting_report/limitations_and_next_steps.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/058.txt`, `references/059.txt`. |
| `main_3/reports/meeting_report/main2_vs_main3.md` | ARCHIVE → `archive/agent_working_notes/main_3/reports/meeting_report/main2_vs_main3.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/060.txt`, `references/061.txt`. |
| `main_3/reports/meeting_report/results_analysis.md` | ARCHIVE → `archive/agent_working_notes/main_3/reports/meeting_report/results_analysis.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/062.txt`, `references/063.txt`. |
| `main_3/reports/meeting_report/talking_points.md` | ARCHIVE → `archive/agent_working_notes/main_3/reports/meeting_report/talking_points.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/064.txt`, `references/065.txt`. |
| `main_3/reports/meeting_report/technical_report.md` | ARCHIVE → `archive/agent_working_notes/main_3/reports/meeting_report/technical_report.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/066.txt`, `references/067.txt`. |
| `main_4/BENCHMARK_DIAGNOSTICS.md` | ARCHIVE → `archive/agent_working_notes/main_4/BENCHMARK_DIAGNOSTICS.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/068.txt`, `references/069.txt`. |
| `main_4/CODEBASE_GUIDE.md` | ARCHIVE → `archive/agent_working_notes/main_4/CODEBASE_GUIDE.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/070.txt`, `references/071.txt`. |
| `main_4/COMPLETE_PROJECT_REPORT.md` | ARCHIVE → `archive/agent_working_notes/main_4/COMPLETE_PROJECT_REPORT.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/072.txt`, `references/073.txt`. |
| `main_4/CSV_SCHEMA_AUDIT.md` | ARCHIVE → `archive/agent_working_notes/main_4/CSV_SCHEMA_AUDIT.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/074.txt`, `references/075.txt`. |
| `main_4/FEATURE_DIAGNOSTICS.md` | ARCHIVE → `archive/agent_working_notes/main_4/FEATURE_DIAGNOSTICS.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/076.txt`, `references/077.txt`. |
| `main_4/FIGURE_EXPLANATION_GUIDE.md` | ARCHIVE → `archive/agent_working_notes/main_4/FIGURE_EXPLANATION_GUIDE.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/078.txt`, `references/079.txt`. |
| `main_4/FIGURE_REVIEW.md` | ARCHIVE → `archive/agent_working_notes/main_4/FIGURE_REVIEW.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/080.txt`, `references/081.txt`. |
| `main_4/FIXES_APPLIED.md` | ARCHIVE → `archive/agent_working_notes/main_4/FIXES_APPLIED.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/082.txt`, `references/083.txt`. |
| `main_4/IMPLEMENTATION_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4/IMPLEMENTATION_PLAN.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/084.txt`, `references/085.txt`. |
| `main_4/MODEL_IMPROVEMENTS_APPLIED.md` | ARCHIVE → `archive/agent_working_notes/main_4/MODEL_IMPROVEMENTS_APPLIED.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/086.txt`, `references/087.txt`. |
| `main_4/MODEL_IMPROVEMENT_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4/MODEL_IMPROVEMENT_PLAN.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/088.txt`, `references/089.txt`. |
| `main_4/MODEL_IMPROVEMENT_RESULTS.md` | ARCHIVE → `archive/agent_working_notes/main_4/MODEL_IMPROVEMENT_RESULTS.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/090.txt`, `references/091.txt`. |
| `main_4/NEXT_STEPS_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4/NEXT_STEPS_PLAN.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/092.txt`, `references/093.txt`. |
| `main_4/OUTPUT_REVIEW.md` | ARCHIVE → `archive/agent_working_notes/main_4/OUTPUT_REVIEW.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/094.txt`, `references/095.txt`. |
| `main_4/OUTPUT_VISUALIZATION_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4/OUTPUT_VISUALIZATION_PLAN.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/096.txt`, `references/097.txt`. |
| `main_4/PROJECT_AUDIT.md` | ARCHIVE → `archive/agent_working_notes/main_4/PROJECT_AUDIT.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/098.txt`, `references/099.txt`. |
| `main_4/PROJECT_CONSTRAINTS.md` | ARCHIVE → `archive/agent_working_notes/main_4/PROJECT_CONSTRAINTS.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/100.txt`, `references/101.txt`. |
| `main_4/PROJECT_EXPLANATION_FOR_PRESENTATION.md` | ARCHIVE → `archive/agent_working_notes/main_4/PROJECT_EXPLANATION_FOR_PRESENTATION.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/102.txt`, `references/103.txt`. |
| `main_4/README.md` | ARCHIVE_REPLACE → `archive/agent_working_notes/main_4/README.md` | none; original archived or entry guide replaced | Keep a concise current entry guide; preserve the original documentation and its claims in the archive. Searches: `references/050.txt`, `references/104.txt`. |
| `main_4/REPORT_EDIT_SUMMARY.md` | ARCHIVE → `archive/agent_working_notes/main_4/REPORT_EDIT_SUMMARY.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/105.txt`, `references/106.txt`. |
| `main_4/SCIENTIFIC_REPORT.md` | ARCHIVE → `archive/agent_working_notes/main_4/SCIENTIFIC_REPORT.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/107.txt`, `references/108.txt`. |
| `main_4/SCIENTIFIC_SOLUTION_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4/SCIENTIFIC_SOLUTION_PLAN.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/109.txt`, `references/110.txt`. |
| `main_4_old/BENCHMARK_DIAGNOSTICS.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/BENCHMARK_DIAGNOSTICS.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/069.txt`, `references/111.txt`. |
| `main_4_old/CODEBASE_GUIDE.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/CODEBASE_GUIDE.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/071.txt`, `references/112.txt`. |
| `main_4_old/COMPLETE_PROJECT_REPORT.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/COMPLETE_PROJECT_REPORT.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/073.txt`, `references/113.txt`. |
| `main_4_old/CSV_SCHEMA_AUDIT.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/CSV_SCHEMA_AUDIT.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/075.txt`, `references/114.txt`. |
| `main_4_old/FEATURE_DIAGNOSTICS.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/FEATURE_DIAGNOSTICS.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/077.txt`, `references/115.txt`. |
| `main_4_old/FIGURE_EXPLANATION_GUIDE.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/FIGURE_EXPLANATION_GUIDE.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/079.txt`, `references/116.txt`. |
| `main_4_old/FIGURE_REVIEW.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/FIGURE_REVIEW.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/081.txt`, `references/117.txt`. |
| `main_4_old/FIXES_APPLIED.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/FIXES_APPLIED.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/083.txt`, `references/118.txt`. |
| `main_4_old/IMPLEMENTATION_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/IMPLEMENTATION_PLAN.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/085.txt`, `references/119.txt`. |
| `main_4_old/MODEL_IMPROVEMENTS_APPLIED.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/MODEL_IMPROVEMENTS_APPLIED.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/087.txt`, `references/120.txt`. |
| `main_4_old/MODEL_IMPROVEMENT_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/MODEL_IMPROVEMENT_PLAN.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/089.txt`, `references/121.txt`. |
| `main_4_old/MODEL_IMPROVEMENT_RESULTS.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/MODEL_IMPROVEMENT_RESULTS.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/091.txt`, `references/122.txt`. |
| `main_4_old/NEXT_STEPS_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/NEXT_STEPS_PLAN.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/093.txt`, `references/123.txt`. |
| `main_4_old/OUTPUT_REVIEW.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/OUTPUT_REVIEW.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/095.txt`, `references/124.txt`. |
| `main_4_old/OUTPUT_VISUALIZATION_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/OUTPUT_VISUALIZATION_PLAN.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/097.txt`, `references/125.txt`. |
| `main_4_old/PROJECT_AUDIT.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/PROJECT_AUDIT.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/099.txt`, `references/126.txt`. |
| `main_4_old/PROJECT_CONSTRAINTS.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/PROJECT_CONSTRAINTS.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/101.txt`, `references/127.txt`. |
| `main_4_old/PROJECT_EXPLANATION_FOR_PRESENTATION.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/PROJECT_EXPLANATION_FOR_PRESENTATION.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/103.txt`, `references/128.txt`. |
| `main_4_old/README.md` | ARCHIVE_REPLACE → `archive/agent_working_notes/main_4_old/README.md` | none; original archived or entry guide replaced | Keep a concise current entry guide; preserve the original documentation and its claims in the archive. Searches: `references/050.txt`, `references/129.txt`. |
| `main_4_old/REPORT_EDIT_SUMMARY.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/REPORT_EDIT_SUMMARY.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/106.txt`, `references/130.txt`. |
| `main_4_old/SCIENTIFIC_REPORT.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/SCIENTIFIC_REPORT.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/108.txt`, `references/131.txt`. |
| `main_4_old/SCIENTIFIC_SOLUTION_PLAN.md` | ARCHIVE → `archive/agent_working_notes/main_4_old/SCIENTIFIC_SOLUTION_PLAN.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/110.txt`, `references/132.txt`. |
| `report_v2/DECISIONS.md` | ARCHIVE → `archive/agent_working_notes/report_v2/DECISIONS.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/010.txt`, `references/133.txt`. |
| `report_v2/FINAL_VERIFICATION.md` | ARCHIVE → `archive/agent_working_notes/report_v2/FINAL_VERIFICATION.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/134.txt`, `references/135.txt`. |
| `report_v2/MORNING_SUMMARY.md` | ARCHIVE → `archive/agent_working_notes/report_v2/MORNING_SUMMARY.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/045.txt`, `references/136.txt`. |
| `report_v2/README.md` | ARCHIVE_REPLACE → `archive/agent_working_notes/report_v2/README.md` | none; original archived or entry guide replaced | Keep a concise current entry guide; preserve the original documentation and its claims in the archive. Searches: `references/050.txt`, `references/137.txt`. |
| `report_v2/RESEARCH_NOTES.md` | ARCHIVE → `archive/agent_working_notes/report_v2/RESEARCH_NOTES.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/138.txt`, `references/139.txt`. |
| `report_v2/VERIFICATION_LOG.md` | ARCHIVE → `archive/agent_working_notes/report_v2/VERIFICATION_LOG.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/140.txt`, `references/141.txt`. |
| `report_v2/thesis/v3/FIGURE_AUDIT.md` | ARCHIVE → `archive/agent_working_notes/report_v2/thesis/v3/FIGURE_AUDIT.md` | relative symlink | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/142.txt`, `references/143.txt`. |
| `report_v2/thesis/v3/V3_CHANGE_SUMMARY.md` | ARCHIVE → `archive/agent_working_notes/report_v2/thesis/v3/V3_CHANGE_SUMMARY.md` | none; original archived or entry guide replaced | Historical planning, interpretation, audit, meeting narrative, or task prompt; current essentials extracted into curated project docs. Searches: `references/144.txt`, `references/145.txt`. |
| `activity_report/CODEX_AUTONOMOUS_PROMPT.md` | ARCHIVE_FROM_GIT → `archive/agent_working_notes/activity_report/CODEX_AUTONOMOUS_PROMPT.md` | none; original archived or entry guide replaced | Already absent and staged deleted before cleanup; retain original HEAD content without restoring the removed working path. Searches: `references/146.txt`, `references/147.txt`. |

### Search index

| Query | Matches | Exact command | Full results |
|---|---:|---|---|
| `report_v2/evidence` | 173 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/evidence .` | `report_cleanup/references/000.txt` |
| `evidence` | 882 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- evidence .` | `report_cleanup/references/001.txt` |
| `report_v2/qa` | 30 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/qa .` | `report_cleanup/references/002.txt` |
| `qa` | 75 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- qa .` | `report_cleanup/references/003.txt` |
| `report_v2/critique` | 5 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/critique .` | `report_cleanup/references/004.txt` |
| `critique` | 24 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- critique .` | `report_cleanup/references/005.txt` |
| `activity_report/notes` | 5 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- activity_report/notes .` | `report_cleanup/references/006.txt` |
| `notes` | 88 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- notes .` | `report_cleanup/references/007.txt` |
| `AUGMENTATION_PLAN.md` | 3 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- AUGMENTATION_PLAN.md .` | `report_cleanup/references/008.txt` |
| `CLAUDE.md` | 4 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- CLAUDE.md .` | `report_cleanup/references/009.txt` |
| `DECISIONS.md` | 8 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- DECISIONS.md .` | `report_cleanup/references/010.txt` |
| `Documentation/augment_dataset_code_explanation.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augment_dataset_code_explanation.md .` | `report_cleanup/references/011.txt` |
| `augment_dataset_code_explanation.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augment_dataset_code_explanation.md .` | `report_cleanup/references/012.txt` |
| `Documentation/augmentation_email_analysis.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_email_analysis.md .` | `report_cleanup/references/013.txt` |
| `augmentation_email_analysis.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_email_analysis.md .` | `report_cleanup/references/014.txt` |
| `Documentation/augmentation_independent_plan.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_independent_plan.md .` | `report_cleanup/references/015.txt` |
| `augmentation_independent_plan.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_independent_plan.md .` | `report_cleanup/references/016.txt` |
| `Documentation/augmentation_journal_plan.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_journal_plan.md .` | `report_cleanup/references/017.txt` |
| `augmentation_journal_plan.md` | 4 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_journal_plan.md .` | `report_cleanup/references/018.txt` |
| `Documentation/augmentation_methodology_final.md` | 7 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_methodology_final.md .` | `report_cleanup/references/019.txt` |
| `augmentation_methodology_final.md` | 9 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_methodology_final.md .` | `report_cleanup/references/020.txt` |
| `Documentation/augmentation_methodology_report.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_methodology_report.md .` | `report_cleanup/references/021.txt` |
| `augmentation_methodology_report.md` | 3 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_methodology_report.md .` | `report_cleanup/references/022.txt` |
| `Documentation/augmentation_methodology_review.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_methodology_review.md .` | `report_cleanup/references/023.txt` |
| `augmentation_methodology_review.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_methodology_review.md .` | `report_cleanup/references/024.txt` |
| `Documentation/augmentation_objective_decision.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_objective_decision.md .` | `report_cleanup/references/025.txt` |
| `augmentation_objective_decision.md` | 9 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_objective_decision.md .` | `report_cleanup/references/026.txt` |
| `Documentation/augmentation_phase1_intent.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_phase1_intent.md .` | `report_cleanup/references/027.txt` |
| `augmentation_phase1_intent.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_phase1_intent.md .` | `report_cleanup/references/028.txt` |
| `Documentation/augmentation_phase2_professor_plan.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_phase2_professor_plan.md .` | `report_cleanup/references/029.txt` |
| `augmentation_phase2_professor_plan.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_phase2_professor_plan.md .` | `report_cleanup/references/030.txt` |
| `Documentation/augmentation_readiness_assessment.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/augmentation_readiness_assessment.md .` | `report_cleanup/references/031.txt` |
| `augmentation_readiness_assessment.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation_readiness_assessment.md .` | `report_cleanup/references/032.txt` |
| `Documentation/codex/make_splits_prompt.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/codex/make_splits_prompt.md .` | `report_cleanup/references/033.txt` |
| `make_splits_prompt.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- make_splits_prompt.md .` | `report_cleanup/references/034.txt` |
| `Documentation/final_augmentation_strategy.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/final_augmentation_strategy.md .` | `report_cleanup/references/035.txt` |
| `final_augmentation_strategy.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- final_augmentation_strategy.md .` | `report_cleanup/references/036.txt` |
| `Documentation/final_strategy.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/final_strategy.md .` | `report_cleanup/references/037.txt` |
| `final_strategy.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- final_strategy.md .` | `report_cleanup/references/038.txt` |
| `Documentation/project_review.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/project_review.md .` | `report_cleanup/references/039.txt` |
| `project_review.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- project_review.md .` | `report_cleanup/references/040.txt` |
| `Documentation/splitting_strategy.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/splitting_strategy.md .` | `report_cleanup/references/041.txt` |
| `splitting_strategy.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- splitting_strategy.md .` | `report_cleanup/references/042.txt` |
| `Documentation/verification_audit.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation/verification_audit.md .` | `report_cleanup/references/043.txt` |
| `verification_audit.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- verification_audit.md .` | `report_cleanup/references/044.txt` |
| `MORNING_SUMMARY.md` | 3 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- MORNING_SUMMARY.md .` | `report_cleanup/references/045.txt` |
| `REPORT_PLANNING.md` | 11 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- REPORT_PLANNING.md .` | `report_cleanup/references/046.txt` |
| `activity_report/CODEX_DELIVERY_CLEANUP_PROMPT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- activity_report/CODEX_DELIVERY_CLEANUP_PROMPT.md .` | `report_cleanup/references/047.txt` |
| `CODEX_DELIVERY_CLEANUP_PROMPT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- CODEX_DELIVERY_CLEANUP_PROMPT.md .` | `report_cleanup/references/048.txt` |
| `augmentation/README.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- augmentation/README.md .` | `report_cleanup/references/049.txt` |
| `README.md` | 36 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- README.md .` | `report_cleanup/references/050.txt` |
| `main/README.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main/README.md .` | `report_cleanup/references/051.txt` |
| `main_2/README.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_2/README.md .` | `report_cleanup/references/052.txt` |
| `main_3/README.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_3/README.md .` | `report_cleanup/references/053.txt` |
| `main_3/reports/meeting_report/executive_summary.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_3/reports/meeting_report/executive_summary.md .` | `report_cleanup/references/054.txt` |
| `executive_summary.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- executive_summary.md .` | `report_cleanup/references/055.txt` |
| `main_3/reports/meeting_report/figures_explained.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_3/reports/meeting_report/figures_explained.md .` | `report_cleanup/references/056.txt` |
| `figures_explained.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- figures_explained.md .` | `report_cleanup/references/057.txt` |
| `main_3/reports/meeting_report/limitations_and_next_steps.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_3/reports/meeting_report/limitations_and_next_steps.md .` | `report_cleanup/references/058.txt` |
| `limitations_and_next_steps.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- limitations_and_next_steps.md .` | `report_cleanup/references/059.txt` |
| `main_3/reports/meeting_report/main2_vs_main3.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_3/reports/meeting_report/main2_vs_main3.md .` | `report_cleanup/references/060.txt` |
| `main2_vs_main3.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main2_vs_main3.md .` | `report_cleanup/references/061.txt` |
| `main_3/reports/meeting_report/results_analysis.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_3/reports/meeting_report/results_analysis.md .` | `report_cleanup/references/062.txt` |
| `results_analysis.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- results_analysis.md .` | `report_cleanup/references/063.txt` |
| `main_3/reports/meeting_report/talking_points.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_3/reports/meeting_report/talking_points.md .` | `report_cleanup/references/064.txt` |
| `talking_points.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- talking_points.md .` | `report_cleanup/references/065.txt` |
| `main_3/reports/meeting_report/technical_report.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_3/reports/meeting_report/technical_report.md .` | `report_cleanup/references/066.txt` |
| `technical_report.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- technical_report.md .` | `report_cleanup/references/067.txt` |
| `main_4/BENCHMARK_DIAGNOSTICS.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/BENCHMARK_DIAGNOSTICS.md .` | `report_cleanup/references/068.txt` |
| `BENCHMARK_DIAGNOSTICS.md` | 17 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- BENCHMARK_DIAGNOSTICS.md .` | `report_cleanup/references/069.txt` |
| `main_4/CODEBASE_GUIDE.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/CODEBASE_GUIDE.md .` | `report_cleanup/references/070.txt` |
| `CODEBASE_GUIDE.md` | 8 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- CODEBASE_GUIDE.md .` | `report_cleanup/references/071.txt` |
| `main_4/COMPLETE_PROJECT_REPORT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/COMPLETE_PROJECT_REPORT.md .` | `report_cleanup/references/072.txt` |
| `COMPLETE_PROJECT_REPORT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- COMPLETE_PROJECT_REPORT.md .` | `report_cleanup/references/073.txt` |
| `main_4/CSV_SCHEMA_AUDIT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/CSV_SCHEMA_AUDIT.md .` | `report_cleanup/references/074.txt` |
| `CSV_SCHEMA_AUDIT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- CSV_SCHEMA_AUDIT.md .` | `report_cleanup/references/075.txt` |
| `main_4/FEATURE_DIAGNOSTICS.md` | 6 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/FEATURE_DIAGNOSTICS.md .` | `report_cleanup/references/076.txt` |
| `FEATURE_DIAGNOSTICS.md` | 20 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- FEATURE_DIAGNOSTICS.md .` | `report_cleanup/references/077.txt` |
| `main_4/FIGURE_EXPLANATION_GUIDE.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/FIGURE_EXPLANATION_GUIDE.md .` | `report_cleanup/references/078.txt` |
| `FIGURE_EXPLANATION_GUIDE.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- FIGURE_EXPLANATION_GUIDE.md .` | `report_cleanup/references/079.txt` |
| `main_4/FIGURE_REVIEW.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/FIGURE_REVIEW.md .` | `report_cleanup/references/080.txt` |
| `FIGURE_REVIEW.md` | 6 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- FIGURE_REVIEW.md .` | `report_cleanup/references/081.txt` |
| `main_4/FIXES_APPLIED.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/FIXES_APPLIED.md .` | `report_cleanup/references/082.txt` |
| `FIXES_APPLIED.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- FIXES_APPLIED.md .` | `report_cleanup/references/083.txt` |
| `main_4/IMPLEMENTATION_PLAN.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/IMPLEMENTATION_PLAN.md .` | `report_cleanup/references/084.txt` |
| `IMPLEMENTATION_PLAN.md` | 4 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- IMPLEMENTATION_PLAN.md .` | `report_cleanup/references/085.txt` |
| `main_4/MODEL_IMPROVEMENTS_APPLIED.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/MODEL_IMPROVEMENTS_APPLIED.md .` | `report_cleanup/references/086.txt` |
| `MODEL_IMPROVEMENTS_APPLIED.md` | 6 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- MODEL_IMPROVEMENTS_APPLIED.md .` | `report_cleanup/references/087.txt` |
| `main_4/MODEL_IMPROVEMENT_PLAN.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/MODEL_IMPROVEMENT_PLAN.md .` | `report_cleanup/references/088.txt` |
| `MODEL_IMPROVEMENT_PLAN.md` | 6 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- MODEL_IMPROVEMENT_PLAN.md .` | `report_cleanup/references/089.txt` |
| `main_4/MODEL_IMPROVEMENT_RESULTS.md` | 4 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/MODEL_IMPROVEMENT_RESULTS.md .` | `report_cleanup/references/090.txt` |
| `MODEL_IMPROVEMENT_RESULTS.md` | 13 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- MODEL_IMPROVEMENT_RESULTS.md .` | `report_cleanup/references/091.txt` |
| `main_4/NEXT_STEPS_PLAN.md` | 11 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/NEXT_STEPS_PLAN.md .` | `report_cleanup/references/092.txt` |
| `NEXT_STEPS_PLAN.md` | 18 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- NEXT_STEPS_PLAN.md .` | `report_cleanup/references/093.txt` |
| `main_4/OUTPUT_REVIEW.md` | 6 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/OUTPUT_REVIEW.md .` | `report_cleanup/references/094.txt` |
| `OUTPUT_REVIEW.md` | 23 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- OUTPUT_REVIEW.md .` | `report_cleanup/references/095.txt` |
| `main_4/OUTPUT_VISUALIZATION_PLAN.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/OUTPUT_VISUALIZATION_PLAN.md .` | `report_cleanup/references/096.txt` |
| `OUTPUT_VISUALIZATION_PLAN.md` | 4 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- OUTPUT_VISUALIZATION_PLAN.md .` | `report_cleanup/references/097.txt` |
| `main_4/PROJECT_AUDIT.md` | 3 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/PROJECT_AUDIT.md .` | `report_cleanup/references/098.txt` |
| `PROJECT_AUDIT.md` | 7 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- PROJECT_AUDIT.md .` | `report_cleanup/references/099.txt` |
| `main_4/PROJECT_CONSTRAINTS.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/PROJECT_CONSTRAINTS.md .` | `report_cleanup/references/100.txt` |
| `PROJECT_CONSTRAINTS.md` | 8 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- PROJECT_CONSTRAINTS.md .` | `report_cleanup/references/101.txt` |
| `main_4/PROJECT_EXPLANATION_FOR_PRESENTATION.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/PROJECT_EXPLANATION_FOR_PRESENTATION.md .` | `report_cleanup/references/102.txt` |
| `PROJECT_EXPLANATION_FOR_PRESENTATION.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- PROJECT_EXPLANATION_FOR_PRESENTATION.md .` | `report_cleanup/references/103.txt` |
| `main_4/README.md` | 9 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/README.md .` | `report_cleanup/references/104.txt` |
| `main_4/REPORT_EDIT_SUMMARY.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/REPORT_EDIT_SUMMARY.md .` | `report_cleanup/references/105.txt` |
| `REPORT_EDIT_SUMMARY.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- REPORT_EDIT_SUMMARY.md .` | `report_cleanup/references/106.txt` |
| `main_4/SCIENTIFIC_REPORT.md` | 6 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/SCIENTIFIC_REPORT.md .` | `report_cleanup/references/107.txt` |
| `SCIENTIFIC_REPORT.md` | 32 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- SCIENTIFIC_REPORT.md .` | `report_cleanup/references/108.txt` |
| `main_4/SCIENTIFIC_SOLUTION_PLAN.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4/SCIENTIFIC_SOLUTION_PLAN.md .` | `report_cleanup/references/109.txt` |
| `SCIENTIFIC_SOLUTION_PLAN.md` | 4 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- SCIENTIFIC_SOLUTION_PLAN.md .` | `report_cleanup/references/110.txt` |
| `main_4_old/BENCHMARK_DIAGNOSTICS.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/BENCHMARK_DIAGNOSTICS.md .` | `report_cleanup/references/111.txt` |
| `main_4_old/CODEBASE_GUIDE.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/CODEBASE_GUIDE.md .` | `report_cleanup/references/112.txt` |
| `main_4_old/COMPLETE_PROJECT_REPORT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/COMPLETE_PROJECT_REPORT.md .` | `report_cleanup/references/113.txt` |
| `main_4_old/CSV_SCHEMA_AUDIT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/CSV_SCHEMA_AUDIT.md .` | `report_cleanup/references/114.txt` |
| `main_4_old/FEATURE_DIAGNOSTICS.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/FEATURE_DIAGNOSTICS.md .` | `report_cleanup/references/115.txt` |
| `main_4_old/FIGURE_EXPLANATION_GUIDE.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/FIGURE_EXPLANATION_GUIDE.md .` | `report_cleanup/references/116.txt` |
| `main_4_old/FIGURE_REVIEW.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/FIGURE_REVIEW.md .` | `report_cleanup/references/117.txt` |
| `main_4_old/FIXES_APPLIED.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/FIXES_APPLIED.md .` | `report_cleanup/references/118.txt` |
| `main_4_old/IMPLEMENTATION_PLAN.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/IMPLEMENTATION_PLAN.md .` | `report_cleanup/references/119.txt` |
| `main_4_old/MODEL_IMPROVEMENTS_APPLIED.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/MODEL_IMPROVEMENTS_APPLIED.md .` | `report_cleanup/references/120.txt` |
| `main_4_old/MODEL_IMPROVEMENT_PLAN.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/MODEL_IMPROVEMENT_PLAN.md .` | `report_cleanup/references/121.txt` |
| `main_4_old/MODEL_IMPROVEMENT_RESULTS.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/MODEL_IMPROVEMENT_RESULTS.md .` | `report_cleanup/references/122.txt` |
| `main_4_old/NEXT_STEPS_PLAN.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/NEXT_STEPS_PLAN.md .` | `report_cleanup/references/123.txt` |
| `main_4_old/OUTPUT_REVIEW.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/OUTPUT_REVIEW.md .` | `report_cleanup/references/124.txt` |
| `main_4_old/OUTPUT_VISUALIZATION_PLAN.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/OUTPUT_VISUALIZATION_PLAN.md .` | `report_cleanup/references/125.txt` |
| `main_4_old/PROJECT_AUDIT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/PROJECT_AUDIT.md .` | `report_cleanup/references/126.txt` |
| `main_4_old/PROJECT_CONSTRAINTS.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/PROJECT_CONSTRAINTS.md .` | `report_cleanup/references/127.txt` |
| `main_4_old/PROJECT_EXPLANATION_FOR_PRESENTATION.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/PROJECT_EXPLANATION_FOR_PRESENTATION.md .` | `report_cleanup/references/128.txt` |
| `main_4_old/README.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/README.md .` | `report_cleanup/references/129.txt` |
| `main_4_old/REPORT_EDIT_SUMMARY.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/REPORT_EDIT_SUMMARY.md .` | `report_cleanup/references/130.txt` |
| `main_4_old/SCIENTIFIC_REPORT.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/SCIENTIFIC_REPORT.md .` | `report_cleanup/references/131.txt` |
| `main_4_old/SCIENTIFIC_SOLUTION_PLAN.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old/SCIENTIFIC_SOLUTION_PLAN.md .` | `report_cleanup/references/132.txt` |
| `report_v2/DECISIONS.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/DECISIONS.md .` | `report_cleanup/references/133.txt` |
| `report_v2/FINAL_VERIFICATION.md` | 0 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/FINAL_VERIFICATION.md .` | `report_cleanup/references/134.txt` |
| `FINAL_VERIFICATION.md` | 6 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- FINAL_VERIFICATION.md .` | `report_cleanup/references/135.txt` |
| `report_v2/MORNING_SUMMARY.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/MORNING_SUMMARY.md .` | `report_cleanup/references/136.txt` |
| `report_v2/README.md` | 4 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/README.md .` | `report_cleanup/references/137.txt` |
| `report_v2/RESEARCH_NOTES.md` | 2 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/RESEARCH_NOTES.md .` | `report_cleanup/references/138.txt` |
| `RESEARCH_NOTES.md` | 4 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- RESEARCH_NOTES.md .` | `report_cleanup/references/139.txt` |
| `report_v2/VERIFICATION_LOG.md` | 7 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/VERIFICATION_LOG.md .` | `report_cleanup/references/140.txt` |
| `VERIFICATION_LOG.md` | 10 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- VERIFICATION_LOG.md .` | `report_cleanup/references/141.txt` |
| `report_v2/thesis/v3/FIGURE_AUDIT.md` | 3 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/thesis/v3/FIGURE_AUDIT.md .` | `report_cleanup/references/142.txt` |
| `FIGURE_AUDIT.md` | 7 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- FIGURE_AUDIT.md .` | `report_cleanup/references/143.txt` |
| `report_v2/thesis/v3/V3_CHANGE_SUMMARY.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- report_v2/thesis/v3/V3_CHANGE_SUMMARY.md .` | `report_cleanup/references/144.txt` |
| `V3_CHANGE_SUMMARY.md` | 1 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- V3_CHANGE_SUMMARY.md .` | `report_cleanup/references/145.txt` |
| `activity_report/CODEX_AUTONOMOUS_PROMPT.md` | 3 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- activity_report/CODEX_AUTONOMOUS_PROMPT.md .` | `report_cleanup/references/146.txt` |
| `CODEX_AUTONOMOUS_PROMPT.md` | 3 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- CODEX_AUTONOMOUS_PROMPT.md .` | `report_cleanup/references/147.txt` |
| `main` | 5571 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main .` | `report_cleanup/references/148.txt` |
| `main_2` | 423 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_2 .` | `report_cleanup/references/149.txt` |
| `main_3` | 764 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_3 .` | `report_cleanup/references/150.txt` |
| `main_4` | 1405 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4 .` | `report_cleanup/references/151.txt` |
| `main_first` | 156 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_first .` | `report_cleanup/references/152.txt` |
| `main_4_old` | 10 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- main_4_old .` | `report_cleanup/references/153.txt` |
| `out` | 75650 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- out .` | `report_cleanup/references/154.txt` |
| `Documentation` | 140 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- Documentation .` | `report_cleanup/references/155.txt` |
| `emiling` | 71 | `rg --hidden --no-ignore -n -F -g '!.git/**' -- emiling .` | `report_cleanup/references/156.txt` |

## Documentation conflicts and conservative choices

The old main_3 README's “final” designation conflicts with the later main_4 phase;
old report README front-loads v2 despite v3 existing; agent guidance cites a missing
main_4 requirements file and mixed working directories. One augmentation methodology
calls minimum version constraints exact installed versions. These originals are
archived, with conflicts explained in `docs/project_history.md`. Distinct 792-row/
five-class and 791-row/four-class datasets are not silently harmonized.

No authoritative manuscript choice was supplied. README will label v3 “latest
produced” and explicitly state that authority is undecided, while linking both the
original activity report and all report_v2 versions. Future work is described as
pending, never presented as a completed classifier study.

## Proposed final tree

```text
README.md                         # professor/student entry point
CLAUDE.md                         # concise maintainer guidance
DELIVERY_CLEANUP_PLAN.md
CLEANUP_HANDOFF.md
Data/                             # unchanged, local ignored assets
Documentation/                    # source documents and generated reports
main_first/ main/ main_2/ main_3/ main_4/ main_4_old/
augmentation/                     # unchanged code behaviour and prepared artifacts
activity_report/                  # immutable report, notes compatibility link
report_v2/                        # all manuscript versions and shared assets
  evidence/ qa/ critique/         # compatibility links into archive
emiling/ out/                     # retained exports / uncertain mixed tree
docs/
  project_history.md experiments.md data_dictionary.md reproduction.md known_issues.md
  reference/augmentation_code.md
archive/agent_working_notes/       # mirrored historical paths; immutable originals
report_cleanup/                   # machine-readable cleanup evidence and checks
```

## Execution and verification gates

1. Commit inventory after the read-only inspection; record the external backup.
2. Commit this plan and individual Markdown classification before any move.
3. Commit dependency results and pre-move SHA-256 output inventory.
4. Execute only listed actions; log one row per moved file; commit.
5. Write curated docs/READMEs, flag conflicts, retain all manuscript claims; commit.
6. Add only comments/docstrings to selected code; compare normalized ASTs and Python
   tokens against the baseline; preserve code used by report hash ledgers; commit.
7. Hash every preserved file after cleanup, accounting for the manifest; check
   config parsing/types, CLI help, code imports/syntax, links/report references and
   saved source hashes. Do not run full training or regenerate scientific outputs.
8. Review as professor and future student; commit final verification and handoff.

New cleanup verification scripts are tooling, not changes to scientific code.
Scientific source edits are comments/docstrings only. Existing blockers remain
recorded separately from cleanup regressions. No original scientific output may
change merely to make a verification script pass.

## Execution outcome and final review

All planned stages completed on `cleanup/delivery-prep`. The external tar archive
completed successfully; full `tar -tzf` readback confirmed all 16,140 initial files
and the Git index before any move. The archive is 52,807,580,105 bytes.

Executed 91 action groups covering 329 preserved files; no deletion. Created 26
relative compatibility links. All 122 Markdown records are accounted for (27 A,
5 B, 90 C, 0 D), plus the recovered previously deleted prompt. The separate current
README and five curated guides capture the information needed for handoff.
Eight scientific-source files received docstrings only, verified by matching
normalized ASTs and executable tokens. Source files referenced by report checksum
ledgers were not edited.

All 15,566 protected scientific input/output hashes and sizes match; all seven
primary report PDFs are byte-identical. Functional checks, CLI help, 120 report
input/figure dependencies, 96 saved source-hash records, and the existing grouped
split test pass. The initial path checker required correction to respect commented
LaTeX includes, `graphicspath`, and the report's `shared`/`fig` macros; no report
source was changed to satisfy it.

The broader inventory found drift only in untracked `.idea/workspace.xml`, outside
any cleanup action. Current IDE state is left untouched and its initial content
remains in the backup; exact hashes are disclosed in `local_state_drift.json`.
This is not an output-preservation failure. Also documented: three locally present
`main_3/src/data/` source files are ignored by the existing broad Data ignore rule.
No source/ignore surgery was made to those historical files. A complete local
bundle is required; a Git-only transfer is insufficient.

Both professor and student perspectives were reviewed against the new README and
curated guides. The repository is ready for academic review/continuation with these
explicit limits; current historical modelling defects and pending classifier
training/evaluation remain unresolved. Full outcome: `CLEANUP_HANDOFF.md`.
