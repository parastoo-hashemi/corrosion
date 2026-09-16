# Front-Matter Scientific Summaries — Plan (Abstract + Executive Summary)

Internal planning document. Not part of the final report. Drawn entirely
from frozen Chapters 1–8 and 10, and provisional Chapter 9; no new
repository research performed, per instruction. Every claim below already
appears in the main report body — this plan only decides which of those
claims are compact enough for the Abstract, which belong in the fuller
Executive Summary, and what qualification must travel with each.

Classification key: **context**, **method**, **result**, **limitation**,
**next step**.

## Claim inventory

| Claim | Class | Source | Qualification that must remain attached |
|---|---|---|---|
| Corrosion assessment in reinforced cementitious elements; repeated photography as inexpensive non-destructive observation | context | Ch.1 §1.1 | None (general framing) |
| Predecessor experimental work (thesis + conference paper), external to present activity | context | Ch.1 §1.1 | Present activity builds on, does not reproduce, the predecessor |
| 48 ferrocement specimens, two campaigns, repeated photographic observations | context | Ch.1 §1.2, Ch.2 §1.1 | None |
| 791 aligned/readable observations (of 792 raw files) in current audited basis | context | Ch.1 §1.2, Ch.2 §1.5 | Current audited basis specifically; historical phases used different policies |
| Terminal structural measurements (wire-area loss, ultimate load) once per specimen; no longitudinal structural observation | context | Ch.1 §1.1 (corrected wording), Ch.2 §1.4 | Do not say "hidden structural condition is measured once" — say structural supervision is available only through terminal measurements |
| Dense visible-corrosion supervision vs. sparse terminal structural supervision — central asymmetry | context/method | Ch.1 §1.2, Ch.2 §1.7 | None |
| Activities: dataset audit, classical/deep/interpretable image modelling, structural feasibility, grouped/LOTO/LOCO robustness, terminal-load refocus/ablation, degradation/proxy-RUL, four-class data prep, reproducibility audit | method | Ch.1 §1.4, Ch.4 (all sections) | Do not list every individual model family |
| Visible surface corrosion is the strongest, most consistently learnable image-based task | result | Ch.5 §4.2, Ch.6 §6.2, Ch.10 §9.1 RQ1 | Total-rust/label-adjacency risk; campaign robustness supported across phases, treatment-level behaviour phase-dependent (corrected RQ1 wording) |
| Hidden structural inference substantially weaker and less transferable | result | Ch.5 §4.3, Ch.6 §6.3, Ch.10 §9.1 RQ2 | Must be interpreted in light of sparse/terminal/campaign-confounded supervision, not asserted as sole cause; does not establish absence of physical relationship |
| Pooled terminal-load analysis: no reliable incremental image value over metadata | result | Ch.5 §4.4, Ch.6 §6.4, Ch.10 §9.1 RQ3 | Post-onset analysis showed limited improvement in some metrics but did not overturn pooled result; scoped to this target |
| Evaluation regime materially changes what can be claimed; LOCO is an extrapolative stress test (campaign entangled with mesh/chloride/duration) | result/method | Ch.3 §2.3.3, Ch.5 §4.5, Ch.10 §9.1 RQ4 | Treatment-level visible-corrosion fragility is phase-specific, not project-wide |
| Degradation/proxy-RUL work is methodological/diagnostic, not validated prognosis; zero *future* crossings in refined configuration | result | Ch.5 §4.6, Ch.6 §6.7, Ch.10 §9.1 RQ5 | Not zero crossings overall; structural trajectories model-derived; no true RUL supervision anywhere |
| Only 48 structural endpoints, two campaigns, design/campaign confounding, no repeated structural ground truth, no true lifetime outcome | limitation | Ch.1 §1.4, Ch.8 §7.1–7.5 | Already-established scope boundaries, not new claims |
| Four-class classification branch: data preparation complete, leakage-safe, augmentation built; **no classifier trained** | context/limitation | Ch.4 §3.8, Ch.6 §6.8, Ch.8 §7.6, Ch.9 §8.1 | Must state untrained status explicitly wherever mentioned |
| Report body (Chapters 1–8, 10) complete; Chapter 9 status table provisional pending one row's refresh | context | Ch.9 §8.1 (provisional) | State as current status, not as a claim about content |
| Next modelling step: baseline four-class classifier, class-sensitive metrics, specimen-disjoint untouched test set | next step | Ch.9 §8.2, Ch.10 §9.3 | "Prepared, not yet trained," not implied as already scheduled with a date |
| Stronger structural/RUL claims require new data (additional campaigns, decoupled design factors, repeated structural measurements, lifetime/event data), not just better models | next step | Ch.9 §8.3, Ch.10 §9.3 | Framed as a requirement the limitations point to, not scheduled work |
| Reproducibility: traceable evidence chain built; two live configuration/source issues identified, partially addressed | method/limitation | Ch.7 (all), Ch.8 §7.7 | Not "reproducible" alone — "progressively more reproducible and source-traceable" (per Ch.10 §10.4 corrected wording) |

## Guardrails carried into both documents (verbatim boundaries, already frozen)

