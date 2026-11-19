# DART Installation Guide

This document provides detailed installation instructions for DART (Digital Asset Routing and Transformation) on macOS, Windows, and Linux systems.

This guide is for people installing DART. Maintainers preparing release packages
should use the [DART Distribution Guide](DISTRIBUTION.md).

---

## Table of Contents

- [macOS Installation (DMG)](#macos-installation-dmg)
- [Windows Installation (ZIP)](#windows-installation-zip)
- [Linux Installation (Source)](#linux-installation-source)
- [Prerequisites](#prerequisites)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## macOS Installation (DMG)

DART 7.3 for macOS is distributed as `DART_v7.3.dmg`. The installer puts the
application in `~/DART/` and does not require administrator permissions.

### Prerequisites

- **macOS 12** (Monterey) or later
- **Python 3.8+** must be installed
  - Download from: [python.org/downloads](https://python.org/downloads)
  - Or install via Homebrew: `brew install python`
  - Verify: `python3 --version`

### Installation Steps

1. **Download the DMG**
   - Download `DART_v7.3.dmg` from the DART release location provided by your
     administrator.

2. **Open the DMG**
   - Double-click the downloaded DMG file
   - A Finder window opens with `Install DART.command` and a README.

3. **Run the Installer**
   - Control-click `Install DART.command`, choose **Open**, and confirm that
     you want to open it.
   - The distributed DMG is not code-signed or notarized, so macOS may block it
     the first time. Only bypass Gatekeeper if you obtained the DMG from a
     trusted DART release location and verified the version. If macOS offers
     **Open Anyway**, it is in **System Settings > Privacy & Security**.
   - This approval may be needed once for each downloaded release.

4. **Follow the Installation**
   - A Terminal window opens with the installer
   - The installer checks for Python 3
   - Installs DART to `~/DART/`
   - If that folder already exists, the installer asks before replacing it.
     Confirming replaces the application folder; close DART first and keep any
     personal files elsewhere.
   - Recreates a Desktop launcher if the Desktop folder exists
   - Press Enter to close the installer

5. **Eject the DMG**
   - Right-click the mounted DART volume → Eject
   - Or drag it to the Trash

Updating DART replaces `~/DART/`, but does not remove `~/DART-data/` or your
project working folders. Do not delete `~/DART-data/` during an update; it
contains user-level settings and the encryption key.

### Installation Location

DART is installed to: `~/DART/` (your home directory)

```
~/DART/
├── Launch DART.command   # Double-click to start DART
├── run.sh                # Root compatibility launcher
├── app.py                # Main application
├── scripts/              # Launcher and helper scripts
│   └── run.sh            # Launcher script
├── common_dg_utilities/  # Utility functions (included)
├── INSTALLATION.md       # This file
├── README.md            # Full documentation
└── ... (other files)
```

### Desktop Shortcut

The installer creates: **Launch DART** on your Desktop

- Double-click this to launch DART at any time
- It's a symbolic link to `~/DART/Launch DART.command`

### First Launch

1. **Start DART**
   - Double-click: `Launch DART` (on Desktop)
   - Or navigate to `~/DART/` and double-click: `Launch DART.command`

2. **Automatic Setup (first time only)**
   - A Terminal window opens
   - Python virtual environment is created in `~/DART/.venv/`
   - Dependencies are downloaded and installed automatically (allow a few minutes and an internet connection)
   - Progress and any errors appear in Terminal

3. **DART Window Opens**
   - The DART application window appears when ready
   - Keep the Terminal window open while using DART

4. **Subsequent Launches**
   - Just double-click the launcher
   - The launcher checks and installs required dependencies before starting DART

### Why No Applications Folder?

**Traditional approach issues:**
- Many work computers restrict Applications folder access
- Requires admin permissions to install
- Users encounter permission errors

**DART's solution:**
- Installs to `~/DART/` in your home directory
- No admin permissions required
- Works on all systems, including managed/restricted computers
- Clean, predictable location

---

## Windows Installation (ZIP)

DART for Windows is distributed as a ZIP archive.

### Prerequisites

- **Windows 10** or **Windows 11**
- **Python 3.8+** must be installed
  - Download from: [python.org/downloads](https://python.org/downloads)
  - **During installation: Check "Add Python to PATH"** ✅
  - Verify: Open Command Prompt, type `python --version`

### Installation Steps

1. **Download the ZIP**
   - Download `DART_v7.3_Windows.zip` from the DART release location provided
     by your administrator.

2. **Extract the Archive**
   - Right-click the ZIP file → Extract All...
   - Choose a convenient location, such as a folder under your user profile

3. **Installation Location**
   - The extracted folder contains all DART files
   - No further installation needed

### First Launch

1. Open the extracted `DART_v7.3` folder, then open its `scripts` folder.
2. Double-click `run.bat`.

3. **Automatic Setup (first time only)**
   - A Command Prompt window opens
   - Python virtual environment is created in `.venv\`
   - Dependencies install automatically (allow a few minutes and an internet connection)
   - Progress is shown in the console

4. **DART Window Opens**
   - The DART application window appears when ready
   - Keep the Command Prompt window open while using DART

5. **Subsequent Launches**
   - Launch DART using `scripts\run.bat` again

### Creating a Desktop Shortcut (Optional)

1. Right-click `scripts\run.bat` → Show more options → Send to → Desktop (create shortcut)
2. Rename the shortcut to "DART"
3. Double-click the Desktop shortcut to launch DART

---

## Linux Installation (Source)

For headless Linux operation on `dg-landing`, use the separate
[Headless Linux Installation Guide](INSTALL-LINUX.md). It covers explicit
private storage, source-mount approval, dependencies, and deployment
boundaries. Then follow the [Operating Overview](LINUX-HEADLESS-OVERVIEW.md) and
[Acceptance Testing](LINUX-ACCEPTANCE.md). The source/desktop instructions
below remain available for native use.

DART runs from source on Linux systems.

### Prerequisites

- **Python 3.8+**
  - Most Linux distributions include Python 3
  - Verify: `python3 --version`
  - Install if needed:
    - Debian/Ubuntu: `sudo apt install python3 python3-venv`
    - Fedora/RHEL: `sudo dnf install python3`
    - Arch: `sudo pacman -S python`

### Installation Steps

1. **Download or Clone**
   ```bash
   # Clone from repository:
   git clone https://github.com/Digital-Grinnell/DART.git
   cd DART
   ```

2. **Install common-DG-utilities (required dependency)**
   ```bash
   cd ..
   git clone https://github.com/Digital-Grinnell/common-DG-utilities.git
   cd DART
   ```

3. **Run DART**
   ```bash
   ./run.sh
   ```

4. **First Launch**
   - The script creates a Python virtual environment in `.venv/`
   - Installs all dependencies automatically
   - Launches the DART application
   - Subsequent runs skip the setup phase

**Note for developers:** The `python_requirements.txt` file includes `-e ../common-DG-utilities` which references the sibling repository. This line is automatically removed by the build scripts when creating DMG/ZIP distributions since those packages bundle the utilities directly.

### Creating a Desktop Launcher (Optional)

Create `~/.local/share/applications/dart.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=DART
Comment=Digital Asset Routing and Transformation
Exec=/path/to/DART/scripts/run.sh
Icon=utilities-terminal
Terminal=false
Categories=Utility;
```

Update `/path/to/DART/` with your actual path.

---

## Prerequisites

### Python 3.8 or Later

DART's desktop launchers require Python 3.8 or later. The separate headless
Linux workflow has its own Python 3.11+ requirement; see
[Headless Linux Installation](INSTALL-LINUX.md). To verify your Python version:

```bash
# macOS/Linux
python3 --version

# Windows
python --version
```

**Installation:**

- **macOS:**
  - Download: [python.org/downloads](https://python.org/downloads)
  - Or via Homebrew: `brew install python`

- **Windows:**
  - Download: [python.org/downloads](https://python.org/downloads)
  - **Important:** Check "Add Python to PATH" during installation

- **Linux:**
  - Usually pre-installed
  - If needed: `sudo apt install python3` (Debian/Ubuntu)

### Python Dependencies

The following Python packages are installed automatically on first launch:

- **flet 0.25.2** — UI framework
- **flet-desktop 0.25.2** — Desktop-specific features
- **cryptography 41.0.0+** — Encrypted settings storage
- **azure-storage-blob 12.19.0+** — Azure Blob Storage integration
- **Pillow 10.0.0+** — Image processing
- **csvdiff 0.3.0+** — CSV comparison
- **PyMuPDF 1.24.0+** — PDF processing

**You don't need to install these manually** — the `scripts/run.sh` and
`scripts/run.bat` launchers install the packages listed in
`python_requirements.txt`.

---

## Troubleshooting

### macOS Issues

#### "Install DART.command Can't Be Opened"

**Cause:** macOS Gatekeeper is blocking the unsigned, unnotarized installer.

**Solution:**
1. Confirm the DMG came from your trusted DART release location.
2. Control-click `Install DART.command` and choose **Open**.
3. If necessary, use **System Settings > Privacy & Security > Open Anyway**.

#### "Python 3 Not Found" Error

**Cause:** Python not installed or not in PATH

**Solution:**
```bash
# Install Python via Homebrew
brew install python

# Or download from python.org
# Then verify:
python3 --version
```

#### Installer Says "DART Is Already Installed"

**Cause:** Previous DART installation exists

**Solution:**
- Close DART, then type `y` to replace the application in `~/DART/`.
- Type `n` to cancel. You do not need to remove the folder manually.

#### DART Window Doesn't Appear

**Cause:** Terminal window was closed during setup

**Solution:**
1. Open Terminal
2. Navigate: `cd ~/DART`
3. Run manually: `bash run.sh`
4. Watch for error messages

### Windows Issues

#### "Python Is Not Recognized"

**Cause:** Python not installed or not in PATH

**Solution:**
1. Install Python from [python.org](https://python.org/downloads)
2. **During installation: Check "Add Python to PATH"**
3. Restart Command Prompt
4. Verify: `python --version`

#### Dependencies Fail to Install

**Cause:** Network issues or pip outdated

**Solution:**
```cmd
# Upgrade pip
python -m pip install --upgrade pip

# Then re-run DART
scripts\run.bat
```

#### Virtual Environment Errors

**Cause:** Corrupt virtual environment

**Solution:**
```cmd
# Delete the virtual environment
rmdir /s .venv

# Re-run launcher (recreates .venv)
scripts\run.bat
```

### Linux Issues

#### `./run.sh`: Permission Denied

**Cause:** Script not executable

**Solution:**
```bash
chmod +x run.sh scripts/run.sh
./run.sh
```

#### "No Module Named 'tkinter'"

**Cause:** tkinter not installed (required by flet)

**Solution:**
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

### Common Issues (All Platforms)

#### DART Closes Immediately After Launch

**Cause:** Error during startup

**Solution:**
1. Look for error messages in the Terminal/Console window
2. Check log files in `~/DART-data/logfiles/` or `{working_folder}/logfiles/`
3. Common causes:
   - Missing Python dependencies (re-run installer)
   - Corrupted user settings: back up `~/DART-data/` before contacting support; do not delete the encryption key.

#### "common_dg_utilities Not Found" Error

**Cause:** DMG/ZIP was missing the utilities folder

**Solution:**
- This should not happen with a correctly built release package.
- The build scripts automatically bundle common_dg_utilities
- For developers: Ensure `../common-DG-utilities/` exists when building

#### "Not a Valid Editable Requirement" Error

**Cause:** Using source repository with missing sibling common-DG-utilities repo

**Solution (for developers):**
```bash
# Clone the required utilities repository
cd ..
git clone https://github.com/Digital-Grinnell/common-DG-utilities.git
cd DART
```

**Note:** DMG/ZIP installers automatically remove this dependency since utilities are bundled directly.

---

## Uninstallation

### macOS

1. **Delete the application folder:**
   ```bash
   rm -rf ~/DART
   ```

2. **Delete user data only if you intend to remove saved settings and the
   encryption key:**
   ```bash
   rm -rf ~/DART-data
   ```

   Back up any settings you need first. Removing the encryption key can make encrypted values in saved settings unreadable.

3. **Remove Desktop shortcut:**
   - Drag `Launch DART` from Desktop to Trash

### Windows

1. **Delete the DART folder:**
   - Navigate to where you extracted DART
   - Delete the entire folder

2. **Delete user data (optional):**
   - Navigate to: `C:\Users\YourName\DART-data\`
   - Delete the folder

3. **Remove Desktop shortcut (if created):**
   - Delete the DART shortcut from Desktop

### Linux

```bash
# Delete DART folder
rm -rf ~/path/to/DART

# Delete user data (optional)
rm -rf ~/DART-data

# Remove desktop launcher (if created)
rm ~/.local/share/applications/dart.desktop
```

---

## Support

### Documentation

- **README.md** — Full application documentation
- **QUICKSTART.md** — Quick reference guide
- **Function Help** — Built-in help for each function (Help Mode toggle in app)

### Getting Help

- **Repository:** [https://github.com/Digital-Grinnell/DART](https://github.com/Digital-Grinnell/DART)
- **Issues:** Report bugs on GitHub Issues
- **Questions:** Use GitHub Discussions

### Log Files

DART maintains detailed log files for troubleshooting:

- **Startup logs:** `~/DART-data/logfiles/`
- **Operational logs:** `{working_folder}/logfiles/` (set in app)
- **Format:** `dart_YYYYMMDD_HHMMSS.log`

Include relevant log excerpts when reporting issues.

---

## System Requirements

### Minimum

- **OS:** macOS 12+, Windows 10+, or modern Linux
- **Python:** 3.8 or later (desktop); 3.11 or later for headless Linux
- **Memory:** 2 GB RAM
- **Disk:** 500 MB free space
- **Display:** 1280x720 or higher

### Recommended

- **OS:** macOS 13+, Windows 11, or latest LTS Linux
- **Python:** 3.10 or later
- **Memory:** 4 GB RAM
- **Disk:** 1 GB free space
- **Display:** 1920x1080 or higher

---

## Security Note

DART stores sensitive settings (like Azure connection strings) using encrypted storage:

- **Encryption key:** `~/DART-data/encryption_key`
- **Settings file:** `~/DART-data/persistent.json` (sensitive fields encrypted)
- **Working settings:**
  `{working_folder}/.DART-working-directory/dart_settings.json` (per-project)

**Keep your encryption key secure.** If lost, you'll need to re-enter encrypted settings.

---

*Last updated: November 19, 2026*

*DART Version: 7.3*
*Documentation: [https://github.com/Digital-Grinnell/DART](https://github.com/Digital-Grinnell/DART)*
