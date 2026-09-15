# Chapters 7–9 — Evidence / Scope Plan

Internal planning document. Not part of the final report. Written before
drafting. Chapters 2–6 are frozen; this plan draws on their already-
established facts plus fresh, targeted repository verification this
session (all items below marked with exact source paths; **NEW** marks
facts not previously logged anywhere in this report).

Organised into three categories per instruction: **A** (Chapter 7,
reproducibility/engineering), **B** (Chapter 8, limitations), **C**
(Chapter 9, status/remaining work). For every item: exact source, current
status, why it belongs where it does, essential/optional/omit, and
historical-vs-current-live.

---

## A. Reproducibility / engineering facts for Chapter 7

| Item | Source | Status | Essential? | Historical or live? |
|---|---|---|---|---|
| Five sub-projects (`main`, `main_2`, `main_3`, `main_4`, `augmentation`) each in a separate directory with growing internal structure (`src/`, `configs/`, `outputs/`) | Directory listing, all five roots | Verified | Essential (frames §7.1) | N/A (structural fact) |
| Config-driven pipeline in `main_4`: six YAML configs (`dataset.yaml`, `features.yaml`, `modeling.yaml`, `thresholds.yaml`, `specimen_mapping.yaml`, `ultimate_load_refocus.yaml`) loaded through one `load_configs()` function | `main_4/src/corrosion_proxy_rul/config.py` (`load_yaml_config`, `load_configs`, `yaml.safe_load`) | Verified **NEW** (read directly this session) | Essential (§7.1/§7.5) | Live |
| `main_3` uses a single `default.toml` for RUL/degradation thresholds, a lighter-weight but still centralised config approach | `main_3/configs/default.toml` (already cited in Ch.4 §4.5) | Verified (carried over) | Optional (one sentence, contrast with main_4) | Historical |
| `main`/`main_2` are more script-parameterised than config-driven (thresholds and paths appear as constants/arguments in the training scripts themselves) | `main/train_models.py`, `main_2/data.py` (already established in prior audit) | Verified (carried over) | Optional (one sentence, contrast) | Historical |
| Deterministic, hash-derived augmentation RNG: `stable_rng(seed, image_name, augmentation_index)` derives a per-image-per-copy seed from a SHA-based digest of `f"{seed}|{image_name}|{augmentation_index}"`; default seed `20260630`; the seed actually used is written into the augmentation methodology report itself | `augmentation/augment_dataset.py` lines 91, 388–392, 780 | Verified **NEW** (read directly this session) | Essential (§7.3/§7.7 — concrete, verifiable determinism) | Live, current |
| Validation/test split membership is fixed via hardcoded, disjointness-checked specimen-ID lists, not randomly sampled; `make_splits.py` raises `RuntimeError` if the lists overlap, if any augmented row leaks into val/test, or if a specimen appears in more than one split | `augmentation/make_splits.py` (already logged for the leakage check; disjointness check re-confirmed this session, lines ~246, 260, 357, 360) | Verified | Essential (§7.3) | Live, current |
| Explicit `random_state: 42` in two `main_4` configs | `main_4/configs/modeling.yaml:1`, `main_4/configs/ultimate_load_refocus.yaml:1` | Verified **NEW** | Essential (§7.3, one line) | Live |
| `requirements.txt` present for `main`, `main_2`, `main_3`, `augmentation`; **absent** for `main_4`, whose README instead says "use the existing conda environment" with no exported environment file | Directory listing of all five roots; `main_4/README.md` | Verified **NEW** | Essential (§7.5/§9.4 — a concrete, fixable gap) | Live |
| Report-level figure-generation scripts (`activity_report/figures/generated_scripts/*.py`) read directly from saved project CSVs rather than hardcoding values, and are themselves versioned alongside the report | This session's own `make_fig_4_*`, `make_fig_5_1_*` scripts, already logged in evidence_log.md | Verified (self-referential; already established) | Essential (§7.7 — this report's own reproducibility discipline) | Live, current |
| `evidence_log.md` and the per-chapter evidence-plan files constitute a running, source-cited audit trail for every reported number | This document's own working files | Verified (self-referential) | Essential (§7.7, one paragraph) | Live, current |
| Provenance chain from raw workbook/images through to report figures is traceable but not uniformly automated end-to-end: `main_4` has the most complete `outputs/data → outputs/models → outputs/diagnostics` structure; earlier phases (`main`, `main_2`) save flatter `reports/` directories | Directory structure comparison across `main*/outputs` and `main*/reports` | Verified (structural, already partly established in Ch.4) | Essential (§7.2) | Both (contrast is the point) |
| `main_4/configs/specimen_mapping.yaml` is the single canonical source for campaign/treatment/mesh/NaCl/terminal-week facts, already used as the preferred reconstruction source over raw workbook columns (Chapter 2 footnote) | Chapter 2 §1.1 footnote (already frozen) | Already established | Essential (§7.2, cited briefly) | Live, current |