- No true RUL claim; "proxy-RUL" always qualified.
- No causal corrosion→capacity statement; confounding-based wording only.
- No claim of deployment readiness or external validation.
- No claim that longitudinal/intermediate structural state was measured —
  it is model-derived, and only terminal wire-area loss and ultimate load
  are directly observed, once per specimen.
- No four-class classifier result stated or implied.
- "Zero future crossings," never "zero crossings" unqualified.
- Visible-corrosion vs. structural evidence-hierarchy distinction must
  remain the organizing spine of both documents.

## Abstract vs. Executive Summary — division of content

**Abstract (~250–300 words):** context → dataset/supervision structure →
method (one sentence) → main findings (compressed to the five bullets
given in the brief, in prose) → principal limitation/interpretive
boundary → concluding contribution. No procedural detail, no repository
names, minimal numbers (48 specimens, 791 observations, "once per
specimen" only). Four-class branch mentioned only if one closing phrase is
useful — decided at drafting time; current assessment: worth one brief
closing clause since it is a genuine, current part of project scope, not
worth more than that since it has no result.

**Executive Summary (~1.5–2 pages):** all five sections A–E as specified,
short paragraphs, one compact bullet list permitted for the four-item
findings hierarchy in part C. Includes current status and next steps,
which the Abstract does not. No repository-cleanup minutiae beyond one
short reproducibility sentence in part D or E.

No sentence is to be copied verbatim between the two documents; both must
independently satisfy the same scientific boundaries.

## Front-matter mechanics

New files: `activity_report/frontmatter/abstract.tex`,
`activity_report/frontmatter/executive_summary.tex`, loaded via
`\input` from `activity_report.tex` in the order Title page → Abstract →
Executive Summary → Table of Contents, using unnumbered headings
(`\chapter*`/`\section*` with `\addcontentsline` only if the report's
existing convention already adds unnumbered material to the TOC —
checked: no prior unnumbered front-matter exists yet in this report, so a
consistent choice must be made now and applied to both). Decision: add
both to the TOC via `\addcontentsline{toc}{chapter}{...}` for
discoverability, consistent with how a reader would expect to navigate a
long technical report — this is a one-time convention decision, applied
identically to both new sections. Title-page metadata (author, supervisor,
programme) is explicitly out of scope for this pass — the placeholder
title-page text stays untouched, per instruction, since no verified
institutional metadata has been supplied.

---

## QC correction pass (post-approval, targeted review)

Four items corrected after substantive approval of both documents:

1. **Executive Summary label-adjacency claim overstated.** "A benchmark
   can look accurate while substantially restating the rule used to
   construct its own label" reintroduced wording already removed from
   Chapter 5 (the repository does not establish that the Phase-1
   rust-mask feature uses the same rule that produced the manually
   assigned label). Corrected to separate the two findings implicitly by
   naming only the one that is directly quantified: "some strong
   visible-corrosion benchmarks rely on image-derived features that are
   very closely aligned with the target, creating shortcut or
   label-adjacency risk; the strongest case is the near-reconstructive
   total-rust pairing identified by the later feature audit."
2. **"The one structural quantity directly measured" — a genuine
   exclusivity error, found in four reader-facing locations, not just the
   Executive Summary.** The dataset has *two* directly measured terminal
   structural endpoints (wire-area loss and ultimate load); ultimate load
   is the one *selected* for the refocused analysis, not the only one
   measured. Corrected in: `frontmatter/executive_summary.tex` (finding
   3); `chapters/01_introduction.tex` (Contribution D); `chapters/10_conclusions_and_next_steps.tex`
   (§10.2); and, on inspection, two further instances in the previously
   frozen `chapters/04_research_and_development_activities.tex` (the
   Phase 4b section introduction and the Phase 4a-to-4b transition
   sentence) that had carried this same error since Batch B and had not
   been caught by any earlier QC pass. All corrected to "one of the two
   directly measured terminal structural endpoints... selected for this
   analysis" or equivalent. A full-report grep for exclusivity variants
   ("the one structural...", "only directly measured...", "the only
   structural...", "single structural quantity...") after the fix
   confirms none remain.
3. **Abstract structural-inference sentence softened.** "Consistent with
   its sparse... supervision rather than an established deficiency of the
   images themselves" implied an isolated causal contrast the experiments
   do not establish. Corrected to "must be interpreted in light of its
   sparse, terminal, campaign-confounded supervision," dropping the
   "rather than" contrast entirely, consistent with the equivalent
   Chapter 10 §9.1 RQ2 correction made in an earlier pass.
4. **No new repository verification was required** for any of these four
   corrections — all are wording-precision fixes against already-frozen
   Chapter 4/5 facts (the two structural endpoints have been established
   since Chapter 2 §1.1).

This pass required touching two frozen chapters (Chapter 1 and, most
notably, Chapter 4) beyond the front-matter documents themselves, since
the exclusivity error pre-dated this session's front-matter work and was
only surfaced by this targeted full-report grep. This is treated as a
legitimate factual correction to an otherwise-frozen chapter, per explicit
instruction, not a reopening of Chapter 4's substantive content.
