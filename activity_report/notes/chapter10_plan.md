# Chapter 10 — Conclusions and Next Steps: Plan

Internal planning document. Not part of the final report. Drawn entirely
from frozen Chapters 1–8 and provisional Chapter 9; no new repository
verification performed or needed, per instruction. No new empirical
result appears in Chapter 10 — every number, if any appears at all, is
already stated in an earlier frozen chapter.

## 10.1 Answers to the research questions

| RQ (Chapter 1 §1.3) | Source chapter(s) | Defensible answer | Qualification that must remain attached |
|---|---|---|---|
| RQ1 — visible-corrosion estimation | Ch.4 §3.1–3.4.1, §3.6; Ch.5 §4.2; Ch.6 §6.2 | Visible surface corrosion is the strongest, most consistently learnable image-based quantity in this dataset, reached by three *distinct* (not "independent") representations | Total-rust/label-adjacency risk in specific benchmarks; campaign-level visible-corrosion robustness is supported across both later phases; treatment-level behaviour is phase-dependent — **not** "campaign robustness is consistently stronger than treatment robustness," which the fixed-model evidence (main_4 LOTO/GH MAE 0.549 total rust, 0.758 peak rust, both with strong R²/Spearman) does not support as a general claim |
| RQ2 — hidden structural condition | Ch.4 §3.4.2, §3.6; Ch.5 §4.3; Ch.6 §6.3 | Structural inference is substantially weaker and less transferable than visible-corrosion estimation | Sparse, terminal-only, campaign-confounded supervision is a major limitation **consistent with** the observed instability — not stated as its established primary cause; main_3 structural models mixed-input; main_4 final robustness-weighted selections metadata-only; LOCO exposes severe transfer limits; does NOT establish absence of a physical corrosion-capacity relationship; explicitly states the available experiments do not isolate the relative contribution of data limitations, image information, and model representation |
| RQ3 — incremental image value for terminal ultimate load | Ch.4 §3.7; Ch.5 §4.4; Ch.6 §6.4 | Under the tested pooled setting, images did not provide reliable incremental predictive value beyond metadata | A post-onset analysis showed a limited improvement in some metrics (not framed as a "demonstrated exception") but did not overturn the pooled result; subgroup and campaign-transfer evidence does not support a robust image-value claim; scoped to this dataset only |
| RQ4 — evaluation robustness | Ch.4 §3.4/§3.6/§3.7; Ch.5 §4.5; Ch.6 §6.5 | Evaluation regime materially changes what can be claimed; grouped holdout is useful but insufficient for transfer claims | LOCO is an extrapolative stress test (campaign entangled with mesh/chloride/duration), not an estimate of ordinary future performance; treatment-level visible-corrosion fragility is phase-specific, not project-wide |
| RQ5 — degradation and proxy-RUL | Ch.4 §3.5/§3.6; Ch.5 §4.6; Ch.6 §6.7 | The work produced a functioning methodological/diagnostic threshold-screening pipeline, not validated remaining-life prediction | Structural trajectories are model-derived, not measured; no true RUL supervision; zero *future* crossings in the refined configuration (not zero crossings overall); degradation inputs are not yet out-of-fold |

## 10.2 Overall scientific conclusion

Central synthesis, drawing on Chapter 6 §6.1's evidence hierarchy by
reference only (not redrawn/repeated): the project's evidence supports a
three-level hierarchy of confidence — visible surface condition
(strongest), hidden structural inference (weaker, sparse/confounded-supervision-dependent),
longitudinal degradation/proxy-RUL (exploratory, model-dependent). The
governing lesson is not a model-vs-model comparison; it is that target
observability, supervision density, target provenance, metadata controls,
and evaluation design jointly determine how strong a claim can legitimately
be made. The terminal-load refocus (Ch.4 §3.7, Ch.6 §6.5) is restated
briefly as a scientifically useful narrowing toward a directly measured
endpoint, not re-derived.

## 10.3 Next steps (three levels only, each explicitly labelled)

- **A. Immediate research/modelling step — PREPARED, NOT TRAINED.** Four-class
  classification branch: establish a simple baseline first, evaluate
  candidate CNN/ViT architectures only if justified, keep validation/test
  specimen-disjoint and untouched appropriately, report class-sensitive
  metrics. Source: Ch.9 §8.2 (compressed to ~3 sentences, not the full
  checklist).
