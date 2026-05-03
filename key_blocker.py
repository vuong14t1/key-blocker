"""
Key Blocker - A simple key blocking tool for Windows.
Author: Vuong
Requires: pip install keyboard
Note: Must be run as Administrator.
"""

__version__ = "1.3.0"

import keyboard
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import ctypes
import winreg
import os
import json
import atexit
import subprocess
from pathlib import Path
try:
    import pystray
    from PIL import Image, ImageDraw
    HAS_PYSTRAY = True
except ImportError:
    HAS_PYSTRAY = False


TRANSLATIONS = {
    "en": {
        "lang_name": "English",
        "window_title": "Key Blocker v{version} - Block Keys",
        "title": "🔒 KEY BLOCKER",
        "subtitle": "Block unwanted keys on Windows",
        "version_label": "Version {version}",
        "admin_warning": "⚠️ Not running as Administrator!\nSome system keys may not be blocked.",
        "select_frame": "Select keys to block",
        "key_label": "Key:",
        "add_btn": "➕ Add",
        "or_type_label": "Or type:",
        "list_frame": "Keys to block",
        "remove_btn": "🗑️ Remove selected key",
        "start_btn": "▶️ START BLOCKING",
        "stop_btn": "⏸️ STOP BLOCKING",
        "status_idle": "● Status: Idle",
        "status_active": "● Status: BLOCKING KEYS",
        "tip": "💡 Tip: press Ctrl+Alt+Q for emergency exit",
        "language_label": "Language:",
        "startup_check": "🚀 Auto-start with Windows (background + auto-block)",
        "startup_hint": "When enabled: a Scheduled Task with highest privileges is created → the app starts hidden in the tray and enables blocking on login, with no UAC prompt.",
        "warn_title": "Warning",
        "info_title": "Notice",
        "error_title": "Error",
        "success_title": "Success",
        "warn_pick_key": "Please select a key!",
        "warn_type_key": "Please type a key name!",
        "info_key_exists": "Key '{key}' is already in the list!",
        "warn_select_to_remove": "Please select a key to remove!",
        "warn_add_one_first": "Please add at least one key to block!",
        "error_block": "Cannot block keys:\n{err}\n\nPlease run as Administrator!",
        "error_stop": "Error while stopping:\n{err}",
        "startup_enabled": "Auto-start with Windows is enabled!\n\nA Scheduled Task running with highest privileges has been created, so NO UAC confirmation will be needed on each login.",
        "startup_enable_failed": "Failed to create the Scheduled Task.\nPlease run the program as Administrator and try again.",
        "startup_disabled": "Auto-start has been disabled.",
        "startup_disable_failed": "Failed to remove the Scheduled Task.",
        "tray_show": "Show",
        "tray_start": "Start blocking",
        "tray_stop": "Stop blocking",
        "tray_exit": "Quit",
        "tray_tooltip": "Key Blocker v{version} - Block Keys",
        "background_title": "Running in background",
        "background_msg": "The program has been hidden to the system tray!\n\n💡 Right-click the 🔒 icon at the bottom-right\nto show it again or quit.",
    },
    "vi": {
        "lang_name": "Tiếng Việt",
        "window_title": "Key Blocker v{version} - Chặn phím",
        "title": "🔒 KEY BLOCKER",
        "subtitle": "Chặn các phím không mong muốn trên Windows",
        "version_label": "Phiên bản {version}",
        "admin_warning": "⚠️ Chưa chạy với quyền Administrator!\nMột số phím hệ thống có thể không chặn được.",
        "select_frame": "Chọn phím cần chặn",
        "key_label": "Phím:",
        "add_btn": "➕ Thêm",
        "or_type_label": "Hoặc nhập:",
        "list_frame": "Danh sách phím sẽ bị chặn",
        "remove_btn": "🗑️ Xóa phím đã chọn",
        "start_btn": "▶️ BẮT ĐẦU CHẶN",
        "stop_btn": "⏸️ DỪNG CHẶN",
        "status_idle": "● Trạng thái: Đang dừng",
        "status_active": "● Trạng thái: ĐANG CHẶN PHÍM",
        "tip": "💡 Mẹo: Nhấn Ctrl+Alt+Q để thoát khẩn cấp",
        "language_label": "Ngôn ngữ:",
        "startup_check": "🚀 Tự động khởi động cùng Windows (chạy nền + tự chặn)",
        "startup_hint": "Khi bật: dùng Scheduled Task chạy quyền cao nhất → app tự chạy ẩn ở tray và bật chặn phím khi đăng nhập, không cần UAC popup.",
        "warn_title": "Cảnh báo",
        "info_title": "Thông báo",
        "error_title": "Lỗi",
        "success_title": "Thành công",
        "warn_pick_key": "Vui lòng chọn một phím!",
        "warn_type_key": "Vui lòng nhập tên phím!",
        "info_key_exists": "Phím '{key}' đã có trong danh sách!",
        "warn_select_to_remove": "Vui lòng chọn phím cần xóa!",
        "warn_add_one_first": "Vui lòng thêm ít nhất một phím để chặn!",
        "error_block": "Không thể chặn phím:\n{err}\n\nVui lòng chạy với quyền Administrator!",
        "error_stop": "Lỗi khi dừng:\n{err}",
        "startup_enabled": "Đã bật tự động khởi động cùng Windows!\n\nĐã tạo Scheduled Task chạy với quyền cao nhất, nên sẽ KHÔNG cần xác nhận UAC mỗi lần đăng nhập.",
        "startup_enable_failed": "Không thể tạo Scheduled Task.\nVui lòng chạy chương trình với quyền Administrator và thử lại.",
        "startup_disabled": "Đã tắt tự động khởi động.",
        "startup_disable_failed": "Không thể xoá Scheduled Task.",
        "tray_show": "Hiển thị",
        "tray_start": "Bắt đầu chặn",
        "tray_stop": "Dừng chặn",
        "tray_exit": "Thoát",
        "tray_tooltip": "Key Blocker v{version} - Chặn phím",
        "background_title": "Chạy nền",
        "background_msg": "Chương trình đã ẩn xuống system tray!\n\n💡 Click phải vào icon 🔒 ở góc dưới bên phải\nđể hiển thị lại hoặc thoát chương trình.",
    },
}