## A (continued). Configuration/schema issues — Section 7.5

| Item | Source | Status | Essential? | Historical or live? |
|---|---|---|---|---|
| **(A) PyYAML `NO`→`False` boolean-parsing bug.** `main_4/configs/specimen_mapping.yaml` contains unquoted `treatment_coarse: NO` for every no-treatment-control specimen; PyYAML's default (YAML 1.1) resolver reads bare `NO` as the boolean `False`. Directly re-verified this session: `main_4/outputs/data/master_table.csv`'s `treatment_coarse` column shows the literal string `"False"` for exactly 168 rows, while the parallel `treatment_raw` column correctly shows `"NO"` for the same rows, and `treatment_protocol` (`no_treatment_control`) is unaffected. | `main_4/configs/specimen_mapping.yaml` line 46 (and all `treatment_coarse: NO` entries); `main_4/outputs/data/master_table.csv`; re-verified via `yaml.safe_load` behaviour and direct `pandas.value_counts()` this session | Confirmed live and reproducible from current source | Essential | **Live** — reproducible today by reloading the YAML |
| **(B) Numeral/word "1"/"first" → "main_first" corruption — broader than previously logged.** Re-verified and **substantially extended** this session. Previously logged instances (two `.py` files, category-range strings) are one small part of a much wider pattern. Newly confirmed this session: it also replaces the pandas aggregation-function name `"first"` with `"main_first"` in named-aggregation and `pivot_table` calls (confirmed this breaks execution: `df.groupby(...).agg(y=('x','main_first'))` raises `AttributeError: 'SeriesGroupBy' object has no attribute 'main_first'`); it also replaces the bare numeral `1` in YAML hyperparameter values (`n_jobs: -main_first`, `reg_lambda: main_first.0`, `alpha: main_first.0`, `curve_grid_step_days: main_first`, `glcm_distances: [main_first, 3]`, `strip_width_cm: main_first.0`, `train_size_fractions: [...,\ main_first.0]`); it also appears in comments, docstrings, a package `__version__` string (`"0.main_first.0"`, cosmetic only — import still succeeds), plotted-label strings (`"Low (<main_first%)"`), and generated report prose (`"Phase main_first"`, `"Table main_first"`, `"Figure main_first"`). Confirmed present in **`main`, `main_2`, `main_3`, and `main_4`** (9 files in `main_4` alone: `data_loading.py`, `eda.py`, `ultimate_load_refocus.py`, `models_hidden_damage.py`, `__init__.py`, `features.yaml`, `modeling.yaml`, `ultimate_load_refocus.yaml`, `specimen_mapping.yaml`); confirmed **absent** from `augmentation/` (the newest sub-project). | Direct `grep -rl "main_first"` across the repository this session; direct Python reproduction of the `AttributeError`; direct reading of each affected line | Live in current source; **breaks specific runtime calls** if re-executed (pandas aggregation calls; several YAML-sourced hyperparameters would fail type validation or silently pass an invalid string) but does **not** prevent package import | Essential — this is the single most consequential reproducibility finding for Chapter 7/9 | **Live** |
| Timestamp evidence for (B), stated as an observation only. Most affected files share the **identical** modification timestamp `2026-04-01 16:58:13` across `main_3` and `main_4` (`specimen_mapping.yaml`, `ultimate_load_refocus.py`, `models_hidden_damage.py`, `data_loading.py`, `eda.py`, `__init__.py`, `features.yaml`, `modeling.yaml`, `ultimate_load_refocus.yaml`, `main_2/visualize.py`, `main_2/build_pdf_report.py`, `main_3/src/rul/estimator.py`, `main/data_utils.py`); two files in `main/` (`train_models.py`, `api.py`) instead share a different, later timestamp, `2026-04-08 14:10:24`. All already-generated output artifacts cited elsewhere in this report (e.g. `master_table.csv`, 2026-03-16; `specimen_summary_table.csv`, 2026-03-25; `diagnostics.py`, 2026-03-19) **predate** both corruption timestamps. | `stat` timestamps, checked directly this session across ~15 files | Verified fact (timestamp clustering); **mechanism and cause are not established and are not claimed** | Essential, stated carefully | N/A (a dated fact, not a live/historical distinction) |
| **(C) Category-schema evolution (4-class vs. 5-class) is a separate, legitimate change, not a corruption instance.** Already fully established and frozen (Chapter 2 §1.5, Table 1.6): a genuine workbook-column range change between dataset snapshots, verified at the byte level in a prior session, unrelated to (A) or (B) above. | Chapter 2 §1.5 (frozen) | Already established | Essential to state explicitly as a *contrast*, not to re-derive | Historical (a genuine version difference, not a bug) |

