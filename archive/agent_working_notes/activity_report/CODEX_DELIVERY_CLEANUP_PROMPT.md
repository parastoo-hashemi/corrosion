# Autonomous task: prepare the `corrosion` repository for academic handoff

## 0. Operating rules — read this section first

You are running **unattended overnight**. The user will not be available to
answer questions, approve choices, or unblock you.

- **Never stop mid-task to ask a question.** If you would normally ask a
  clarifying question, instead: pick the most conservative option (when in
  doubt, `ARCHIVE` or `UNCERTAIN — DO NOT TOUCH`, never `DELETE`); write down
  what you chose and why in `DELIVERY_CLEANUP_PLAN.md`; and continue. "Never
  stop" means never pause and wait for input — it does **not** mean skip the
  git-permission gate in Section 9. Finishing the entire task and then
  naturally ending, with everything committed on a branch and nothing
  merged or pushed, is the correct and expected outcome, not a failure to
  finish.
- **Work on a dedicated local branch, `cleanup/delivery-prep`, created from
  the current `master`/current branch tip before you touch anything.**
  Commit **incrementally to that branch** after each stage in Section 10,
  with clear messages — this is your checkpoint mechanism so that a crash
  or restart doesn't lose progress and so the user can review the full
  history of what changed, stage by stage, via `git log` and `git diff` in
  the morning. **Do not commit to, merge into, rebase onto, or otherwise
  touch `master` (or whatever the current branch was before you started).
  Do not push anything to any remote. Do not create tags. Do not
  force-push. Do not rewrite history.** Committing to `cleanup/delivery-prep`
  is your normal, expected way of working throughout the night — it is not
  "finalizing" and does not violate the permission gate in Section 9, which
  is specifically about `master`/remote/merge actions.
- **Before any destructive or large-scale change**, create a full backup:
  `tar czf` (or equivalent) the entire pre-cleanup repository state to a
  location **outside** the `corrosion/` directory (e.g. a sibling
  directory, clearly named with a timestamp, e.g.
  `../corrosion_pre_cleanup_backup_YYYYMMDD.tar.gz`). Do this in addition
  to, not instead of, git history — belt and suspenders, since this
  operation touches far more of the repository than any previous task.
- Every other constraint in the user's brief below is binding as written:
  no scientific/functional changes, audit-before-destroy, dependency
  checks before any rename/move/delete, extremely conservative treatment
  of generated scientific artifacts, and the git-permission gate in
  Section 9 (no commit to `master`, no push, no merge, without explicit
  user approval — which, again, is about `master`/remote, not about your
  own incremental commits on `cleanup/delivery-prep`).

## 1. Why this matters and what "done" looks like

This repository grew organically during development of an MSc technical
activity on ferrocement corrosion assessment (48 specimens, two campaigns,
repeated corrosion photography, terminal structural testing). It needs to
go, unchanged in scientific substance, to two audiences: the user's
professor, and a future MSc student who will continue the work without
access to this development history. Right now it contains unclear
historical folder names (`main`, `main_2`, `main_3`, `main_4`, `main_first`,
`main_4_old`, `augmentation`, `emiling`), many agent-generated `.md`
planning/audit/QC files, and real scientific outputs (CSVs, parquet,
figures, trained models, split manifests, PDFs) that must not be lost or
altered. "Done" means: a clean, professional, self-explanatory repository
where the scientific results are provably untouched, on a reviewable
branch the user can inspect and merge themselves.

## 2. Non-negotiable rules

- **Do not change scientific functionality, model behaviour, datasets,
  splits, seeds, hyperparameters, feature definitions, preprocessing, or
  evaluation protocols.**
- **Do not recompute or overwrite existing scientific outputs**, except
  where strictly required to *verify* that cleanup preserved them
  (e.g., re-running a cheap, already-passing check) — never to regenerate
  or "improve" a result.
- **Do not silently alter**: saved predictions, CSV/JSON/parquet metrics,
  figures, trained models, manifests, or any number/claim in the final
  report. If something in old documentation conflicts with the final
  report's verified results, **flag the conflict in the plan/report — do
  not silently edit either to match the other.**
- This is a **structure + naming + documentation + clutter-removal** task,
  not a scientific or code-behaviour change.

## 3. Stage 1 — Inventory (read-only)

Inspect the entire repository: every top-level directory, every file type,
every `.md` file, every config, every script's imports and path
references, every place the final report (`activity_report/` and
`report_v2/`) or a README cites a path. Use `git ls-files`, `git grep`,
`find`, and directory listings. Do not modify anything in this stage.

## 4. Stage 2 — Cleanup plan (write-only, not yet executed)

Create `DELIVERY_CLEANUP_PLAN.md` at the repo root. For every top-level
folder and every important file, classify it as one of:

`KEEP` · `RENAME` · `MOVE` · `ARCHIVE` · `DELETE` ·
`GENERATED OUTPUT — PRESERVE` · `UNCERTAIN — DO NOT TOUCH`