DEFAULT_LANG = "en"


def is_admin():
    """Check whether the program is running as Administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


TASK_NAME = "KeyBlocker"


def _run_schtasks(args):
    """Run schtasks.exe with the console window hidden. Returns CompletedProcess."""
    CREATE_NO_WINDOW = 0x08000000
    return subprocess.run(
        ["schtasks.exe"] + args,
        capture_output=True,
        text=True,
        creationflags=CREATE_NO_WINDOW,
    )


def _remove_legacy_run_key():
    """Remove the legacy Run key entry (the old startup mechanism, before Task Scheduler)."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_ALL_ACCESS,
        )
        try:
            winreg.DeleteValue(key, "KeyBlocker")
        except FileNotFoundError:
            pass
        finally:
            winreg.CloseKey(key)
    except Exception:
        pass


def is_startup_enabled():
    """Return True if the KeyBlocker Scheduled Task exists."""
    result = _run_schtasks(["/Query", "/TN", TASK_NAME])
    return result.returncode == 0


def enable_startup():
    """Create a Scheduled Task that runs at logon with highest privileges (no UAC popup).

    The Run registry key does not auto-elevate, so for an app that requires admin
    Windows would either block it in silent mode or force a UAC click on every
    boot. A Scheduled Task with /RL HIGHEST is elevated directly at logon,
    bypassing UAC.
    """
    exe_path = os.path.abspath(sys.argv[0])
    if exe_path.endswith('.py'):
        pythonw = sys.executable.replace('python.exe', 'pythonw.exe')
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        tr = f'"{pythonw}" "{exe_path}" --silent'
    else:
        tr = f'"{exe_path}" --silent'

    result = _run_schtasks([
        "/Create", "/TN", TASK_NAME,
        "/TR", tr,
        "/SC", "ONLOGON",
        "/RL", "HIGHEST",
        "/F",
    ])
    if result.returncode != 0:
        print(f"Failed to create Scheduled Task: {result.stderr or result.stdout}")
        return False

    _remove_legacy_run_key()
    return True


