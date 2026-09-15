# Chapter 1 — Introduction and Project Scope: Plan

Internal planning document. Not part of the final report. Written before
drafting, per instructions. Chapter 1 is written last, after Chapters 2–9
are stable, precisely so that it introduces the project the report
actually contains. Sourced entirely from frozen Chapters 2–9, the
evidence log, the two predecessor sources already in
`references/references.bib`, and REPORT_PLANNING.md's already-approved
central narrative (§7) for framing language only — no new repository
audit was performed, and no claim below required reopening primary
repository evidence, since every fact traces to an already-frozen chapter.

Each proposed claim is classified as **physical/experimental context**,
**project objective**, **completed activity**, **established finding**, or
**scope boundary**, per instruction.

## 1.1 Background and Motivation

| Claim | Class | Source |
|---|---|---|
| Corrosion assessment in reinforced cementitious elements is a durability concern; repeated photography is a comparatively inexpensive, non-destructive way to observe surface condition over time | Physical/experimental context | Chapter 2 §1.1 (frozen); general framing, not a new literature claim |
| Visible surface corrosion (external, photographable) and hidden structural condition (internal, not directly observable) are distinct quantities requiring distinct evidence | Physical/experimental context | Chapter 2 §1.2/§1.4; Chapter 6 §6.3 (physical-vs-identifiability distinction) |
| Hidden structural condition is scientifically harder to establish because it is measured once, at a single terminal timepoint, for a small fraction of observations | Physical/experimental context | Chapter 2 §1.4 (frozen) |
| The physical fabrication, exposure, and terminal mechanical testing programme was designed and executed as predecessor work (an earlier MSc thesis and a related conference paper), external to the present activity | Physical/experimental context + attribution | Chapter 2 §1.1 footnote (frozen); `references.bib` (`hossain_thesis`, `artiste2025`); REPORT_PLANNING.md §8 item 3 (predecessor author Al Amin Hossain, s313940, confirmed distinct from the present author) |
| The present activity is not an exact reproduction of the predecessor's manual image-analysis workflow | Scope boundary | Chapter 4 §3.4 (frozen: "best described as a Python reconstruction and extension... rather than an exact reproduction") |

## 1.2 Project Context and Data Basis

| Claim | Class | Source |
|---|---|---|
| 48 ferrocement specimens, two experimental campaigns | Physical/experimental context | Chapter 2 §1.1 (frozen) |
| Repeated photographic observations per specimen over its exposure period | Physical/experimental context | Chapter 2 §1.3 (frozen) |
| 791 aligned, readable observations in the current audited basis (out of 792 raw image files) | Established finding (dataset audit) | Chapter 2 §1.5 (frozen) |
| Visible-corrosion labels available throughout the image series (dense supervision) | Physical/experimental context | Chapter 2 §1.2 (frozen) |
| Terminal structural measurements available only once per specimen (sparse supervision) | Physical/experimental context | Chapter 2 §1.4 (frozen) |
| This asymmetry (dense visible-corrosion labels vs. sparse terminal structural labels) is the single most important structural fact about the dataset for interpreting everything that follows | Established finding, stated as framing | Chapter 2 §1.7 (frozen); Chapter 6 §6.1 (evidence hierarchy) |

Explicitly NOT reproduced here: the campaign/treatment design matrix
(Table 1.1), the corrupted-image handling table (Table 1.5), the
category-schema table (Table 1.6) — all cited by reference only.

## 1.3 Project Objectives and Research Questions

Derived from what was actually completed, not aspirational. Five research
questions map directly onto completed chapters:

| RQ | Maps to | Class |
|---|---|---|
| RQ1: visible surface corrosion estimation from classical, deep-embedding, and interpretable representations | Chapter 4 §3.1–3.4.1; Chapter 5 §4.2 | Project objective (realised) |
| RQ2: reliability of hidden structural condition / terminal structural response inference | Chapter 4 §3.4.2, §3.6; Chapter 5 §4.3 | Project objective (realised, with a bounded negative-leaning answer) |
| RQ3: incremental value of image-derived features beyond metadata for terminal ultimate load | Chapter 4 §3.7; Chapter 5 §4.4 | Project objective (realised) |
| RQ4: robustness from grouped holdout to treatment-/campaign-level transfer | Chapter 4 §3.4, §3.6, §3.7; Chapter 5 §4.5 | Project objective (realised) |
| RQ5: what degradation fitting and proxy-RUL screening can legitimately contribute absent repeated structural measurements or true lifetime outcomes | Chapter 4 §3.5, §3.6; Chapter 5 §4.6; Chapter 6 §6.7 | Project objective (realised, with an explicitly bounded/methodological answer) |

The four-class classification direction is deliberately **not** phrased as
a sixth completed RQ, since no classifier has been trained
(Chapter 4 §3.8; Chapter 9 §8.1/§8.2) — it is introduced in §1.4 as a
current, subsequent workstream instead.

## 1.4 Scope of the Technical Activity

