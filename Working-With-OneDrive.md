# Working with OneDrive and DART

This guide describes a safe, turn-based workflow for using DART with digital
assets and a shared core metadata CSV stored in a SharePoint document library
that is synced with OneDrive.

## Important: OneDrive Is Shared Storage, Not a DART Lock

OneDrive syncs files between computers, but it does not coordinate DART
sessions or prevent two people from editing the same file at once. Use DART
serially: one person processes a batch and finishes syncing before the next
person starts or merges into the core CSV.

Do not let both users run Function 1, save settings, or merge into the core
CSV at the same time. Wait for OneDrive to finish syncing after each handoff.
If OneDrive reports a sync conflict, stop and resolve it before continuing;
do not assume that the newest-looking copy contains all changes.

## Sync the SharePoint Folder to Your Mac

1. Open the Music Department SharePoint site and navigate to the
   `Shared Documents/CONCERT RECORDINGS` folder.
2. Use **Add shortcut to OneDrive** for that folder or **Sync** for the
   document library, depending on which option is available and permitted.
   Use one method for a given folder; do not add a shortcut and sync the same
   content separately.
3. Approve opening Microsoft OneDrive if prompted, then wait for the folder to
   appear in Finder under the Grinnell College OneDrive location.
4. Make the recordings available offline on this Mac before processing.
   In Finder, use the OneDrive item’s context menu to choose **Always Keep on
   This Device**, then wait for the download/sync status to show completion.
5. Confirm the local folder path in Finder. DART needs this local path; a
   SharePoint webpage or sharing URL cannot be used as an Inputs Folder.

Each collaborator must have access to the SharePoint folder and sync it to
their own computer. Their local paths may differ.

## Confirm Edit Access

Before relying on this location for shared DART outputs, confirm that you can
create files in `CONCERT RECORDINGS`. If its contents are marked **Read-only**
or SharePoint does not offer a **New** action, ask the site or library owner
for **Edit** permission. A OneDrive shortcut can be added even when you only
have read access; that does not make the folder writable.

After creating a test or project folder locally, confirm that it appears in
the SharePoint browser view before treating it as shared. If it does not
appear, check OneDrive's sync status and resolve any permission or sync errors
before using DART.

## Create the Shared DART Project Folder

Choose a folder where both collaborators have **Edit** access. The Music
Department `CONCERT RECORDINGS` library was marked **Read-only** in the
current setup, so it is suitable as an Inputs Folder only if recordings are
available locally; do not use it for DART outputs unless the owner grants
write access.

For the current concert-archives setup, use the `Student-Collaboration` folder
in the Grinnell College OneDrive account. Share the `DART-working-folder`
inside it with the student and grant **Can edit** access before treating it
as a shared workspace. In this setup, the parent `Student-Collaboration`
folder is not shared. Its contents are:

```text
OneDrive-GrinnellCollege/
└── Student-Collaboration/
    └── DART-working-folder/
        └── concert-archives_metadata.csv
```

Select `DART-working-folder` as DART’s **Working/Outputs Folder**. DART will
create its own `.DART-working-directory` subfolder there for settings, ID
mappings, exports, and other generated files. Do not create or edit that
hidden subfolder manually.

The shared core CSV can be kept beside the hidden DART working subfolder, as
shown above. Configure DART’s **Core Metadata CSV** setting to point to
`concert-archives_metadata.csv`.

The recordings remain under the synced `CONCERT RECORDINGS` shortcut and can
be selected as DART’s **Inputs Folder**. The DART output folder and inputs do
not have to be in the same OneDrive folder.

## Copy and Configure the Core CSV

Use the supplied file
`../SHOW/collections/concert-archives/_data/concert-archives_metadata.csv` as
the source. It has been copied into
`Student-Collaboration/DART-working-folder/concert-archives_metadata.csv`;
the source file remains unchanged.

The supplied file currently contains the CSV headers only and no data rows.
That is suitable as a starting schema/template, but it is not a populated
catalog. Confirm that this is the intended starting core before adding
collection records. Verify that OneDrive shows the folder and CSV in the
OneDrive web view and that the student can edit them before using them as the
shared project.

After selecting `DART-working-folder` in DART:

1. Open **App Settings**.
2. Set **Collection ID** to `concert-archives`.
3. Set **Core Metadata CSV** to the local synced path for
   `DART-working-folder/concert-archives_metadata.csv`.
4. Review the other collection settings, then save.
5. Repeat on each computer. DART stores the Core Metadata CSV as a local path
   in the shared project settings, and another computer may use a different
   local path. Before each person’s work session, verify that this setting
   points to a file that exists on their computer. Take turns saving settings
   and let those changes sync before handing off.

The `concert-archives` Collection ID is a recommendation based on the source
collection name. Keep it unchanged after assigning durable object IDs.

## Divide and Process Batches

1. Assign each person separate recording folders or a clearly defined,
   non-overlapping list of files.
2. Configure **Inputs Folder** to the local synced path for that person’s
   assigned recording folder or folders.
3. Confirm the Working/Outputs Folder and Core Metadata CSV settings before
   running DART.
4. Run Functions 1–3 for the assigned batch and review the generated export.
5. Wait for OneDrive to finish syncing the DART working files and settings.
6. Hand off to the next person. Merge exports into the shared core CSV one at
   a time using Function 4.
7. After a successful merge, wait for the core CSV to finish syncing before
   the next merge or processing handoff.

Avoid processing the same source files from different local paths. DART saves
file-to-ID mappings in the working folder, and those mappings are based on
file paths. A different path may cause DART to assign a different ID rather
than reuse the existing one.

## Before Every Handoff

- DART is closed or idle on the previous user’s computer.
- OneDrive reports that the project folder and core CSV are fully synced.
- There are no OneDrive conflict copies or unresolved sync errors.
- The next user has the same shared DART-working-folder synced locally.
- The next user verifies their local Core Metadata CSV path in App Settings.
- The next user works only on their assigned, not-yet-processed assets.

For general DART setting behavior, see [App Settings](./APP_SETTINGS.md).
For identifier persistence, see [Function 1: Analyze Assets](./FUNCTION_1_ANALYZE_ASSETS.md).
For the review and merge procedure, see [Function 4: Compare and Merge CSV Files](./FUNCTION_4_COMPARE_MERGE_CSV.md).