def disable_startup():
    """Remove the Scheduled Task (and the legacy Run key entry, if any)."""
    _run_schtasks(["/Delete", "/TN", TASK_NAME, "/F"])
    _remove_legacy_run_key()
    return True


def _has_legacy_run_key():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        )
        try:
            winreg.QueryValueEx(key, "KeyBlocker")
            return True
        except FileNotFoundError:
            return False
        finally:
            winreg.CloseKey(key)
    except Exception:
        return False


def migrate_legacy_startup_if_needed():
    """If the user previously enabled auto-start via the Run key (old mechanism,
    blocked by UAC), migrate to a Scheduled Task to preserve their intent."""
    if is_startup_enabled():
        return
    if _has_legacy_run_key():
        enable_startup()


def get_config_path():
    """Return the path to the settings file."""
    config_dir = Path.home() / "AppData" / "Local" / "KeyBlocker"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "settings.json"


def get_lock_file_path():
    """Return the path to the single-instance lock file."""
    config_dir = Path.home() / "AppData" / "Local" / "KeyBlocker"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "instance.lock"


def get_wake_file_path():
    """Flag file used by a second instance to ask the running one to show its window."""
    config_dir = Path.home() / "AppData" / "Local" / "KeyBlocker"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "instance.wake"


def signal_existing_instance_to_show():
    """Create a wake file so the running instance knows the user double-clicked the app again."""
    try:
        get_wake_file_path().write_text(str(os.getpid()), encoding='utf-8')
    except OSError:
        pass


def _is_pid_alive(pid):
    """Check whether a PID is still alive (Windows-only)."""
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259
    try:
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong(0)
            if ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return exit_code.value == STILL_ACTIVE
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        pass
    return False


def acquire_single_instance_lock():
    """Write the current PID to the lock file. Returns True if we are the only instance,
    False if another instance is already running."""
    lock_path = get_lock_file_path()
    if lock_path.exists():
        try:
            existing_pid = int(lock_path.read_text(encoding='utf-8').strip())
            if existing_pid != os.getpid() and _is_pid_alive(existing_pid):
                return False
        except (ValueError, OSError):
            pass  # corrupt lock file → treat as stale, overwrite
    try:
        lock_path.write_text(str(os.getpid()), encoding='utf-8')
        return True
    except OSError:
        return True  # cannot write lock → allow run (fail-open)


def release_single_instance_lock():
    """Remove the lock file if it belongs to the current process."""
    try:
        lock_path = get_lock_file_path()
        if not lock_path.exists():
            return
        try:
            owner_pid = int(lock_path.read_text(encoding='utf-8').strip())
        except (ValueError, OSError):
            return
        if owner_pid == os.getpid():
            lock_path.unlink(missing_ok=True)
    except Exception:
        pass


def load_settings():
    """Load saved settings."""
    try:
        config_path = get_config_path()
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load settings: {e}")
    return {"blocked_keys": [], "language": DEFAULT_LANG}


