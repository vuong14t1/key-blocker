# 🔒 Key Blocker - Windows Key Blocking Tool

A simple tool to block unwanted keys on Windows. Useful for:
- Blocking the Windows key while gaming
- Locking keys to prevent kids from pressing them randomly
- Disabling annoying keys like Caps Lock, Insert
- Blocking F1-F12 in certain applications

## 📋 System Requirements

- Windows 7/8/10/11
- Python 3.7 or later ([Download here](https://www.python.org/downloads/))
- Administrator privileges (required to block system keys)

## 🚀 Installation

### Step 1: Install Python
Download and install Python from https://www.python.org/downloads/
**Important:** Check the **"Add Python to PATH"** option during installation.

### Step 2: Install the keyboard library
Open Command Prompt and run:
```bash
pip install keyboard
```

### Step 3: Run the program
**Option 1 (Recommended):** Right-click `run_key_blocker.bat` → select **Run as administrator**

**Option 2:** Open CMD as Administrator, then run:
```bash
python key_blocker.py
```

## 🎯 How to Use

1. **Add a key to block:**
   - Pick from the dropdown list → click **➕ Add**
   - Or type any key name into the input box → click **➕ Add**

2. **Start blocking:** Click **▶️ START BLOCKING**

3. **Stop blocking:** Click **⏸️ STOP BLOCKING**

4. **Remove a key:** Select the key from the list → click **🗑️ Remove selected key**

5. **Close the window:** Click X → the program hides to the system tray (bottom-right corner, 🔒 icon). Right-click the icon to show the window again or to quit.

## 🚀 Run on Windows startup

Tick the **"🚀 Auto-start with Windows (run in background + auto-block)"** checkbox.

When enabled:
- Creates a Scheduled Task `KeyBlocker` that runs with the highest privileges on user logon
- On every Windows boot → the program starts hidden in the tray and auto-enables key blocking
- **No** UAC confirmation required on each login (unlike the Run registry key approach)

When disabled: untick → the Scheduled Task is removed automatically.

> Note: The first time you enable it, the app must be running as Administrator so the Task can be created.

## 🔒 Single instance only

The program prevents two copies from running at once. If you double-click the EXE while a background instance is already running → the existing instance will **bring its window to the front** (the second instance exits silently).

To run a freshly built EXE: right-click the 🔒 tray icon → **Quit**, then launch the new EXE.

## ⌨️ Common key names

| Key | Name in the app |
|-----|-----------------|
| Windows key | `windows` |
| Alt | `alt` |
| Ctrl | `ctrl` |
| Shift | `shift` |
| Caps Lock | `caps lock` |
| Tab | `tab` |
| Esc | `esc` |
| Enter | `enter` |
| Space | `space` |
| Backspace | `backspace` |
| Delete | `delete` |
| Arrow keys | `up`, `down`, `left`, `right` |
| F1-F12 | `f1`, `f2`, ..., `f12` |
| Print Screen | `print screen` |

## 🆘 Emergency exit

Press **Ctrl + Alt + Q** to quit the program immediately (even while keys are being blocked).

## ⚠️ Important notes

- **Must be run as Administrator** to block system keys like `windows`, `ctrl`, `alt`
- Don't block every key at once → you'll lose control of the machine
- Always remember the **Ctrl+Alt+Q** emergency-exit shortcut
- All keys are released automatically when the program exits

## 🐛 Troubleshooting

**Error "ImportError: No module named 'keyboard'":**
```bash
pip install keyboard
```

**Cannot block the Windows key:**
→ The program must be run as Administrator

**Keys still work after pressing "Start Blocking":**
→ Close the program, right-click the `.bat` file → Run as administrator

## 📝 License

Free software - for personal use.
