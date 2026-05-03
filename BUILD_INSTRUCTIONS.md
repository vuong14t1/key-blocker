# KEY BLOCKER - Build & Install Guide

## 📋 Requirements

- Windows 10/11
- Python 3.8 or later
- Pip (bundled with Python)

## 🔧 Building the .EXE

### Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Build the .exe

Run `build.bat`:

```bash
build.bat
```

Or build manually:

```bash
python -m PyInstaller --clean KeyBlocker.spec
```

### Step 3: Get the .exe

After a successful build, `KeyBlocker.exe` will be in the `dist/` folder:

```
dist/
└── KeyBlocker.exe  ← This file (~19 MB)
```

The .exe has `uac_admin=True` embedded in its manifest, so it will request Administrator privileges automatically when launched.

## 📦 Installation

### Option 1: Run directly
- Double-click `KeyBlocker.exe`
- The program will request Administrator privileges (UAC popup)

### Option 2: Copy to Program Files
1. Copy `KeyBlocker.exe` to `C:\Program Files\KeyBlocker\`
2. Create a Desktop shortcut if desired

## 🚀 Usage

### Block a key

1. **Pick from the dropdown** or **type a key name** (e.g. `windows`, `alt`, `` ` ``)
2. Click **➕ Add** to add it to the list
3. Click **▶️ START BLOCKING** to activate

### Unblock a key

1. Select the key in the list
2. Click **🗑️ Remove selected key**

### 🎯 System Tray (background mode)

- The program shows a **🔒 icon in the system tray** (bottom-right of the taskbar)
- **Right-click the icon** to: show the window, start/stop blocking, or quit
- Closing the window (X) → automatically minimizes to tray (the program keeps running)

### ✅ Auto-saved settings

- The selected key list is **saved automatically** every time you add/remove a key
- Config file: `%LOCALAPPDATA%\KeyBlocker\settings.json`
- Reopen the program → the key list is **restored automatically**

### 🚀 Auto-start with Windows

Tick the **"🚀 Auto-start with Windows (background + auto-block)"** checkbox.

When enabled, on every Windows boot:
- ✨ The program starts hidden in the system tray (no window)
- ✨ Key blocking is enabled automatically for the saved keys
- ✨ **No** UAC confirmation required on each login

How it works: a Scheduled Task `KeyBlocker` is created (`ONLOGON` trigger, `/RL HIGHEST`) running the executable with the `--silent` flag. Because Task Scheduler supports "Run with highest privileges", the process is elevated directly without a UAC popup — this is why we use Task Scheduler instead of the Run registry key (the Run key does not auto-elevate, so an app requesting admin would be blocked by Windows in silent mode).

Older versions that used the Run key are migrated to a Scheduled Task automatically the first time the new version runs.

### 🔒 Single-instance protection

The program enforces single-instance via a lock file at `%LOCALAPPDATA%\KeyBlocker\instance.lock`:
- Manually opening a second copy → it writes a wake file `instance.wake`; the running instance detects it and brings its window to the front (the second copy exits silently — no popup)
- A second copy launched in silent mode → exits silently
- If the previous instance crashed → the stale lock file is cleaned up automatically on the next run (the PID is checked for liveness)

**Note when building/testing:** after building a new EXE, if the old one is still running in the background, double-clicking the new EXE will only bring the old window to the front (no new copy is spawned). Right-click the tray icon → **Quit**, then launch the new EXE.

### 🆘 Emergency exit

Press **Ctrl + Alt + Q** to disable blocking and quit immediately (even when hidden in the tray).

## 📝 Blockable keys

- System keys: `windows`, `alt`, `ctrl`, `shift`, `tab`, `esc`, `caps lock`
- Function keys: `f1`-`f12`
- Letters: `a`-`z`
- Digits: `0`-`9`
- Special: `` ` ``, `~`, `-`, `=`, `[`, `]`, `\`, `;`, `'`, `,`, `.`, `/`
- Navigation: `up`, `down`, `left`, `right`, `home`, `end`, `page up`, `page down`
- Others: `space`, `enter`, `backspace`, `delete`, `insert`, `print screen`

## ⚙️ Project Structure

```
key_blocker/
├── key_blocker.py          # Main source code
├── KeyBlocker.spec         # PyInstaller specification
├── build.bat               # Automated build script
├── run_key_blocker.bat     # Run from source (no build required)
├── requirements.txt        # Python dependencies
├── BUILD_INSTRUCTIONS.md   # This file
├── USER_GUIDE.md           # End-user guide
│
├── build/                  # Temporary build directory (auto-generated, gitignored)
└── dist/                   # Output directory for the .exe (auto-generated)
    └── KeyBlocker.exe
```

## 🐛 Troubleshooting

### Error: "Cannot block keys"
- ✅ Must be run as Administrator (the .exe self-elevates via UAC; running from source requires `run_key_blocker.bat`)
- ✅ Some antivirus software may block the keyboard hook → disable it temporarily and try again

### Error: "Module 'keyboard' not found"
```bash
pip install -r requirements.txt
```

### Error: `'pyinstaller' is not recognized`
PyInstaller is installed via pip, but `Scripts/` isn't on PATH. Use:
```bash
python -m PyInstaller --clean KeyBlocker.spec
```

### Build error (PYZ/EXE corrupted)
- Delete the `build/` and `dist/` folders
- Run `build.bat` again

### The program doesn't auto-start with Windows
- Re-tick the "🚀 Auto-start with Windows" checkbox in the UI
- Verify the Scheduled Task: PowerShell `Get-ScheduledTask -TaskName KeyBlocker` should report State `Ready`
- Or open **Task Scheduler** (`taskschd.msc`) and look for the `KeyBlocker` task

## 📄 License

Author: Vuong
Free to use - educational purpose

## ⚠️ Notes

- Administrator privileges are required to block system keys
- Always remember the emergency shortcut: **Ctrl + Alt + Q**
- Don't block every key at once (you'll lose control of the machine)
- Use responsibly
