# DART Feature and Release Summary

This document summarizes the major capabilities and milestones recorded
through DART 7.3. It is a concise overview, not a replacement for the
[complete changelog](./CHANGELOG.md). The release groupings below reflect
versions documented there.

## Current Capabilities

- **Desktop asset workflow:** Analyze source files, assign durable object IDs,
  group related files as compound objects, export CollectionBuilder-compatible
  CSV metadata, generate derivatives, and review and merge metadata updates.
- **Collection-aware identifiers:** New IDs use the required `collection-id`
  setting in `<collection-id>_dg_<epoch>` form. Existing mappings and IDs are
  preserved.
- **Metadata and merge safety:** The configured core CSV remains the source of
  truth. Working exports are isolated in `.DART-working-directory`; compare
  and merge tools support review before changes are applied.
- **Storage and derivatives:** Optional Azure Blob Storage uploads, encrypted
  sensitive settings, image and PDF derivatives, and protections against
  unnecessary repeat uploads.
- **GEMS, Alma, and OHM workflows:** Recursive and folder-scoped compound
  processing, GEMS metadata backfill, and OHM transcript handling support
  specialized collection workflows.
- **Privacy and preservation:** Private files are excluded from public exports
  and Azure uploads. Oversized audio and video are recorded in archive-only
  manifests; the optional `restrict_media` setting records audio and video of
  any size for preservation without Azure uploads.

## Release Milestones

- **1.0–1.2:** Established the Flet desktop application, settings and logging,
  standard `dg_<epoch>` identifiers, persistent file-to-ID mappings, and
  compound-object grouping.
- **1.3–1.5:** Added CollectionBuilder CSV export, Azure uploads, image and PDF
  derivatives, and Function 4 compare-and-merge review. Later 1.x releases
  improved compound-family review, CSV comparison, logging, and safe repeat
  processing.
- **2.2.1, 2.2.3–2.3.2:** Introduced versioned builds, isolated working files,
  core-CSV-preserving merges, workflow progress indicators, and optional
  identifier prefixes. Seeklight metadata conversion and merge functions were
  also introduced in 2.3; they were removed in 6.7.
- **4.4:** Changed compound analysis to one parent per folder, with numbered
  sequences represented as nested `multiple` objects.
- **6.0–6.1:** Made `collection-id` required, protected the reserved
  `collection-template.csv`, added Azure overwrite and OHM-data options, and
  expanded recursive, flat-compound processing for GEMS and Alma migrations.
- **6.5–6.7:** Improved folder-scoped grouping and macOS file filtering, added
  GEMS metadata backfill and completed-batch handling, and removed Seeklight.
- **7.0–7.3:** Introduced a managed headless Linux workflow in 7.0; the
  headless CLI, job submission, and desktop handoff controls were disabled in
  7.1, while the underlying code and settings were retained. Releases 7.1–7.3
  added private file handling, archive-only recording for oversized media,
  status-based manifests, and restricted audio/video recording without Azure
  uploads.

## Version Coverage

The changelog currently records releases in the 1.x, 2.2.x, 2.3.x, 4.4, 6.x,
and 7.x series through 7.3. Consult the [changelog](./CHANGELOG.md) for the
individual release entries, patch details, and changes not covered by this
summary.