## A (continued). Model/artifact contract status — Section 7.6

Re-verified each `NEXT_STEPS_PLAN.md` "Code Changes Needed" item against
the current repository this session, rather than assuming all remain
open:

| Recommendation (from `main_4/NEXT_STEPS_PLAN.md`) | Current status, re-verified this session |
|---|---|
| "Save the exact feature list used by each trained model" | **Partially done.** `main_4/outputs/models/hidden_damage/hidden_damage_selected_feature_list.csv` exists (one global list for that stage), but per-model `best_model.json` files contain only `{"target", "best_model_name"}` — no feature list or hyperparameters — and no equivalent file exists for the surface stage. |
| "Export fully explicit out-of-fold predictions for the structural target models ... as the basis for any degradation modelling experiment" | **Not done.** Already established (Chapter 5/6 QC passes): `ultimate_load_refocus.py` produces genuine out-of-fold ("terminal_oof") predictions, but only for the terminal-load evaluation task, not for the degradation-modelling stage, which still consumes in-sample hidden-damage refits. |
| "Add an automatic feature-QC report" (constant/duplicate/collinear/zero-inflated columns) | **Done.** `main_4/FEATURE_DIAGNOSTICS.md` is generated by `main_4/src/corrosion_proxy_rul/diagnostics.py` (confirmed by `grep` this session, not hand-written) and covers exactly the recommended checks (near-constant, duplicate, high-collinearity, missingness/variance). |
| "Separate 'analysis tables' from 'model-ready X matrices'" | **Not done.** `main_4/outputs/models/surface/surface_feature_table.csv` (and the equivalent hidden-damage table) still mix features, targets, and identifiers in one artifact, confirmed by listing the file this session. |
| "Add raw-versus-smoothed degradation artifacts" | **Done.** `main_4/outputs/models/degradation/degradation_raw_vs_monotone_proxy.csv` contains both `raw_predicted_wire_area_loss_frac` and `monotone_proxy_wire_area_loss_frac` columns together, confirmed by reading the file this session — contrary to an initial assumption that this remained outstanding. |

This mixed picture (two items done, one partially done, two still open) is
more accurate and more useful than treating the whole `NEXT_STEPS_PLAN.md`
list as uniformly unaddressed, and is the basis for §7.6's "which of these
remain valid" framing and §9.4's prioritised cleanup list.

---

## B. Scientific and technical limitations for Chapter 8

Organised by category per instruction, cross-referencing already-frozen
material rather than re-deriving it. No new repository verification was
needed for most of these; they synthesise Chapters 2–6.

