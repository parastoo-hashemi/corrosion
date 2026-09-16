# Selected research results

A curated collection of useful figures and papers kept together for discussion,
teaching and research handoff. This is the former `emiling/` folder.
**All 30 research files are preserved unchanged as real files: 28 PNG figures and
two PDF papers.** No selected result was deleted or replaced with a shortcut.

## Reading order

1. [Condition assessment](condition_assessment/README.md): dataset coverage,
   surface prediction, terminal damage and exploratory degradation (16 files).
2. [Structural capacity](structural_capacity/README.md): feature comparisons,
   evaluation splits and metadata-only Ridge diagnostics (14 files).
3. [Experiment map](../docs/experiments.md): the broader scientific conclusions,
   campaign-transfer results and the later classification-preparation phase.

Each phase index explains every selected file and links to an exact matching
copy in the source experiment or export directory. In particular, the condition
plots mix target units in some historical panels, while the proxy-RUL plots
show threshold-based estimates rather than validated lifetimes. Read their notes
before reusing them in a presentation.

## Which report should a new reader use?

The current handoff reports are the [v3 five-page article](../report_v2/article/v3/article.pdf)
and [v3 40-page thesis](../report_v2/thesis/v3/thesis.pdf). The two papers kept in
this collection are historical exports and remain useful for understanding the
work's development. They are different documents/builds, not replacements for
the current reports.

## Preservation and future updates

- Keep this selection together when sharing the repository. The intentional
  copies make it convenient to browse; duplicate content alone is not a reason
  to remove a selected file.
- [manifest.json](manifest.json) records original/current paths, SHA-256 checksums
  and all verified exact matching source copies for the 30 research files.
  Paths in that manifest are relative to the repository root.
- The [preservation record](../report_cleanup/selected_results/README.md) documents
  the verified external backup and the folder mapping. The original Finder
  metadata file was also retained, separately from the 30 research files.
- For future results, add a new clearly named file or dated subfolder and extend
  the index with the source experiment, evaluation split, units and limitations.
  Keep these historical snapshots intact.
- The indexes and renamed paths are local working-tree changes. They have not
  been staged or committed. Keep the external backup with the handoff until an
  approved repository version and a separate backup are available.

To locate an old citation from the repository root:

```bash
python research_paths.py "emiling/main_3/corrosion_model_mae.png"
```

See the [folder migration guide](../docs/folder_migration.md) for all mappings.
