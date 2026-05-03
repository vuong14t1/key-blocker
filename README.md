# Key Blocker

A simple Windows tool to block unwanted keys. Tkinter UI, runs in the system tray, supports auto-start with Windows without a UAC prompt.

## Features

- Block any key: Windows, Alt, Ctrl, Shift, F1-F12, Caps Lock, letters, ...
- Auto-saves the key list (`%LOCALAPPDATA%\KeyBlocker\settings.json`)
- Runs in the system tray (🔒 icon)
- Auto-start via a **Scheduled Task** with highest privileges → no UAC prompt in silent mode
- Single-instance: a second double-click brings the running window to the front instead of spawning a new copy
- Emergency hotkey: **Ctrl + Alt + Q**
- Language switcher: English (default) / Vietnamese

## Requirements

- Windows 10/11
- Python 3.8+ (only when running from source)
- Administrator privileges (required to block system keys like `windows`, `ctrl`, `alt`)

## Run from source

```bash
pip install -r requirements.txt
```

Right-click `run_key_blocker.bat` → **Run as administrator**, or:

```bash
python key_blocker.py
```

## Build the .exe

```bash
build.bat
```

`KeyBlocker.exe` (~19 MB) will be in `dist/`. The manifest already embeds `uac_admin=True`, so the .exe self-elevates when double-clicked.

## How to use

1. Pick a key from the combobox or type one in → click **➕ Add**
2. Click **▶️ START BLOCKING**
3. Close the window (X) → minimizes to tray, keeps running in the background
4. Right-click the tray icon 🔒 to show / stop / quit

Tick **🚀 Auto-start with Windows** to make Key Blocker run hidden and start blocking immediately on logon.

## Documentation

- [USER_GUIDE.md](USER_GUIDE.md) — End-user guide
- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) — Build steps, architecture, troubleshooting

## License

Free to use - educational purpose. Author: Vuong.