| Category | Items (concise, not re-deriving counts) | Source |
|---|---|---|
| 8.1 Dataset/design | 48 specimens, 2 campaigns, campaign⟷mesh/chloride/duration entanglement, sparse single-timepoint structural supervision, no repeated internal structural measurement, no observed failure-event time, image modality is external surface only, uneven treatment-group sizes | Chapter 2 §1.1/§1.4/§1.6/§1.7 (frozen) |
| 8.2 Label/target | Visible-corrosion labels are manually assigned (not machine-derived ground truth); two independent label-adjacent/near-reconstructive findings (Phase-1 peak-rust shortcut, main_4 total-rust near-identity); historical 5-class vs. current 4-class schema (a version difference, stated as such, not an error); proxy-RUL thresholds are exploratory engineering choices, not physically validated constants; no ground-truth RUL anywhere in the dataset | Chapter 2 §1.5/Table 1.6; Chapter 5 §4.2.2; Chapter 3 §2.8 |
| 8.3 Generalisation | Grouped holdout answers interpolation, not transfer; LOCO is a severe extrapolation stress test given campaign/design entanglement, not an ordinary generalisation estimate; treatment-level (LOTO) visible-corrosion behaviour is phase-specific (fragile in one implementation, robust in another) rather than a settled project-wide property; within-mesh subgroups are small (24 specimens each) | Chapter 3 §2.3.3; Chapter 5 §4.2.3/§4.5 (QC-corrected) |
| 8.4 Structural modelling | Only 48 structural labels underlie every structural claim in the report; main_3's structural models are mixed-input (metadata + manual labels + image features), not image-only; main_4's final robustness-weighted selections are metadata-only; degradation-stage structural estimates remain in-sample refits, not out-of-fold; no validated intermediate/longitudinal structural state exists at all — every non-terminal "structural" value in the dataset is model-derived | Chapter 4 §3.4.2/§3.6; Chapter 6 §6.3 (physical-relationship-vs-identifiability distinction restated, not re-derived) |
| 8.5 Prognostic/proxy-RUL | No true-RUL supervision anywhere in the dataset; thresholds (wire-loss %, load ratio, health-index, or the refined single-series thresholds) are screening assumptions, not derived from an independent physical failure criterion; many baseline-crossed cases exist at first observation; the refined configuration's own output shows zero future crossings; no out-of-fold structural trajectory feeds the degradation model; no validation exists against an observed future failure or a repeated structural measurement | Chapter 3 §2.8; Chapter 5 §4.6 (QC-corrected: "zero future crossings," not "zero crossings"); Chapter 6 §6.7 |
| 8.6 Classification branch | Severe class imbalance (approx. 83/12/2/2%, Chapter 2 Table 1.2); no classifier trained, compared, or evaluated at the time of writing; uniform augmentation does not itself rebalance the classes (documented explicitly by the project); performance on held-out or external data is entirely unknown pending training | Chapter 4 §3.8; Chapter 6 §6.8 |
| 8.7 Software/reproducibility | Cross-referenced to Chapter 7 rather than repeated: the live `main_first` corruption pattern and the YAML `NO`→`False` bug both currently prevent an unmodified clean rerun of some `main_4` pipeline stages; `main_4` lacks an exported dependency/environment file; historical pipeline generations (`main`, `main_2`) are not guaranteed to rerun against the currently stored data workbook without repair (already noted, Chapter 4 §3.2) | Chapter 7 §7.5/§7.6 (this pass); Chapter 4 §3.2 (frozen, already-noted schema-mismatch caveat) |

## C. Completed / pending / recommended work for Chapter 9

| Workstream | Status | Evidence/output | Category |
|---|---|---|---|
| Dataset audit/alignment | Complete | Chapter 2, `main_4/outputs/audit/verified_facts.json` | Completed |
| Visible-corrosion regression | Complete across 3 phases; robustness re-quantified | Chapter 4 §3.2–3.4, §3.6 | Completed |
| Structural-condition feasibility | Complete (feasibility established, not validated for transfer) | Chapter 4 §3.4.2, §3.6 | Completed (as a feasibility study) |
| Robustness diagnostics | Complete for both target families under 3 regimes, 2 independent phases | Chapter 4 §3.6; Chapter 5 §4.5 | Completed |
| Terminal ultimate-load refocus | Complete | Chapter 4 §3.7 | Completed |
| Degradation/proxy-RUL screening | Complete (two generations); explicitly not a validated prognostic method | Chapter 4 §3.5/§3.6; Chapter 5 §4.6 | Completed (as a methodological/diagnostic exercise) |
| Four-class classification | Data preparation, splitting, augmentation, leakage controls complete; **no classifier trained** | Chapter 4 §3.8 | **Prepared, not started** |
| Software/reproducibility cleanup | Partially addressed (feature-QC automated, raw/smoothed trajectories saved); YAML boolean bug and `main_first` corruption still live; `main_4` has no environment file; per-model feature-list/OOF/table-separation recommendations partially open | This session's verification, table above | **Mixed — some completed, several open** |
| Final report/documentation | Chapters 1 (Introduction), 10 (Conclusions), Executive Summary, Abstract, Appendices not yet written; Chapters 2–6 frozen; Chapters 7–9 in progress (this pass) | `activity_report.tex` include list | In progress |

