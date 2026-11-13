# DART Installation Guide

This document provides detailed installation instructions for DART (Digital Asset Routing and Transformation) on macOS, Windows, and Linux systems.

---

## Table of Contents

- [macOS Installation (DMG)](#macos-installation-dmg)
- [Windows Installation (ZIP)](#windows-installation-zip)
- [Linux Installation (Source)](#linux-installation-source)
- [Prerequisites](#prerequisites)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## macOS/Linux Installation (Source)

DART runs from source on Linux and Mac systems.

### Prerequisites

- **Python 3.8+**
  - Most Linux distributions include Python 3
  - Verify: `python3 --version`
  - Install if needed:
    - Debian/Ubuntu: `sudo apt install python3 python3-venv`
    - Fedora/RHEL: `sudo dnf install python3`
    - Arch: `sudo pacman -S python`
    - macOS: download from [python.org/downloads](https://python.org/downloads) or Homebrew - `brew install python`
- **macOS 12** (Monterey) or later if installing on macOS

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

### Creating a Desktop Launcher (Optional for Linux)

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

### Headless Linux

For headless Linux operation on `dg-landing`, use the separate
[Headless Linux Installation Guide](INSTALL-LINUX.md). It covers explicit
private storage, source-mount approval, dependencies, and deployment
boundaries. Then follow the [Operating Overview](LINUX-HEADLESS-OVERVIEW.md) and
[Acceptance Testing](LINUX-ACCEPTANCE.md). The source/desktop instructions
below remain available for native use.


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
   - Download `DART_v2.x_Windows.zip` from your distribution source

2. **Extract the Archive**
   - Right-click the ZIP file → Extract All...
   - Choose a convenient location (e.g., `C:\Users\YourName\DART\`)
   - Or extract to your Desktop

3. **Installation Location**
   - The extracted folder contains all DART files
   - No further installation needed

### First Launch

1. **Open the DART folder**
   - Navigate to where you extracted the files

2. **Run the launcher**
   - Double-click: `run.bat`

3. **Automatic Setup (first time only)**
   - A Command Prompt window opens
   - Python virtual environment is created in `.venv\`
   - Dependencies install automatically (1-2 minutes)
   - Progress is shown in the console

4. **DART Window Opens**
   - The DART application window appears when ready
   - The Command Prompt window stays open (don't close it!)
   - Minimize the console if you want it out of the way

5. **Subsequent Launches**
   - Just double-click `run.bat`
   - DART starts immediately

### Creating a Desktop Shortcut (Optional)

1. Right-click `run.bat` → Send to → Desktop (create shortcut)
2. Rename the shortcut to "DART"
3. Double-click the Desktop shortcut to launch DART

---

## Prerequisites

### Python 3.8 or Later

DART requires Python 3.8 or later. To verify your Python version:

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
- **cryptography** — Encrypted settings storage
- **azure-storage-blob 12.19.0+** — Azure Blob Storage integration
- **Pillow** — Image processing
- **PyMuPDF (fitz)** — PDF processing
- **pandas** — Data manipulation

**You don't need to install these manually** — the `run.sh` / `scripts/run.sh` / `scripts/run.bat` launchers handle everything.

---

## Troubleshooting

### macOS Issues

#### "Python 3 not found" error

**Cause:** Python not installed or not in PATH

**Solution:**
```bash
# Install Python via Homebrew
brew install python

# Or download from python.org
# Then verify:
python3 --version
```

#### `./run.sh` error

**Cause:** missing dependencies/requirements

**Solution:** ensure `../common-DG-utilities` is installed and exists in the same folder `DART` was cloned/downloaded into.

#### DART window doesn't appear

**Cause:** Terminal window was closed during setup

**Solution:**
1. Open Terminal
2. Navigate: `cd ~/DART`
3. Run manually: `bash run.sh`
4. Watch for error messages

### Windows Issues

#### "python is not recognized"

**Cause:** Python not installed or not in PATH

**Solution:**
1. Install Python from [python.org](https://python.org/downloads)
2. **During installation: Check "Add Python to PATH"**
3. Restart Command Prompt
4. Verify: `python --version`

#### Dependencies fail to install

**Cause:** Network issues or pip outdated

**Solution:**
```cmd
# Upgrade pip
python -m pip install --upgrade pip

# Then re-run DART
scripts\run.bat
```

#### Virtual environment errors

**Cause:** Corrupt virtual environment

**Solution:**
```cmd
# Delete the virtual environment
rmdir /s .venv

# Re-run launcher (recreates .venv)
scripts\run.bat
```

### Linux Issues

#### `./run.sh`: Permission denied

**Cause:** Script not executable

**Solution:**
```bash
chmod +x run.sh scripts/run.sh
./run.sh
```

#### "No module named 'tkinter'"

**Cause:** tkinter not installed (required by flet)

**Solution:**
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

### Common Issues (All Platforms)

#### DART closes immediately after launch

**Cause:** Error during startup

**Solution:**
1. Look for error messages in the Terminal/Console window
2. Check log files in `~/DART-data/logfiles/` or `{working_folder}/logfiles/`
3. Common causes:
   - Missing Python dependencies (re-run installer)
   - Corrupted settings file (delete `~/DART-data/persistent.json`)

#### "common_dg_utilities not found" error

**Cause:** DMG/ZIP was missing the utilities folder

**Solution:**
- Ensure `../common-DG-utilities/` exists when building

#### "not a valid editable requirement" error

**Cause:** Using source repository with missing sibling common-DG-utilities repo

**Solution:**
```bash
# Clone the required utilities repository
cd ..
git clone https://github.com/Digital-Grinnell/common-DG-utilities.git
cd DART
```

---

## Uninstallation

### macOS/Linux

1. **Delete the application folder:**
   ```bash
   rm -rf ~/path/to/DART
   ```

2. **Delete user data (optional):**
   ```bash
   rm -rf ~/path/to/DART-data
   ```

3. **Remove Desktop shortuct (if created)**
   ```bash
   # Linux
   rm ~/.local/share/applications/dart.desktop
   ```

### Windows

1. **Delete the DART folder:**
   - Navigate to where you extracted DART
   - Delete the entire folder

2. **Delete user data (optional):**
   - Navigate to: `C:\Users\YourName\DART-data\`
   - Delete the folder

3. **Remove Desktop shortcut (if created):**
   - Delete the DART shortcut from Desktop

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
- **Python:** 3.8 or later
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
- **Working settings:** `{working_folder}/dart_settings.json` (per-project)

**Keep your encryption key secure.** If lost, you'll need to re-enter encrypted settings.

---

*Last updated: November 13, 2026*  
*DART Version: 7.x*  
*Documentation: [https://github.com/Digital-Grinnell/DART](https://github.com/Digital-Grinnell/DART)*
