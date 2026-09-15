# Senior-reviewer critique of v1

Review date: 2026-09-16. This is a self-review, not independent peer review.
Reviewed the compiling 44-page thesis and 5-page IEEE article, their extracted
text, every page in rendered contact sheets, and the data behind the headline
comparisons. Thesis page numbers below are printed Arabic numbers unless marked
as physical PDF pages. Article page numbers are physical PDF pages.

## Verdict and central contribution

The strongest contribution is a defensible empirical boundary on terminal
structural inference, grounded in a complete metadata/image comparison and a
confounded design. The paper is stronger as a case study of evaluation and
supervision than as a claim of methodological novelty. It does not need a new
model to be useful. Its principal risk is that 'no reliable increment' sounds
stronger than a non-nested comparison on 48 specimens warrants. The qualifications
are present, but a reader should see the actual paired error pattern as well.

The v1 thesis is substantively complete. It is not yet a first-class reading
experience: long captions flood the lists, several chapter endings spill onto
nearly empty pages, and the article strands a short bibliography fragment on its
fifth page. These are avoidable editorial defects, despite error-free compilation.

## Rubric scores

Scores: 0 absent, 1 weak, 2 adequate, 3 strong, 4 exemplary.

| Rubric | Thesis | Article | Assessment |
|---|---:|---:|---|
| R1 Contribution | 3 | 3 | Consistent scope; article should present the terminal-image limitation earlier in the abstract. |
| R2 Provenance | 3 | 3 | Saved metrics verified; a few descriptive claims (model selection, feature counts, legacy split n) need finer source notes. |
| R3 Units and n | 3 | 3 | Main experiment clear; classical holdout lacks explicit test count in Table 5.1 and sensitivity fold sizes could be more explicit. |
| R4 Evaluation | 3 | 3 | Good distinction between reselected and fixed models; paired fixed-family evidence would make the ablation clearer. |
| R5 Uncertainty | 3 | 3 | SD and non-nested selection disclosed; mean-only near-tie remains insufficiently visualized. |
| R6 Observed/inferred | 4 | 4 | Both terminal endpoints and derived threshold statuses clearly distinguished. |
| R7 Visuals | 2 | 2 | Figures useful, but overlong lists, sparse page endings, and article flow weaken delivery. |
| R8 Related work | 3 | 3 | Verified focused context; the empirical gap should be summarized explicitly instead of left for inference. |
| R9 Limitations | 3 | 3 | Full coverage; need a concrete warning that failure-surface cover availability is not established for early deployment. |
| R10 Writing | 3 | 3 | Logical, restrained, some repeated caveats and long chapter headings. |
| R11 Reproduction | 3 | 3 | Audit/build scripts work; final commands and line-level numerical inventory need consolidation. |
| R12 Calibration | 4 | 4 | No true-RUL, classifier, exclusivity, or causal overclaim found. |

## Required revisions and planned response

### C1. Strengthen the incremental-value comparison (major)

Location: thesis §6.2, pp.15–16, Table 6.2 / Fig.6.1; article §IV-B, pp.2–3.
The pooled near-tie between metadata-only and metadata+HSV is stated precisely,
but fold means do not show whether improvement is shared across specimens or
concentrated in a few. The two selected configurations both use Ridge, providing
a useful saved-data comparison with model family fixed.

**Change:** pair their saved terminal fold predictions by specimen and split,
average absolute errors over the two held-out evaluations of each specimen,
and plot the 48 differences. Report the specimen-weighted mean difference,
median, and better/worse counts, explicitly distinguishing this aggregation from
the reported unweighted fold mean. This is descriptive reanalysis after selection,
not a new test of statistical significance and not a training run.

### C2. Make prediction time prominent (major)

Location: thesis abstract (physical p.2), §4.1 p.8; article abstract p.1 and
§III-B p.2. The limitation is in the methods, but the abstract should say directly
that the primary score uses terminal images. Otherwise 'terminal-load prediction'
can still be read as early prediction of the later load.

**Change:** add explicit terminal-image scoring to both abstracts and add a compact
information-availability table in the thesis. In the methods/limitations, name
failure-surface cover as an input whose availability before the destructive test
is not established by the saved feature definition. Do not assert that it was
necessarily unavailable: the record does not establish the measurement timing
for a future deployment.

### C3. Report the small-subgroup evaluation scale (moderate)

Location: thesis §4.4 p.10 and §6.4 pp.17–18; article §III-C p.2. The total n is
stated, but readers should see how few specimens generate an individual subgroup
R². Add actual terminal test-size ranges from saved fold files, not guesses.