For every proposed `RENAME`/`MOVE`/`DELETE`, state: why; whether code,
configs, the report, or saved manifests reference the current path (and
how you checked — exact `grep` commands and what they returned); whether a
future student would plausibly need it; and how you verified it is safe.
**Do not classify anything `DELETE` unless you are highly confident it is
pure development clutter (cache files, OS metadata, empty directories,
build artifacts) with zero references anywhere in the repo.** Anything
that is agent-generated documentation, historical planning material, or
otherwise not obviously disposable junk should default to `ARCHIVE`
(moved into a clearly separated, clearly labelled location — see Stage 5 —
not deleted), never `DELETE`. If a file's role is genuinely unclear after
checking, mark it `UNCERTAIN — DO NOT TOUCH` and leave it exactly where it
is; do not act on an uncertain classification.

Also include in this plan: a proposed final directory tree, and — for any
historical implementation directory (`main`, `main_2`, `main_3`, `main_4`,
`main_first`) — a decision on renaming per Section 5, backed by an actual
dependency-graph inspection, not an assumption.

## 5. Stage 3 — Dependency check (read-only, before any change)

Before moving, renaming, or deleting anything named in the plan, grep the
entire repository (code, configs, shell scripts, notebooks, the final
report's LaTeX source, `report_v2/`, README/docs) for every reference to
that path. Record the exact search commands and results in the plan.

For the historical `main*` directories specifically: inspect the real
import/config/path dependency graph first. **Do not rename `main`,
`main_2`, `main_3`, `main_4`, or `main_first` if doing so requires
invasive, error-prone path surgery across scripts/configs/saved
manifests.** In that case, prefer: keep the physical directory names
unchanged, and provide a clear mapping in the README and in
`docs/project_history.md` (using evidence from the repository and the
final report, not guesses), e.g.:

```
main_first → exploratory prototype (no held-out evaluation, no saved metrics)
main       → classical corrosion baseline
main_2     → frozen deep-image-embedding experiment
main_3     → interpretable features + structural feasibility + first proxy-RUL pipeline
main_4     → robustness diagnostics + terminal-ultimate-load refocus (most mature generation)
augmentation → four-class classification data prep (separate, later branch; classifier not yet trained)
```

Only rename a directory or file if you have confirmed, by actually
checking every reference found above, that doing so is safe and every
reference can be updated consistently in the same change. Preserving
functionality is more important than cosmetic renaming.

## 6. Stage 4 — Execute only verified-safe changes

Carry out only the `RENAME`/`MOVE`/`ARCHIVE`/`DELETE` actions from the plan
that Stage 3 confirmed safe. As you go, maintain a machine-readable
`report_cleanup/move_manifest.csv` (or similar) with one row per
moved/renamed/deleted path: `old_path,new_path_or_deleted,action,reason` —
this is what lets the next student (or the professor) find something that
moved. Commit after this stage completes (per Section 0's branch/commit
rule) before moving on.

For anything classified `ARCHIVE`: move it into a single, clearly labelled
location such as `docs/development_history/` or `archive/agent_working_notes/`
— not deleted, not scattered — so it remains available but is visibly
separated from the professor-facing material. Update `.gitignore` for true
build/cache clutter (`__pycache__/`, `.DS_Store`, LaTeX build artifacts,
editor metadata, local caches) rather than one-off deleting it, so it
doesn't reaccumulate.

## 7. Stage 5 — `.md` file audit (part of Stages 2/4, called out separately)

Inspect **every** `.md` file in the repository individually — do not judge
by filename alone. Classify each into:

- **A. Essential user-facing documentation** (README, dataset description,
  methodology, reproduction instructions, a still-valid next-steps
  document) — keep and improve.
- **B. Useful technical documentation** — move into a curated `docs/`
  structure.
- **C. Historical/internal development record** (agent planning files,
  intermediate audit notes, QC scratch files, obsolete TODOs, chapter
  evidence plans, duplicated explanations, investigation logs, this
  session's own `CODEX_*_PROMPT.md` files, `DECISIONS.md`,
  `MORNING_SUMMARY*.md`, `report_v2/critique/`, `report_v2/evidence/`,
  `report_v2/qa/`, `activity_report/notes/evidence_log.md` and the
  `*_plan.md` files) — these should **not** remain in the professor-facing
  root/primary view. If their unique information isn't already captured by
  the final report, README, or curated docs, extract that information into
  a curated document first (e.g. into `docs/project_history.md` or
  `docs/known_issues.md`), then `ARCHIVE` the original (per Stage 4 — do
  not delete outright; the test is "would a professor or the next student
  genuinely need this specific file," not "was it made by an agent" — an
  agent having written something is never itself a reason to delete it if
  the content is genuinely useful and not duplicated elsewhere).
- **D. Obsolete or duplicate**, with zero unique information and zero
  references anywhere — only these may be `DELETE`d, and only after Stage
  3's reference check confirms nothing points to them.

## 8. Stage 6 — Documentation

### 8a. Root `README.md`

Rewrite it so a new student understands the project in 5–10 minutes.
Sections: Project Overview; Dataset (48 specimens, repeated imagery,
sparse terminal structural measurements, current audited basis — without
exposing the internal audit history); Project Structure (the *actual*
final tree, one line per important directory, with the historical-phase
mapping from Section 5 for anything not renamed); Research Workflow (a
short phase list: data audit → visible-corrosion modelling → structural
feasibility → robustness analysis → terminal-load refocus →
degradation/proxy-RUL screening → four-class classification prep); Key
Findings (high-level only — this is not the 70-page report); How to Run
(exact current commands; put historical-phase commands in
`docs/experiments.md` instead); Environment/Dependencies (derive honestly
from the code — do not invent package versions you haven't verified);
Outputs (where metrics/predictions/figures/models/manifests/report PDFs
actually live); Reproducibility Notes (concise — only what the next
student actually needs, not the full forensic writeup); Current Status
(explicitly: four-class classifier data prep = complete, training/
evaluation = not yet done); Recommended Next Steps; Final Report location
(both `activity_report/` and, if the user has by then decided which
version of `report_v2/` is authoritative, that one too — if undecided,
say so plainly rather than guessing).

### 8b. Supporting docs

Only create what's genuinely useful, under `docs/`: `project_history.md`
(historical-phase mapping), `experiments.md` (what each completed
experiment did and where its outputs live), `data_dictionary.md` (target/
feature/terminology glossary), `reproduction.md` (exact commands and
execution order), `known_issues.md` (only unresolved issues — e.g. the
live YAML boolean bug and the `main_first` string-corruption pattern,
described accurately from the existing report, not re-investigated). Do
not create documentation for its own sake.

## 9. Stage 7 — Code readability pass (no behaviour change)

Add module-level and important-function docstrings, and comments that
explain **why**, not what, especially around: specimen-level grouping and
leakage controls; the distinction between observed and model-estimated
quantities; unusual preprocessing decisions; and any place the code
implements a scientific guardrail that isn't otherwise obvious. Do not
refactor algorithms, change control flow, or "clean up" logic — the
diff for any touched code file should be comments/docstrings only. Verify
this yourself before finishing each file (e.g. a diff that touches
anything but comment/docstring/blank lines needs to be reverted and
reconsidered).

## 10. Stage 8 — Output preservation and functional verification

**Mandatory, not "where practical":** before Stage 4 begins, generate an
inventory of every file classified `GENERATED OUTPUT — PRESERVE` with its
path, size, and SHA-256 hash. After all cleanup is complete, regenerate
that inventory (accounting for any deliberate, logged moves from the
move-manifest) and confirm every hash still matches. Save both snapshots
and the diff under `report_cleanup/output_preservation_check.md`.

Then: run import/syntax checks on touched Python files; validate that
configs still load; confirm the paths the final report/README/docs cite
still resolve; confirm the README's own commands are accurate (dry-run
them where cheap, e.g. `--help` or a syntax check, not full training). Do
not retrain any model or regenerate any expensive output to test the
cleanup — verify against existing saved outputs.

## 11. Stage 9 — final review, from two perspectives

Read the finished repository once as the professor opening it cold, and
once as a new MSc student picking up the project six months from now.
Confirm both can answer, without any access to this development history:
what the project is; where the data and code are; which experiment is
current vs. historical; where the main results and final report are; how
to reproduce the current workflow; what's unfinished; and which historical
code is not a safe starting point. If anything is still unclear, fix it
now rather than noting it as a gap.

## 12. Git / safety permission gate — binding

**Do not commit to, merge into, rebase onto, tag, or push `master` (or
whatever branch was active before you started). Do not push anything to
any remote.** Your incremental commits to `cleanup/delivery-prep` per
Section 0 are expected and required — that rule is unaffected by this
gate. You may use any read-only git command freely (`status`, `diff`,
`log`, `ls-files`, `grep`). At the end of the run, leave everything
committed on `cleanup/delivery-prep`, do not merge it anywhere, and stop —
this is the correct final state, not an incomplete one.

## 13. Final report

Write `CLEANUP_HANDOFF.md` at the repo root covering, in order: final
repository tree; every rename/move/archive/delete with reasoning
(pointer to `DELIVERY_CLEANUP_PLAN.md` and `move_manifest.csv` for detail);
`.md` files removed vs. retained and why; README structure and what
changed; supporting docs created; which code files got comments/
docstrings (confirm: no behavioural diffs); the output-preservation check
result (hash match confirmation); functional checks run and their
results; any unresolved reproducibility issue the next student needs to
know about; anything you deliberately left untouched because it was too
risky to classify confidently, and why; and an explicit statement of
whether the repository is ready to hand to the professor and next student
as-is. End with: exact branch name, exact backup-tarball path, and the
exact `git diff master...cleanup/delivery-prep --stat` a human should run
first to get an overview before reading anything else.
