# Academic delivery handoff

**Historical snapshot of the initial cleanup.** Later reorganizations supersede
the layout below. See the [current project guide](README.md) and
[maintenance archive index](archive/repository_maintenance/README.md).

The repository is ready for professor review and student onboarding **with the
complete local data/source/output bundle and the documented limits**. Scientific
inputs, results, manuscript sources and PDFs are preserved. The current modelling
source is not a verified end-to-end rerun, and a Git-only transfer is incomplete.
Start with [README.md](README.md).

## 1. Final repository tree

```text
README.md                         Project overview and entry guide
CLAUDE.md                         Concise maintainer guidance
DELIVERY_CLEANUP_PLAN.md           Classifications, dependency evidence, decisions
CLEANUP_HANDOFF.md                 This delivery record
Data/                             Unchanged raw/prepared data, variants and splits
Documentation/                    Source PDFs and generated augmentation reports
main_first/                       Exploratory prototype
main/                             Classical corrosion baseline
main_2/                           Frozen image-embedding experiment
main_3/                           Interpretable features and structural feasibility
main_4/                           Mature robustness and terminal-load study
main_4_old/                       Retained earlier baseline snapshot
augmentation/                     Four-class data preparation, not classifier training
activity_report/                  Original 70-page report and unchanged source/assets
  notes/ -> archive               Historical evidence/planning compatibility link
report_v2/                        All six thesis/article PDFs and unchanged source/assets
  thesis/ and article/            v1, v2, v3
  figures/ tables/ references/    Shared scientific assets
  scripts/                        Existing reporting tools
  evidence/ qa/ critique/        Compatibility links into archive
emiling/                          Historical export copies, unchanged
out/                              Mixed historical build/output tree, unchanged
docs/                             Five curated guides
  reference/augmentation_code.md Original detailed implementation reference
archive/agent_working_notes/       Historical records, mirrored by original path
archive/repository_maintenance/                   Move log, snapshots, dependency/check records
catboost_info/ tmp/ .idea/         Retained local state; not research entry points
__init__.py .gitignore .git/       Package marker, ignore policy and local history
```

## 2. Renames, moves, archives, and deletions

The [cleanup plan](DELIVERY_CLEANUP_PLAN.md) lists all 91 action groups, rationale,
157 exact whole-repository searches and their result locations.
The [move manifest](archive/repository_maintenance/move_manifest.csv) lists every affected file:
**329 files preserved through relocation/recovery; zero deleted**.

- 319 files were archived under one mirrored development-history tree, including
  manuscript evidence/QA, critiques, chapter plans, meeting narratives, dated
  development plans, and task prompts.
- Eight original README/agent guides were archived before writing current guides
  at their old paths.
- One detailed augmentation code explanation moved into `docs/reference/` without
  altering its text.
- One already-deleted old prompt was recovered from the starting Git commit into
  the archive; its pre-existing staged deletion at the original path was respected.
- 26 relative compatibility links retain lookup paths used by scripts, saved
  manifests, provenance or frozen manuscripts. They are part of the delivery.

No implementation directory, dataset, model, report PDF, scientific figure, metric,
split or feature definition was renamed or rewritten. Dependency inspection showed
that cosmetic `main*` renaming would require invasive import/path changes. The
phase map is provided in documentation instead. Existing caches and editor files
were not deleted; `.gitignore` now covers future true build/cache clutter.

## 3. Markdown audit: retained versus removed from primary view

All **122 initially present Markdown files** were individually classified by
content in [markdown_audit.json](archive/repository_maintenance/markdown_audit.json):

| Class | Count | Disposition |
|---|---:|---|
| A: essential user-facing or generated data/experiment documentation | 27 | 19 generated records kept in place; eight entry guides improved with originals archived |
| B: useful technical/provenance documentation | 5 | One code reference curated; four asset/bibliography-location or provenance records retained beside their assets |
| C: historical/internal records | 90 | Archived, with compatibility paths where dependencies require them |
| D: disposable obsolete/duplicate records | 0 | None deleted |

The recovered old prompt is additional to those 122 files because it was absent
at the starting filesystem snapshot. Original conflicting/obsolete assertions were
not silently corrected inside archived records. Their current interpretation is
summarized in [project history](docs/project_history.md) and
[known issues](docs/known_issues.md). Being agent-written was not a deletion criterion.

## 4. README changes

The new root README covers project overview, the 48-specimen dataset, actual
structure, phase workflow, restrained findings, safe current commands, real
dependency files, output locations, reproducibility boundaries, pending work, next
steps and report locations. It is about 1,100 words and links detailed material
rather than repeating the scientific report.

The phase READMEs now identify their historical/current role and link the shared
instructions. The report README lists all six manuscript versions. V3 is labelled
**latest produced**, while **the authoritative manuscript choice remains undecided**.
The original activity report remains linked. No report numbers or claims changed.

## 5. Supporting documentation

- [Project history](docs/project_history.md): phase map and explicit documentation conflicts.
- [Experiments](docs/experiments.md): each research question, saved outputs and historical entry points.
- [Data dictionary](docs/data_dictionary.md): observation units, target units, feature meanings and label versions.
- [Reproduction](docs/reproduction.md): verified help/check commands, separate-output preparation commands, report compilation and execution limits.
- [Known issues](docs/known_issues.md): unresolved source/config, environment, portability and scientific limitations.
- [Augmentation code reference](docs/reference/augmentation_code.md): preserved detailed function/preprocessing explanation.

The archive README explains original-path context and warns that historical prompts
and plans are records, not current instructions.