**Change:** document four/five test specimens in within-mesh folds if confirmed,
and eight/nine for the post-onset subset if confirmed. Confirm the classical
holdout count from the original split definition and the saved legacy specimen
IDs; label that n as reconstructed, because a standalone classical holdout
prediction manifest was not found.

### C4. Turn negative R² into an inspectable result (moderate)

Location: thesis §6.4 and Table A.3; article §IV-D p.3. The full subgroup table
exists only in the thesis appendix. A compact article table with metadata and the
lowest-MAE family in each subset will prevent the negative finding from reading
as an unsupported generalization. Include the selected family/model and n, and
retain the explanation that R² is not a deployable baseline comparison.

**Change:** add that compact article table, with all seven-family data preserved
in the companion thesis. Do not report a fresh significance test.

### C5. Improve thesis navigation and page economy (moderate)

Location: physical pp.6–10: full captions overwhelm lists and leave almost empty
pages. Printed pp.7, 21, 26, 29, and 33 have short chapter-end spills. Table A.1's
last source-map row is stranded on the next page.

**Change:** give every figure/table a short list entry, explicitly separate front
matter lists, use compact chapter headings, and reduce unnecessary float height.
Keep standalone long captions with the actual figures. Reduce the source-map
font only slightly or reposition the table so it does not strand one row.

### C6. Improve IEEE flow and last-page balance (moderate)

Location: article Fig.1 appears on p.4 after its principal discussion; p.5 has only
a short reference fragment. The plot is central to the design argument.

**Change:** place the design figure near the dataset description, add the paired
error figure and compact sensitivity table, and balance the final two columns.
Use normal IEEE layout, without shrinking text or margins to force a page limit.

### C7. State the literature gap directly (minor)

Location: thesis §2.4 p.4; article end of §II p.1. The review supports the study,
but the distinction between visual corrosion detection and incremental capacity
estimation should be stated in one direct sentence.

**Change:** identify the present question as the target-specific, metadata-controlled
capacity comparison. Avoid a claim that no prior paper has examined it; the search
was focused, not systematic.

### C8. Clarify reproduction records and final numeric pass (moderate)

Location: thesis Appendix A pp.30–33; article reproduction note p.4. The existing
hashes and script outputs are strong, but the report package needs a single
entry-point README, explicit environment commands, and an inventory of numerical
sentences including captions. Minor claims (curve counts, residual baseline,
input dimensions, augmentation count) should be verified as directly as the main
load metrics.

**Change:** add a final document-verification script, line-level numeric inventory,
manual grammar/guardrail sign-off, compile logs, and a morning summary. Retain
source mtimes as supporting chronology only. Check the frozen report hashes again.

## Figure/table necessity review

- Thesis Fig.3.1: necessary supervision schematic; acquisition arrows are explained.
- Fig.4.1: useful instructional schematic; emphasize tile counts are illustrative.
- Fig.5.1: necessary label-adjacency evidence; residual scale readable in vector PDF.
- Fig.5.2: useful regime synthesis; fixed-model selection caption is long but necessary.
- Fig.6.1: useful joint MAE/ranking view; not independent evidence from Table 6.2.
- Fig.6.2 / article Fig.1: central confounding illustration; retain without causal fit line.
- Fig.7.1: useful status taxonomy, although it repeats Table 7.1; retain for thesis
  readability and omit from the focused article.
- Thesis Table 5.1: useful qualitative cross-representation comparison; never rank
  as a shared protocol. Add explicit test n where recoverable.
- Tables 6.1, 6.2: essential; correctly distinguish final structural selection and
  focused capacity ablation. Preserve both model names and units.
- Tables A.2/A.3: necessary full sensitivity detail; keep out of the main narrative.
- Classification split table: sufficient status evidence; no invented accuracy table.

## Requests that cannot be resolved by rewriting

- Independent replication/new crossed campaigns: deferred; requires new physical data.
- Nested model-selection estimate: deferred; would require retraining and a separately
  specified analysis, beyond the authorized saved-output reporting scope.
- Validated structural trajectories/RUL: not obtainable from this dataset.
- Complete historical execution environment: unavailable; not reconstructed by guessing.
- Exact causal decomposition of metadata dominance: not identifiable from this design.

All eight editorial/analysis changes C1–C8 will be implemented in v2. The five
items above remain explicit limitations, rather than being silently dropped.