- **B. Methodological refinement with existing data — RECOMMENDED, NOT
  IMPLEMENTED (mixed per Ch.7).** OOF structural predictions before
  degradation fitting; physical-plausibility checks on baseline structural
  estimates; complete feature/artifact contracts; repair the two live
  reproducibility issues (Ch.7 §6.5/§6.6, Ch.9 §8.4). Explicitly: none of
  this validates RUL.
- **C. Data required for stronger scientific claims — FUTURE DATA
  REQUIREMENT, not scheduled work.** Additional independent campaigns;
  decoupled experimental factors; more structural-labelled specimens;
  repeated structural measurements; lifetime/event data if true RUL
  becomes the objective. Final substantive point: model complexity cannot
  substitute for missing supervision. Source: Ch.9 §8.3 (compressed).

## 10.4 Closing statement

One short paragraph, ending on the project's actual strongest contribution
(a rigorously bounded understanding of what the data can and cannot
support, plus a reproducible basis for next steps) — not overstated, not
overly negative.

## Guardrail checklist for drafting (restated for discipline)

proxy-RUL ≠ true RUL; no validated prognosis claim; "zero future
crossings" not "zero crossings"; no causal corrosion→capacity wording;
structural trajectories explicitly model-derived; terminal-load image
increment stated as not robustly established (not "disproven"); metadata
framed as possibly-genuine-signal-and-possibly-shortcut simultaneously;
LOCO framed as extrapolative stress test; treatment-level visible-corrosion
fragility framed as phase-specific; four-class classifier stated as
untrained; no deployment/generalisation claim anywhere in the chapter.

## Numerical content policy

At most "48 specimens" / "791 observations" if needed for one orientation
sentence; no MAE/R²/Spearman/class-count/threshold-count anywhere. Given
Chapter 10 is a synthesis chapter following directly from Chapter 1's
already-stated numbers, even the specimen/observation counts are likely
omittable — decide at drafting time based on whether §10.2 needs them for
self-containedness; current assessment: not needed, since Chapter 1 and
Chapter 2 already carry them and Chapter 10 can cite by reference.

## Planned structure, length, and visual budget

10.1 Answers to the Research Questions (prose, one paragraph per RQ);
10.2 Overall Scientific Conclusion; 10.3 Next Steps (three short,
explicitly-labelled paragraphs, not the full Chapter 9 checklist); 10.4
Closing Statement (one paragraph). Target 2–3 pages, ceiling 4. No new
figure, no table — prose throughout, per instruction.

---

## QC correction pass (post-approval, targeted review)

Six items corrected after substantive approval; the RQ1–RQ3 rows above
have been updated in place to reflect the corrected wording (per
instruction, this plan file now carries the approved formulation as
primary, not the pre-QC draft). In summary:

1. **RQ1 campaign-vs-treatment claim corrected.** "Campaign-level
   robustness is consistently stronger than treatment-level robustness"
   overstated what the fixed-model evidence in Chapter 5 established:
   main_4's LOTO/GH ratios (total rust 0.549, peak rust 0.758, both with
   strong R²/Spearman) show treatment-level robustness holding up in that
   phase, even though main_3 shows the opposite. Corrected to "campaign-level
   visible-corrosion robustness is supported across both later phases,
   whereas treatment-level behaviour is phase-dependent."
2. **RQ2/§10.2 causal-attribution wording softened.** "This follows from
   how the two are supervised" and "that weakness tracks directly to...
   not primarily to any deficiency in the images or the models" both
   asserted a causal decomposition the project's experiments do not
   establish. Corrected to "must be interpreted in light of" framing in
   both places, with an added explicit sentence that the available
   experiments do not isolate the relative contribution of data
   limitations, image information, and model representation.
3. **RQ3 "conditional exception" softened.** Replaced with "a post-onset
   analysis showed a limited improvement in some metrics," removing the
   implication of a demonstrated exception to the pooled conclusion while
   preserving the existing "did not overturn the pooled result" statement.
4. **Closing-statement reproducibility wording corrected.** "A
   reproducible, source-cited basis" overstated current reproducibility
   given Chapter 7's own findings (live YAML/string-corruption issues).
   Corrected to "a progressively more reproducible and source-traceable
   basis."
5. **Two micro-wording fixes.** RQ1: "three independent representations"
   → "three distinct representations" (avoids implying statistical
   independence between representations). §10.3 heading: "recommended,
   not implemented" → "recommended, with key items still incomplete"
   (some artifact/reproducibility infrastructure is already partially
   implemented per Chapter 7 §6.6).
6. **No repository re-verification was required** for any of these six
   corrections — all are wording precision fixes against already-frozen
   Chapter 5/6/7 facts.
