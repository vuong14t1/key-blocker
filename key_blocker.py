"""
Key Blocker - Phần mềm chặn phím đơn giản trên Windows
Tác giả: Vuong
Yêu cầu: pip install keyboard
Lưu ý: Cần chạy với quyền Administrator
"""

__version__ = "1.2.0"

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


def is_admin():
    """Kiểm tra xem chương trình có đang chạy với quyền Admin không"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


TASK_NAME = "KeyBlocker"


def _run_schtasks(args):
    """Chạy schtasks.exe ẩn cửa sổ console. Trả về CompletedProcess."""
    CREATE_NO_WINDOW = 0x08000000
    return subprocess.run(
        ["schtasks.exe"] + args,
        capture_output=True,
        text=True,
        creationflags=CREATE_NO_WINDOW,
    )


def _remove_legacy_run_key():
    """Gỡ entry Run key cũ (cơ chế startup cũ trước khi chuyển sang Task Scheduler)."""
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
    """Kiểm tra Scheduled Task KeyBlocker có tồn tại không."""
    result = _run_schtasks(["/Query", "/TN", TASK_NAME])
    return result.returncode == 0


def enable_startup():
    """Tạo Scheduled Task chạy lúc đăng nhập với quyền cao nhất (không cần UAC popup).

    Run registry key không tự nâng quyền, nên với app yêu cầu admin nó sẽ bị
    Windows chặn ở silent mode hoặc bắt user click UAC mỗi lần boot. Scheduled
    Task với /RL HIGHEST chạy elevated trực tiếp, bypass UAC khi đăng nhập.
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
        print(f"Lỗi khi tạo Scheduled Task: {result.stderr or result.stdout}")
        return False

    _remove_legacy_run_key()
    return True


def disable_startup():
    """Xoá Scheduled Task (và entry Run key cũ nếu còn)."""
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
    """Người dùng từng bật auto-start qua Run key (cơ chế cũ, bị UAC chặn) →
    chuyển sang Scheduled Task để giữ đúng ý định."""
    if is_startup_enabled():
        return
    if _has_legacy_run_key():
        enable_startup()


def get_config_path():
    """Lấy đường dẫn file cấu hình"""
    config_dir = Path.home() / "AppData" / "Local" / "KeyBlocker"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "settings.json"


def get_lock_file_path():
    """Lấy đường dẫn lock file để chống chạy 2 instance"""
    config_dir = Path.home() / "AppData" / "Local" / "KeyBlocker"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "instance.lock"


def get_wake_file_path():
    """File flag để instance thứ 2 ra hiệu cho instance đang chạy hiện cửa sổ."""
    config_dir = Path.home() / "AppData" / "Local" / "KeyBlocker"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "instance.wake"


def signal_existing_instance_to_show():
    """Tạo wake file để instance đang chạy biết là user vừa double-click app lần nữa."""
    try:
        get_wake_file_path().write_text(str(os.getpid()), encoding='utf-8')
    except OSError:
        pass


def _is_pid_alive(pid):
    """Kiểm tra PID có còn chạy không (Windows-only)"""
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
    """Tạo lock file với PID hiện tại. Trả về True nếu là instance duy nhất,
    False nếu đã có instance khác đang chạy."""
    lock_path = get_lock_file_path()
    if lock_path.exists():
        try:
            existing_pid = int(lock_path.read_text(encoding='utf-8').strip())
            if existing_pid != os.getpid() and _is_pid_alive(existing_pid):
                return False
        except (ValueError, OSError):
            pass  # lock file hỏng → coi như stale, ghi đè
    try:
        lock_path.write_text(str(os.getpid()), encoding='utf-8')
        return True
    except OSError:
        return True  # không ghi được lock → cho phép chạy (fail-open)


def release_single_instance_lock():
    """Xóa lock file nếu nó thuộc về process hiện tại"""
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
    """Đọc cài đặt đã lưu"""
    try:
        config_path = get_config_path()
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Lỗi khi đọc cài đặt: {e}")
    return {"blocked_keys": []}


def save_settings(blocked_keys):
    """Lưu cài đặt"""
    try:
        config_path = get_config_path()
        settings = {"blocked_keys": list(blocked_keys)}
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Lỗi khi lưu cài đặt: {e}")
        return False