**Immediate next actionable step (§9.2):** train a baseline classifier for
the four-class branch — this is the only workstream that is fully prepared
but has produced literally zero model-performance evidence, making it the
highest-value next action. Concrete practice already specified in Chapter 3
§2.7 (macro-F1/per-class recall, not accuracy alone) and the leakage-safe
split already built (Chapter 4 §3.8) should be used as-is, not re-designed.

**Data requirements for stronger structural/RUL claims (§9.3), framed as
requirements suggested by current limitations, not scheduled work:**
additional independent campaigns; design factors (mesh/chloride/duration)
decoupled across campaigns rather than perfectly aligned; more
structural-labelled specimens; repeated or intermediate structural
measurements per specimen; an observed failure or service-life event time
if RUL is ever to be a stated objective. All four are direct, traceable
consequences of the sparse-supervision and design-confounding limitations
already established in Chapters 2, 5, and 6 — not new claims.

---

## Planned chapter structures (adopting suggested structure; no changes needed)

**Chapter 7** (~3–4 pages): 7.1 Repository and Pipeline Evolution; 7.2 Data
and Artifact Provenance; 7.3 Split and Evaluation Reproducibility; 7.4
Image and Feature Reproducibility; 7.5 Configuration and Schema Issues
(A: YAML boolean bug; B: numeral/word corruption; C: schema evolution is
not a bug); 7.6 Model and Artifact Contract Limitations; 7.7
Reproducibility Improvements Already Achieved.

**Chapter 8** (~3–4 pages): 8.1–8.7 as specified, one short paragraph or a
compact list per category, cross-referencing rather than re-deriving.

**Chapter 9** (~2–3 pages): 9.1 Current Project Status (one compact table:
workstream / status / evidence / next action); 9.2 Immediate Next Work; 9.3
Structural/Prognostic Work Required for Stronger Claims; 9.4 Reproducibility
Cleanup; 9.5 Recommended Validation Before External Claims.

**Figures/tables budget for all three chapters combined:** one status
table in Chapter 9 (§9.1) is the clear highest-value visual; a second,
optional compact table in Chapter 7 or 8 only if prose becomes repetitive
(current assessment: not needed — prose is sufficiently concise). No
figure is planned; the engineering content does not need a schematic
beyond what Chapter 6's evidence-hierarchy figure and Chapter 2's dataset
schematic already provide, and duplicating either would violate the
"do not duplicate result figures" instruction.

**Total target:** 8–10 pages across the three chapters, ceiling ~11.

---

## QC correction pass (post-approval, targeted review)

Eight items corrected after substantive approval of Chapters 7–9; see
`evidence_log.md`'s matching QC section for exact re-verified facts. In
summary: (1) §7.1 now distinguishes `main_first` (exploratory prototype)
from the four structured modelling generations (`main`, `main_2`,
`main_3`, `main_4`) and the later `augmentation` branch, and explicitly
excludes `out/` (dissemination layer) and `main_4_old` (archival) from the
generation count; (2) the corruption-timestamp claim in §7.5/§8.7 is
narrowed to "the saved scientific-output artifacts... predate," re-verified
against more than two dozen specific files, with `specimen_mapping.yaml`
named as an explicit exception (later timestamp, but its cited fields are
unaffected); (3) the proxy-RUL status-table entry now distinguishes further
methodological refinement (possible with existing data) from validated
prognostic claims (which require new data); (4) §9.2 now frames baseline-
classifier training as the top priority "among the research/modelling
workstreams," not the literal next action in the whole project, since
completing this report remains the immediate task; (5) "running
independent feature ablations" was removed from §9.3's engineering list
after confirming `NEXT_STEPS_PLAN.md` contains no such recommendation
(a `grep` for "ablation" returns nothing) and that the terminal-load phase
already ran the relevant ablation for its own target; (6) §9.5 now states
OOF-structural-input regeneration and independent threshold justification
as two separate requirements, with an explicit sentence that OOF inputs do
not themselves validate threshold values.

**INTERNAL TODO, carried into the chapter source as a LaTeX comment above
the "Final report/documentation" row of Table~9.1:** that row is
provisional and must be refreshed during the final, whole-report QA pass
once Chapter 1, Chapter 10, the executive summary, abstract, and
appendices are complete. Chapters 2–8 are frozen as of this pass; Chapter
9 is frozen except for that one row.
