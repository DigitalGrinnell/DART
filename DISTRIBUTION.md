# DART Distribution Guide

This guide is for DART maintainers preparing installer packages for users.
For recipient installation steps, see [INSTALLATION.md](INSTALLATION.md).

## Preparing a Release

The current release is **DART 7.3**. Start from a fresh clone of the release
commit so local settings, logs, generated files, and collection-specific
operations are not included. The package builders also bundle
`common_dg_utilities` from the sibling `../common-DG-utilities/` checkout;
confirm that checkout exists before building.

From the DART repository root, build both packages using the same explicit
version:

```bash
bash scripts/build_dmg.sh 7.3
bash scripts/build_windows_zip.sh 7.3
```

The scripts set `VERSION` to the supplied version and create
`DART_v7.3.dmg` and `DART_v7.3_Windows.zip` in the repository root. Supplying
the version explicitly avoids the scripts' automatic patch-version increment.
The DMG must be built on macOS.

The package builders omit collection-specific operations, session notes,
editor settings, backup source files, logs, and PDFs. They include the shared
utilities dependency; do not distribute a package if the build reports that
the sibling `common-DG-utilities` checkout is missing.

## Testing and Sharing Packages

Before sharing:

1. Confirm `VERSION` and the matching release entry in [CHANGELOG.md](CHANGELOG.md).
2. Inspect both packages and install-test them on their target platforms. In
   particular, test the ZIP on Windows.
3. Share the approved packages from OneDrive as described below. A versioned
   GitHub Release is an alternative if appropriate for the audience.

## Sharing the Release from OneDrive

For colleague access, use the mcfatem Grinnell College OneDrive. Keep each
release in its own folder so later versions do not replace files colleagues
may still need:

```text
OneDrive/
└── DART-Releases/
    └── 7.3/
        ├── DART_v7.3.dmg
        ├── DART_v7.3_Windows.zip
        └── INSTALLATION.md
```

In Finder, open the synced OneDrive for the mcfatem account and create
`DART-Releases/7.3`. Copy—not move—the two built packages from the DART
repository root into that folder. Also copy the current
[`INSTALLATION.md`](INSTALLATION.md) so colleagues can read setup instructions
before downloading an installer. Do not share the full DART repository or a
collection-specific working folder.

Wait for OneDrive to finish syncing, then open OneDrive on the web and confirm
that all three files appear in `DART-Releases/7.3`. From OneDrive, share the
version folder with the intended colleagues or an approved institutional
group. Use **Can view** access with downloads allowed; avoid **Anyone** links
unless institutional policy explicitly permits them.

Copy the OneDrive sharing link and send it with the version number and the
appropriate installer name for each platform. Test the link with another
authorized account and confirm that the files can be downloaded but not edited.

The DMG is not code-signed or notarized. Tell Mac users to obtain it only from
the trusted release location and follow the Gatekeeper guidance in
[INSTALLATION.md](INSTALLATION.md#macos-installation-dmg).