Activities to list (completed activities, one line each, no metrics):
data audit/alignment; classical visible-corrosion baseline; frozen
deep-image embeddings; engineered/interpretable image features; structural
feasibility modelling; grouped/LOTO/LOCO robustness evaluation;
degradation and proxy-RUL screening; terminal ultimate-load refocus;
augmentation and split preparation for four-class classification;
reproducibility and software audit. All ten map directly onto Chapters
2, 4, and 6.

Scope boundaries (explicit, per instruction) — each already established as
a frozen conclusion, restated here as a boundary rather than re-derived:

| Boundary | Source |
|---|---|
| No true RUL supervision or validated RUL model exists or is claimed | Chapter 3 §2.8; Chapter 6 §6.7; Chapter 8 §7.5 (frozen) |
| No claim that surface corrosion causally determines structural capacity | Chapter 5 §4.3/§4.4 (QC-corrected); Chapter 6 §6.3/§6.4 |
| No externally validated or deployment-ready model of any kind | Chapter 9 §8.5 (frozen) |
| No four-class classifier has been trained | Chapter 4 §3.8; Chapter 9 §8.1 |
| Model-estimated structural states at intermediate weeks are not measurements | Chapter 2 Table 1.3; Chapter 6 §6.1 |

## 1.5 Main Contributions of the Activity

Seven items (A–G), each already a completed, reported activity — "contribution"
meaning work completed, not a novel publication-level claim, per instruction:

A. Audited and aligned the specimen-level analysis basis (Chapter 2).
B. Established visible-corrosion estimation as the strongest image-based
   task while identifying label-adjacency/tautology risk in specific
   benchmarks (Chapter 4 §3.1–3.4.1, §3.6; Chapter 5 §4.2; Chapter 6 §6.2).
C. Quantified the weaker transferability of hidden structural prediction
   and separated image signal from metadata/campaign structure (Chapter 4
   §3.4.2, §3.6; Chapter 5 §4.3/§4.4; Chapter 6 §6.3/§6.4).
D. Refocused the structural question onto directly measured terminal
   ultimate load and explicitly tested incremental image value (Chapter 4
   §3.7; Chapter 6 §6.5).
E. Built and critically evaluated a degradation/proxy-RUL screening chain
   while establishing why it is not validated prognosis (Chapter 4 §3.5,
   §3.6; Chapter 6 §6.7).
F. Prepared a leakage-safe, reproducible four-class classification dataset
   and augmentation pipeline for subsequent modelling (Chapter 4 §3.8;
   Chapter 6 §6.8).
G. Documented concrete reproducibility/software issues and maintained a
   traceable, source-cited evidence chain throughout (Chapter 7; this
   report's own evidence log).

Each classified as **completed activity**; none overstates beyond what its
cited chapter already established.

## 1.6 Report Organisation

One short paragraph, using `\ref` throughout (Chapters~\ref{ch:dataset},
\ref{ch:framework}, \ref{ch:activities}, \ref{ch:results},
\ref{ch:interpretation}, \ref{ch:engineering}, \ref{ch:limitations},
\ref{ch:status}), no hard-coded numbers.

## Bounded findings preview (per explicit instruction on how much to reveal)

Exactly the four bullet points given in the instructions, no metrics:
visible corrosion most learnable; structural inference weaker and
sparse-supervision/campaign-confounded; no reliable pooled incremental
image value for terminal load under the tested setting; proxy-RUL
exploratory, not validated prognosis. Each already a frozen Chapter 5/6
conclusion, not a new claim.

## Terminology discipline (checklist for drafting)

Use: visible corrosion; surface total rust / peak rust; terminal ultimate
load; hidden structural condition; model-estimated structural state;
proxy-RUL / threshold screening; grouped holdout; LOTO; LOCO. Avoid: "true
structural state" for estimates; unqualified "RUL prediction"; "failure
load" (the experimental source defines the measured quantity as ultimate
load from a four-point bending test, not an observed failure event);
causal corrosion→capacity wording.

## Predecessor-attribution discipline

State: "the present activity builds on / uses the experimental dataset
generated in the preceding experimental work" (predecessor thesis, Al
Amin Hossain, and the related ARTISTE conference paper). Never state "we
reproduce the predecessor method." The present author is distinct from
the predecessor thesis author (REPORT_PLANNING.md §8 item 3, already
resolved).

## Planned structure, length, and visual budget

1.1 Background and Motivation; 1.2 Project Context and Data Basis; 1.3
Project Objectives and Research Questions; 1.4 Scope of the Technical
Activity; 1.5 Main Contributions of the Activity; 1.6 Report Organisation.
Target 3–4 pages, ceiling 5. No new figure (Chapter 2's dataset schematic
and Chapter 6's evidence-hierarchy schematic already exist and must not be
duplicated). No table planned — a prose RQ list is sufficient per
instruction, and the report is not so complex at this stage that an
RQ→section map table would add orientation value beyond the §1.3 prose
already cross-referencing each RQ to its chapter.