class KeyBlockerApp:
    def __init__(self, root, silent_mode=False):
        self.root = root
        self.silent_mode = silent_mode
        self.root.title(f"Key Blocker v{__version__} - Chặn phím")
        self.root.geometry("500x640")
        self.root.resizable(False, False)

        # Danh sách các phím đang được chặn
        self.blocked_keys = {}
        self.is_blocking = False
        self.tray_icon = None
        # Khi chạy silent thì không hiện popup khi ẩn xuống tray
        self.first_hide = not silent_mode
        
        # Danh sách các phím phổ biến để chọn
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

        # Theo dõi wake file: khi user double-click EXE lần nữa, instance kia
        # ghi file này → ta hiện cửa sổ thay vì để họ thấy popup "đã đang chạy".
        try:
            get_wake_file_path().unlink(missing_ok=True)  # dọn file stale từ lần trước
        except Exception:
            pass
        self._poll_wake_signal()
    
    def setup_ui(self):
        # Tiêu đề
        title_label = tk.Label(
            self.root, 
            text="🔒 KEY BLOCKER",
            font=("Arial", 20, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        subtitle = tk.Label(
            self.root,
            text="Chặn các phím không mong muốn trên Windows",
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        subtitle.pack()

        version_label = tk.Label(
            self.root,
            text=f"Phiên bản {__version__}",
            font=("Arial", 8),
            fg="#95a5a6"
        )
        version_label.pack()
        
        # Cảnh báo nếu không có quyền admin
        if not is_admin():
            warning = tk.Label(
                self.root,
                text="⚠️ Chưa chạy với quyền Administrator!\nMột số phím hệ thống có thể không chặn được.",
                font=("Arial", 9),
                fg="red",
                bg="#fff3cd"
            )
            warning.pack(pady=5, padx=20, fill="x")
        
        # Frame chọn phím
        select_frame = tk.LabelFrame(
            self.root,
            text="Chọn phím cần chặn",
            font=("Arial", 10, "bold"),
            padx=10, pady=10
        )
        select_frame.pack(pady=10, padx=20, fill="x")
        
        # Combobox chọn phím
        tk.Label(select_frame, text="Phím:").grid(row=0, column=0, sticky="w", pady=5)
        self.key_var = tk.StringVar()
        self.key_combo = ttk.Combobox(
            select_frame,
            textvariable=self.key_var,
            values=self.common_keys,
            width=30
        )
        self.key_combo.grid(row=0, column=1, padx=5, pady=5)
        self.key_combo.set("windows")
        
        # Nút thêm phím
        add_btn = tk.Button(
            select_frame,
            text="➕ Thêm",
            command=self.add_key,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        add_btn.grid(row=0, column=2, padx=5)
        
        # Hoặc nhập tay
        tk.Label(select_frame, text="Hoặc nhập:", font=("Arial", 9, "italic")).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.custom_key = tk.Entry(select_frame, width=33)
        self.custom_key.grid(row=1, column=1, padx=5, pady=5)
        
        custom_btn = tk.Button(
            select_frame,
            text="➕ Thêm",
            command=self.add_custom_key,
            bg="#9b59b6",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        custom_btn.grid(row=1, column=2, padx=5)
        
        # Frame danh sách phím đã chặn
        list_frame = tk.LabelFrame(
            self.root,
            text="Danh sách phím sẽ bị chặn",
            font=("Arial", 10, "bold"),
            padx=10, pady=10
        )
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Listbox với scrollbar
        list_container = tk.Frame(list_frame)
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
        
        # Nút xóa phím
        remove_btn = tk.Button(
            list_frame,
            text="🗑️ Xóa phím đã chọn",
            command=self.remove_key,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2"
        )
        remove_btn.pack(pady=5)
        
        # Frame điều khiển
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        self.toggle_btn = tk.Button(
            control_frame,
            text="▶️ BẮT ĐẦU CHẶN",
            command=self.toggle_blocking,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2,
            cursor="hand2"
        )
        self.toggle_btn.pack(pady=5)
        
        # Trạng thái
        self.status_label = tk.Label(
            self.root,
            text="● Trạng thái: Đang dừng",
            font=("Arial", 10, "bold"),
            fg="#e74c3c"
        )
        self.status_label.pack(pady=5)
        
        # Hướng dẫn
        info = tk.Label(
            self.root,
            text="💡 Mẹo: Nhấn Ctrl+Alt+Q để thoát khẩn cấp",
            font=("Arial", 9, "italic"),
            fg="#7f8c8d"
        )
        info.pack(pady=5)

        # Frame cho các tùy chọn
        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=5)

        # Tùy chọn duy nhất: tự động khởi động cùng Windows ở chế độ silent
        self.startup_var = tk.BooleanVar(value=is_startup_enabled())
        startup_check = tk.Checkbutton(
            options_frame,
            text="🚀 Tự động khởi động cùng Windows (chạy nền + tự chặn)",
            variable=self.startup_var,
            command=self.toggle_startup,
            font=("Arial", 10),
            cursor="hand2"
        )
        startup_check.pack(anchor="w", padx=20)

        startup_hint = tk.Label(
            options_frame,
            text="Khi bật: dùng Scheduled Task chạy quyền cao nhất → app tự chạy ẩn ở tray và bật chặn phím khi đăng nhập, không cần UAC popup.",
            font=("Arial", 8, "italic"),
            fg="#7f8c8d",
            wraplength=440,
            justify="left"
        )
        startup_hint.pack(anchor="w", padx=40)

        # Đăng ký hotkey thoát khẩn cấp
        keyboard.add_hotkey('ctrl+alt+q', self.emergency_exit)
        
        # Xử lý khi đóng cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def add_key(self):
        key = self.key_var.get().strip().lower()
        if not key:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một phím!")
            return

        if key in self.blocked_keys:
            messagebox.showinfo("Thông báo", f"Phím '{key}' đã có trong danh sách!")
            return

        self.blocked_keys[key] = None
        self.key_listbox.insert(tk.END, f"  🔒  {key.upper()}")
        self.save_current_settings()
    
    def add_custom_key(self):
        key = self.custom_key.get().strip().lower()
        if not key:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên phím!")
            return

        if key in self.blocked_keys:
            messagebox.showinfo("Thông báo", f"Phím '{key}' đã có trong danh sách!")
            return

        self.blocked_keys[key] = None
        self.key_listbox.insert(tk.END, f"  🔒  {key.upper()}")
        self.custom_key.delete(0, tk.END)
        self.save_current_settings()
    
    def remove_key(self):
        selection = self.key_listbox.curselection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phím cần xóa!")
            return
        
        index = selection[0]
        item = self.key_listbox.get(index)
        # Lấy tên phím từ chuỗi hiển thị
        key = item.split("🔒")[1].strip().lower()
        
        # Nếu đang block thì gỡ hook trước
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
            messagebox.showwarning("Cảnh báo", "Vui lòng thêm ít nhất một phím để chặn!")
            return
        
        try:
            for key in self.blocked_keys:
                # Block phím bằng cách thêm hotkey trả về False (suppress)
                self.blocked_keys[key] = keyboard.block_key(key)
            
            self.is_blocking = True
            self.toggle_btn.config(
                text="⏸️ DỪNG CHẶN",
                bg="#e74c3c"
            )
            self.status_label.config(
                text="● Trạng thái: ĐANG CHẶN PHÍM",
                fg="#27ae60"
            )
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chặn phím:\n{str(e)}\n\nVui lòng chạy với quyền Administrator!")
    
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
                text="▶️ BẮT ĐẦU CHẶN",
                bg="#27ae60"
            )
            self.status_label.config(
                text="● Trạng thái: Đang dừng",
                fg="#e74c3c"
            )
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi dừng:\n{str(e)}")
    
    def toggle_startup(self):
        """Bật/tắt tự động khởi động cùng Windows"""
        if self.startup_var.get():
            if enable_startup():
                messagebox.showinfo(
                    "Thành công",
                    "Đã bật tự động khởi động cùng Windows!\n\n"
                    "Đã tạo Scheduled Task chạy với quyền cao nhất, "
                    "nên sẽ KHÔNG cần xác nhận UAC mỗi lần đăng nhập."
                )
            else:
                messagebox.showerror(
                    "Lỗi",
                    "Không thể tạo Scheduled Task.\n"
                    "Vui lòng chạy chương trình với quyền Administrator và thử lại."
                )
                self.startup_var.set(False)
        else:
            if disable_startup():
                messagebox.showinfo(
                    "Thành công",
                    "Đã tắt tự động khởi động."
                )
            else:
                messagebox.showerror(
                    "Lỗi",
                    "Không thể xoá Scheduled Task."
                )
                self.startup_var.set(True)

    def load_saved_settings(self):
        """Tải cài đặt đã lưu và khôi phục danh sách phím"""
        settings = load_settings()

        for key in settings.get("blocked_keys", []):
            if key and key not in self.blocked_keys:
                self.blocked_keys[key] = None
                self.key_listbox.insert(tk.END, f"  🔒  {key.upper()}")

        # Silent mode (auto-start cùng Windows): ẩn cửa sổ + tự chặn ngay
        if self.silent_mode:
            self.root.withdraw()
            if self.blocked_keys:
                self.root.after(500, self.start_blocking)

    def save_current_settings(self):
        """Lưu cài đặt hiện tại"""
        save_settings(list(self.blocked_keys.keys()))

    def create_tray_image(self):
        """Tạo icon cho system tray"""
        # Tạo icon 64x64 với ký hiệu khóa
        image = Image.new('RGB', (64, 64), color='#2c3e50')
        dc = ImageDraw.Draw(image)

        # Vẽ biểu tượng khóa đơn giản
        # Thân khóa
        dc.rectangle([20, 35, 44, 55], fill='#ecf0f1', outline='#ecf0f1')
        # Móc khóa
        dc.arc([24, 20, 40, 40], start=180, end=0, fill='#ecf0f1', width=4)
        # Lỗ khóa
        dc.ellipse([29, 42, 35, 48], fill='#2c3e50')

        return image

    def setup_tray_icon(self):
        """Thiết lập system tray icon"""
        if not HAS_PYSTRAY:
            return

        try:
            # Tạo menu cho tray icon
            menu = pystray.Menu(
                pystray.MenuItem("Hiển thị", self.show_window, default=True),
                pystray.MenuItem("Bắt đầu chặn", self.tray_start_blocking,
                                visible=lambda item: not self.is_blocking),
                pystray.MenuItem("Dừng chặn", self.tray_stop_blocking,
                                visible=lambda item: self.is_blocking),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Thoát", self.tray_exit)
            )

            # Tạo tray icon
            image = self.create_tray_image()
            self.tray_icon = pystray.Icon(
                "KeyBlocker",
                image,
                f"Key Blocker v{__version__} - Chặn phím",
                menu
            )

            # Chạy tray icon trong thread riêng
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Lỗi khi tạo tray icon: {e}")

    def show_window(self, icon=None, item=None):
        """Hiển thị cửa sổ từ tray"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _poll_wake_signal(self):
        """Mỗi giây kiểm tra wake file; nếu có thì xoá rồi hiện cửa sổ."""
        try:
            wake_path = get_wake_file_path()
            if wake_path.exists():
                wake_path.unlink(missing_ok=True)
                self.show_window()
        except Exception:
            pass
        self.root.after(1000, self._poll_wake_signal)

    def hide_to_tray(self):
        """Ẩn cửa sổ xuống tray"""
        if HAS_PYSTRAY and self.tray_icon:
            # Hiện thông báo lần đầu
            if self.first_hide:
                self.first_hide = False
                messagebox.showinfo(
                    "Chạy nền",
                    "Chương trình đã ẩn xuống system tray!\n\n"
                    "💡 Click phải vào icon 🔒 ở góc dưới bên phải\n"
                    "để hiển thị lại hoặc thoát chương trình."
                )
            self.root.withdraw()
        else:
            self.root.iconify()

    def tray_start_blocking(self, icon=None, item=None):
        """Bắt đầu chặn từ tray menu"""
        self.root.after(0, self.start_blocking)

    def tray_stop_blocking(self, icon=None, item=None):
        """Dừng chặn từ tray menu"""
        self.root.after(0, self.stop_blocking)

    def tray_exit(self, icon=None, item=None):
        """Thoát từ tray menu"""
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.quit_app)

    def emergency_exit(self):
        """Thoát khẩn cấp với Ctrl+Alt+Q"""
        self.stop_blocking()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        sys.exit(0)
    
    def on_close(self):
        """Xử lý khi đóng cửa sổ (nút X) - luôn ẩn xuống tray nếu có thể"""
        self.save_current_settings()

        if HAS_PYSTRAY and self.tray_icon:
            self.hide_to_tray()
        else:
            self.quit_app()

    def quit_app(self):
        """Thoát hẳn ứng dụng"""
        # Lưu cài đặt
        self.save_current_settings()

        # Dừng chặn phím
        if self.is_blocking:
            self.stop_blocking()

        # Dừng tray icon
        if self.tray_icon:
            self.tray_icon.stop()

        # Unhook keyboard
        try:
            keyboard.unhook_all()
        except:
            pass

        self.root.destroy()


def main():
    silent_mode = '--silent' in sys.argv

    # Chống chạy 2 instance — kiểm tra trước khi elevate để tránh popup UAC vô ích.
    # Nếu user double-click EXE trong khi đã có instance chạy ngầm → ra hiệu cho
    # instance đó hiện cửa sổ (thay vì hiện popup "đã đang chạy" gây khó chịu).
    if not acquire_single_instance_lock():
        if not silent_mode:
            signal_existing_instance_to_show()
        sys.exit(0)

    atexit.register(release_single_instance_lock)

    # Yêu cầu quyền admin nếu chưa có
    if not is_admin():
        # Nhả lock để process elevated có thể acquire lại
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
            # Elevation thất bại → re-acquire lock và chạy với quyền hiện tại
            acquire_single_instance_lock()

    migrate_legacy_startup_if_needed()

    root = tk.Tk()
    app = KeyBlockerApp(root, silent_mode=silent_mode)
    root.mainloop()


if __name__ == "__main__":
    main()