def save_settings(blocked_keys, language=DEFAULT_LANG):
    """Persist settings."""
    try:
        config_path = get_config_path()
        settings = {
            "blocked_keys": list(blocked_keys),
            "language": language,
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Failed to save settings: {e}")
        return False


class KeyBlockerApp:
    def __init__(self, root, silent_mode=False):
        self.root = root
        self.silent_mode = silent_mode

        settings = load_settings()
        lang = settings.get("language", DEFAULT_LANG)
        if lang not in TRANSLATIONS:
            lang = DEFAULT_LANG
        self.language = lang
        self._initial_blocked_keys = settings.get("blocked_keys", [])

        self.root.title(self.t("window_title").format(version=__version__))
        self.root.geometry("500x680")
        self.root.resizable(False, False)

        # Currently blocked keys
        self.blocked_keys = {}
        self.is_blocking = False
        self.tray_icon = None
        # Suppress the "minimized to tray" popup when running silent
        self.first_hide = not silent_mode

        # Common keys to choose from
        self.common_keys = [
            "windows", "alt", "ctrl", "shift", "tab", "esc", "caps lock",
            "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
            "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "space", "enter", "backspace", "delete", "insert",
            "home", "end", "page up", "page down",
            "up", "down", "left", "right",
            "print screen", "scroll lock", "pause",
            "`", "~", "-", "=", "[", "]", "\\", ";", "'", ",", ".", "/"
        ]

        self.setup_ui()
        self.load_saved_settings()
        if HAS_PYSTRAY:
            self.setup_tray_icon()

        # Watch the wake file: when the user double-clicks the app again, the
        # other instance writes this file → we show the window instead of
        # letting them see an "already running" popup.
        try:
            get_wake_file_path().unlink(missing_ok=True)  # clean up stale file from a previous run
        except Exception:
            pass
        self._poll_wake_signal()

    def t(self, key):
        """Translate a key for the current language."""
        return TRANSLATIONS.get(self.language, TRANSLATIONS[DEFAULT_LANG]).get(
            key, TRANSLATIONS[DEFAULT_LANG].get(key, key)
        )

    def setup_ui(self):
        # Title
        self.title_label = tk.Label(
            self.root,
            text=self.t("title"),
            font=("Arial", 20, "bold"),
            fg="#2c3e50"
        )
        self.title_label.pack(pady=10)

        self.subtitle_label = tk.Label(
            self.root,
            text=self.t("subtitle"),
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        self.subtitle_label.pack()

        self.version_label = tk.Label(
            self.root,
            text=self.t("version_label").format(version=__version__),
            font=("Arial", 8),
            fg="#95a5a6"
        )
        self.version_label.pack()

        # Language switcher
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(pady=4)
        self.language_label_widget = tk.Label(
            lang_frame, text=self.t("language_label"), font=("Arial", 9)
        )
        self.language_label_widget.pack(side="left", padx=4)

        self.language_var = tk.StringVar(value=self.language)
        self.language_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=list(TRANSLATIONS.keys()),
            width=6,
            state="readonly",
        )
        self.language_combo.pack(side="left")
        self.language_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        # Admin warning
        self.admin_warning = None
        if not is_admin():
            self.admin_warning = tk.Label(
                self.root,
                text=self.t("admin_warning"),
                font=("Arial", 9),
                fg="red",
                bg="#fff3cd"
            )
            self.admin_warning.pack(pady=5, padx=20, fill="x")

        # Key picker frame
        self.select_frame = tk.LabelFrame(
            self.root,
            text=self.t("select_frame"),
            font=("Arial", 10, "bold"),
            padx=10, pady=10
        )
        self.select_frame.pack(pady=10, padx=20, fill="x")

        # Combobox key picker
        self.key_label_widget = tk.Label(self.select_frame, text=self.t("key_label"))
        self.key_label_widget.grid(row=0, column=0, sticky="w", pady=5)
        self.key_var = tk.StringVar()
        self.key_combo = ttk.Combobox(
            self.select_frame,
            textvariable=self.key_var,
            values=self.common_keys,
            width=30
        )
        self.key_combo.grid(row=0, column=1, padx=5, pady=5)
        self.key_combo.set("windows")

        # Add button
        self.add_btn = tk.Button(
            self.select_frame,
            text=self.t("add_btn"),
            command=self.add_key,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        self.add_btn.grid(row=0, column=2, padx=5)

        # Or type your own
        self.or_type_label = tk.Label(
            self.select_frame, text=self.t("or_type_label"), font=("Arial", 9, "italic")
        )
        self.or_type_label.grid(row=1, column=0, sticky="w", pady=5)
        self.custom_key = tk.Entry(self.select_frame, width=33)
        self.custom_key.grid(row=1, column=1, padx=5, pady=5)

        self.custom_btn = tk.Button(
            self.select_frame,
            text=self.t("add_btn"),
            command=self.add_custom_key,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        self.custom_btn.grid(row=1, column=2, padx=5)

        # Blocked keys list frame
        self.list_frame = tk.LabelFrame(
            self.root,
            text=self.t("list_frame"),
            font=("Arial", 10, "bold"),
            padx=10, pady=10
        )
        self.list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Listbox + scrollbar
        list_container = tk.Frame(self.list_frame)
        list_container.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")

        self.key_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 11),
            height=8
        )
        self.key_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.key_listbox.yview)

        # Remove button
        self.remove_btn = tk.Button(
            self.list_frame,
            text=self.t("remove_btn"),
            command=self.remove_key,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        self.remove_btn.pack(pady=5)

        # Control frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.toggle_btn = tk.Button(
            control_frame,
            text=self.t("start_btn"),
            command=self.toggle_blocking,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            cursor="hand2"
        )
        self.toggle_btn.pack(pady=5)

        # Status
        self.status_label = tk.Label(
            self.root,
            text=self.t("status_idle"),
            font=("Arial", 10, "bold"),
            fg="#e74c3c"
        )
        self.status_label.pack(pady=5)

        # Tip
        self.tip_label = tk.Label(
            self.root,
            text=self.t("tip"),
            font=("Arial", 9, "italic"),
            fg="#7f8c8d"
        )
        self.tip_label.pack(pady=5)

        # Options frame
        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=5)

        # Auto-start with Windows in silent mode
        self.startup_var = tk.BooleanVar(value=is_startup_enabled())
        self.startup_check = tk.Checkbutton(
            options_frame,
            text=self.t("startup_check"),
            variable=self.startup_var,
            command=self.toggle_startup,
            font=("Arial", 10),
            cursor="hand2"
        )
        self.startup_check.pack(anchor="w", padx=20)

        self.startup_hint = tk.Label(
            options_frame,
            text=self.t("startup_hint"),
            font=("Arial", 8, "italic"),
            fg="#7f8c8d",
            wraplength=440,
            justify="left"
        )
        self.startup_hint.pack(anchor="w", padx=40)

        # Emergency-exit hotkey
        keyboard.add_hotkey('ctrl+alt+q', self.emergency_exit)

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _on_language_change(self, _event=None):
        new_lang = self.language_var.get()
        if new_lang not in TRANSLATIONS or new_lang == self.language:
            return
        self.language = new_lang
        self.save_current_settings()
        self.refresh_ui_text()

    def refresh_ui_text(self):
        """Re-apply all translatable strings after a language change."""
        self.root.title(self.t("window_title").format(version=__version__))
        self.title_label.config(text=self.t("title"))
        self.subtitle_label.config(text=self.t("subtitle"))
        self.version_label.config(text=self.t("version_label").format(version=__version__))
        self.language_label_widget.config(text=self.t("language_label"))
        if self.admin_warning is not None:
            self.admin_warning.config(text=self.t("admin_warning"))
        self.select_frame.config(text=self.t("select_frame"))
        self.key_label_widget.config(text=self.t("key_label"))
        self.add_btn.config(text=self.t("add_btn"))
        self.or_type_label.config(text=self.t("or_type_label"))
        self.custom_btn.config(text=self.t("add_btn"))
        self.list_frame.config(text=self.t("list_frame"))
        self.remove_btn.config(text=self.t("remove_btn"))
        self.toggle_btn.config(
            text=self.t("stop_btn") if self.is_blocking else self.t("start_btn")
        )
        self.status_label.config(
            text=self.t("status_active") if self.is_blocking else self.t("status_idle")
        )
        self.tip_label.config(text=self.t("tip"))
        self.startup_check.config(text=self.t("startup_check"))
        self.startup_hint.config(text=self.t("startup_hint"))
        # Rebuild the tray menu with translated labels
        if HAS_PYSTRAY and self.tray_icon is not None:
            self._rebuild_tray_menu()

    def add_key(self):
        key = self.key_var.get().strip().lower()
        if not key:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_pick_key"))
            return

        if key in self.blocked_keys:
            messagebox.showinfo(self.t("info_title"), self.t("info_key_exists").format(key=key))
            return

        self.blocked_keys[key] = None
        self.key_listbox.insert(tk.END, f"  🔒  {key.upper()}")
        self.save_current_settings()

    def add_custom_key(self):
        key = self.custom_key.get().strip().lower()
        if not key:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_type_key"))
            return

        if key in self.blocked_keys:
            messagebox.showinfo(self.t("info_title"), self.t("info_key_exists").format(key=key))
            return

        self.blocked_keys[key] = None
        self.key_listbox.insert(tk.END, f"  🔒  {key.upper()}")
        self.custom_key.delete(0, tk.END)
        self.save_current_settings()

    def remove_key(self):
        selection = self.key_listbox.curselection()
        if not selection:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_select_to_remove"))
            return

        index = selection[0]
        item = self.key_listbox.get(index)
        # Extract the key name from the displayed string
        key = item.split("🔒")[1].strip().lower()

        # Unhook if currently blocked
        if self.is_blocking and key in self.blocked_keys and self.blocked_keys[key] is not None:
            try:
                keyboard.remove_hotkey(self.blocked_keys[key])
            except:
                pass

        del self.blocked_keys[key]
        self.key_listbox.delete(index)
        self.save_current_settings()

    def toggle_blocking(self):
        if not self.is_blocking:
            self.start_blocking()
        else:
            self.stop_blocking()

    def start_blocking(self):
        if not self.blocked_keys:
            messagebox.showwarning(self.t("warn_title"), self.t("warn_add_one_first"))
            return

        try:
            for key in self.blocked_keys:
                # Block the key by registering a suppress-hotkey
                self.blocked_keys[key] = keyboard.block_key(key)

            self.is_blocking = True
            self.toggle_btn.config(
                text=self.t("stop_btn"),
                bg="#e74c3c"
            )
            self.status_label.config(
                text=self.t("status_active"),
                fg="#27ae60"
            )
        except Exception as e:
            messagebox.showerror(self.t("error_title"), self.t("error_block").format(err=str(e)))

    def stop_blocking(self):
        try:
            for key in list(self.blocked_keys.keys()):
                if self.blocked_keys[key] is not None:
                    try:
                        keyboard.unblock_key(key)
                    except:
                        pass
                    self.blocked_keys[key] = None

            self.is_blocking = False
            self.toggle_btn.config(
                text=self.t("start_btn"),
                bg="#27ae60"
            )
            self.status_label.config(
                text=self.t("status_idle"),
                fg="#e74c3c"
            )
        except Exception as e:
            messagebox.showerror(self.t("error_title"), self.t("error_stop").format(err=str(e)))

    def toggle_startup(self):
        """Toggle Windows auto-start."""
        if self.startup_var.get():
            if enable_startup():
                messagebox.showinfo(self.t("success_title"), self.t("startup_enabled"))
            else:
                messagebox.showerror(self.t("error_title"), self.t("startup_enable_failed"))
                self.startup_var.set(False)
        else:
            if disable_startup():
                messagebox.showinfo(self.t("success_title"), self.t("startup_disabled"))
            else:
                messagebox.showerror(self.t("error_title"), self.t("startup_disable_failed"))
                self.startup_var.set(True)

    def load_saved_settings(self):
        """Restore the saved key list."""
        for key in self._initial_blocked_keys:
            if key and key not in self.blocked_keys:
                self.blocked_keys[key] = None
                self.key_listbox.insert(tk.END, f"  🔒  {key.upper()}")

        # Silent mode (auto-start with Windows): hide the window + start blocking immediately
        if self.silent_mode:
            self.root.withdraw()
            if self.blocked_keys:
                self.root.after(500, self.start_blocking)

    def save_current_settings(self):
        """Persist current settings."""
        save_settings(list(self.blocked_keys.keys()), self.language)

    def create_tray_image(self):
        """Create the system tray icon."""
        # 64x64 lock icon
        image = Image.new('RGB', (64, 64), color='#2c3e50')
        dc = ImageDraw.Draw(image)

        # Simple lock symbol
        # Body
        dc.rectangle([20, 35, 44, 55], fill='#ecf0f1', outline='#ecf0f1')
        # Shackle
        dc.arc([24, 20, 40, 40], start=180, end=0, fill='#ecf0f1', width=4)
        # Keyhole
        dc.ellipse([29, 42, 35, 48], fill='#2c3e50')

        return image

    def _build_tray_menu(self):
        return pystray.Menu(
            pystray.MenuItem(self.t("tray_show"), self.show_window, default=True),
            pystray.MenuItem(self.t("tray_start"), self.tray_start_blocking,
                            visible=lambda item: not self.is_blocking),
            pystray.MenuItem(self.t("tray_stop"), self.tray_stop_blocking,
                            visible=lambda item: self.is_blocking),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(self.t("tray_exit"), self.tray_exit)
        )

    def _rebuild_tray_menu(self):
        try:
            self.tray_icon.menu = self._build_tray_menu()
            self.tray_icon.title = self.t("tray_tooltip").format(version=__version__)
            self.tray_icon.update_menu()
        except Exception:
            pass

    def setup_tray_icon(self):
        """Set up the system tray icon."""
        if not HAS_PYSTRAY:
            return

        try:
            menu = self._build_tray_menu()
            image = self.create_tray_image()
            self.tray_icon = pystray.Icon(
                "KeyBlocker",
                image,
                self.t("tray_tooltip").format(version=__version__),
                menu
            )
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Failed to create tray icon: {e}")

    def show_window(self, icon=None, item=None):
        """Show the window from the tray."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _poll_wake_signal(self):
        """Check for the wake file every second; if present, delete it and show the window."""
        try:
            wake_path = get_wake_file_path()
            if wake_path.exists():
                wake_path.unlink(missing_ok=True)
                self.show_window()
        except Exception:
            pass
        self.root.after(1000, self._poll_wake_signal)

    def hide_to_tray(self):
        """Hide the window to the tray."""
        if HAS_PYSTRAY and self.tray_icon:
            # Show the notice the first time
            if self.first_hide:
                self.first_hide = False
                messagebox.showinfo(
                    self.t("background_title"),
                    self.t("background_msg")
                )
            self.root.withdraw()
        else:
            self.root.iconify()

    def tray_start_blocking(self, icon=None, item=None):
        """Start blocking from the tray menu."""
        self.root.after(0, self.start_blocking)

    def tray_stop_blocking(self, icon=None, item=None):
        """Stop blocking from the tray menu."""
        self.root.after(0, self.stop_blocking)

    def tray_exit(self, icon=None, item=None):
        """Quit from the tray menu."""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.quit_app)

    def emergency_exit(self):
        """Emergency exit via Ctrl+Alt+Q."""
        self.stop_blocking()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        sys.exit(0)

    def on_close(self):
        """Handle the close (X) button — always hide to tray when possible."""
        self.save_current_settings()

        if HAS_PYSTRAY and self.tray_icon:
            self.hide_to_tray()
        else:
            self.quit_app()

    def quit_app(self):
        """Fully quit the app."""
        self.save_current_settings()

        if self.is_blocking:
            self.stop_blocking()

        if self.tray_icon:
            self.tray_icon.stop()

        try:
            keyboard.unhook_all()
        except:
            pass

        self.root.destroy()


def main():
    silent_mode = '--silent' in sys.argv

    # Enforce single-instance — done before elevation so we don't spawn a useless UAC prompt.
    # If the user double-clicks the EXE while a background instance is already
    # running → signal that instance to bring its window to the front (instead
    # of showing an "already running" popup).
    if not acquire_single_instance_lock():
        if not silent_mode:
            signal_existing_instance_to_show()
        sys.exit(0)

    atexit.register(release_single_instance_lock)

    # Self-elevate if not running as admin
    if not is_admin():
        # Release the lock so the elevated process can re-acquire it
        release_single_instance_lock()
        try:
            params = " ".join(f'"{a}"' if " " in a else a for a in sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable,
                f'"{sys.argv[0]}" {params}'.strip(),
                None,
                0 if silent_mode else 1
            )
            sys.exit(0)
        except Exception:
            # Elevation failed → re-acquire the lock and run with current privileges
            acquire_single_instance_lock()

    migrate_legacy_startup_if_needed()

    root = tk.Tk()
    app = KeyBlockerApp(root, silent_mode=silent_mode)
    root.mainloop()


if __name__ == "__main__":
    main()