## 6. Code readability: no behavioural diffs

Only docstrings/blank lines changed in these eight existing Python files:

- `augmentation/augment_dataset.py`
- `augmentation/make_splits.py`
- `main_3/src/cv/splits.py`
- `main_4/src/corrosion_proxy_rul/config.py`
- `main_4/src/corrosion_proxy_rul/feature_engineering.py`
- `main_4/src/corrosion_proxy_rul/image_preprocessing.py`
- `main_4/src/corrosion_proxy_rul/models_rul_proxy.py`
- `main_4/src/corrosion_proxy_rul/splits.py`

The additions explain specimen grouping, leakage controls, excluded outcomes,
observed versus estimated quantities, preprocessing scope and config limitations.
**Normalized ASTs and executable tokens match the starting source exactly after
excluding docstrings/comments/layout.** No algorithms, control flow, imports,
parameters or model behaviour changed. Source files pinned by report hash ledgers
were left untouched. The new `archive/repository_maintenance/verify_delivery.py` is delivery
verification tooling, not modelling code.

## 7. Output preservation

[Preservation report](archive/repository_maintenance/output_preservation_check.md): **all 15,566
protected scientific input/output files have matching sizes and SHA-256 hashes;
zero differences**, covering 48,917,480,102 bytes. Before/after snapshots and the
empty diff are linked there. This conservative set includes raw inputs and report
sources as well as generated outputs.

The complete comparison checked 16,131 original files beyond the eight documented
Python edits and `.gitignore`. Archived README originals also match their hashes.
The 70-page original report and all six thesis/article PDFs remain byte-identical.
No training, scientific regeneration, or PDF rebuild was performed.

One untracked local IDE file, `.idea/workspace.xml`, drifted during the task. No
cleanup action targets it; its current contents were left untouched and the original
is in the full backup. The exact difference is disclosed in
[local_state_drift.json](archive/repository_maintenance/local_state_drift.json). No other unexplained
original-file drift was found. This exception is not a scientific output difference.

## 8. Functional verification

The [full check](archive/repository_maintenance/verification_full.json) reports no cleanup failures:

- All 169 pre-existing Python files parse; the eight touched files compile and pass
  both AST and executable-token invariance checks.
- Five touched main_4 modules import and six configs load via their actual loader;
  the main_3 split module imports separately. Augmentation help imports succeed.
- All 12 YAML/TOML files load syntactically and retain their original hashes.
- Three augmentation `--help` commands succeed; documented option names agree.
- All 26 compatibility links, 131 current-guide links and 120 LaTeX input/figure
  references resolve; literal repository paths in report sources still resolve.
- All 96 historical source-hash records checked still match.
- The existing main_3 test for specimen-disjoint grouping passes: one test, no fit.
- Current source/guide diffs pass whitespace checks. Original whitespace in archived
  files and verbatim search results was preserved intentionally.

Config loading and imports are deliberately not presented as a successful training
rerun. CLI checks and report-path checks do not generate new scientific results.

## 9. Unresolved reproducibility issues

- Existing `main_first` substitutions affect historical source/config semantics.
- Unquoted YAML `NO` becomes `False`; the original category/schema defect is preserved.
- The original training environment is not fully recovered. Dependency minimums
  are not a lockfile; there is no `main_4/requirements.txt`, and the augmentation
  requirements omit pandas used by split/variant scripts.
- A Git-only copy lacks ignored raw data, some models/source documents, and the
  three local `main_3/src/data/` Python files. Transfer the complete local bundle.
- Archived prose/manifests can contain old absolute paths; curated guidance uses
  current paths. Preserve compatibility symlinks during transfer.
- Four-class training/evaluation remains pending. Terminal-only structural labels,
  confounded campaigns, and model-derived threshold curves limit scientific claims.
- Manuscript authority remains a supervisor/user decision.

See [known issues](docs/known_issues.md) for the practical boundaries. None was
silently fixed by modifying saved evidence.

## 10. Deliberately untouched material

`out/`, `main_4_old` scientific contents, copied local Data/source-document trees,
`emiling`, existing caches, editor settings and `tmp/` were not deduplicated or
removed. Their historical or local role did not establish safe deletion. The full
[per-file classification](archive/repository_maintenance/file_classification.csv) records this.
All raw data, labels, predictions, metrics, models, splits, seeds, configs, scientific
assets and manuscript sources retain their bytes, except the documented source
docstrings; no scientific behaviour changed.

## 11. Final review and readiness

Read as a professor, the root guide answers the research question, evidence base,
main findings, report options and incomplete work without internal planning notes.
Read as a future student, the five guides identify source/data locations, phase
boundaries, exact working directories, safe checks, saved outputs, known blockers
and the next task. The review is a handoff check, not independent scientific peer review.

**Ready for academic review and continuation using the complete local bundle.**
It is not an end-to-end runnable modelling release or a complete Git-only data
package. Those limits are explicit at the entry point. All cleanup changes are
committed incrementally on the dedicated local branch. `master` and the starting
`report-rebuild-codex-v3` ref are unchanged. Nothing was pushed, merged, rebased or tagged.

The requested master comparison includes the prior report work as well as this
cleanup. For cleanup alone, subsequently run
`git diff 7e69d7a...cleanup/delivery-prep --stat`.

**Branch:** `cleanup/delivery-prep`

**Full backup:** `/Users/parastoo/All_projects/Proj_corrosion/corrosion_pre_cleanup_backup_20260916_092925.tar.gz`

**Run first, from the repository root:**

```bash
git diff master...cleanup/delivery-prep --stat
```
