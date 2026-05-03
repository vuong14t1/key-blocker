# KEY BLOCKER - Hướng dẫn Build và Cài đặt

## 📋 Yêu cầu

- Windows 10/11
- Python 3.8 trở lên
- Pip (đi kèm với Python)

## 🔧 Cách Build thành file .EXE

### Bước 1: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 2: Build file .exe

Chạy file `build.bat`:

```bash
build.bat
```

Hoặc build thủ công:

```bash
python -m PyInstaller --clean KeyBlocker.spec
```

### Bước 3: Lấy file .exe

Sau khi build thành công, file `KeyBlocker.exe` sẽ nằm trong thư mục `dist/`

```
dist/
└── KeyBlocker.exe  ← File này (~19 MB)
```

File .exe đã được nhúng manifest `uac_admin=True`, sẽ tự xin quyền Administrator khi chạy.

## 📦 Cách cài đặt

### Cách 1: Chạy trực tiếp
- Double-click vào `KeyBlocker.exe`
- Chương trình sẽ tự động yêu cầu quyền Administrator (UAC popup)

### Cách 2: Copy vào Program Files
1. Copy file `KeyBlocker.exe` vào `C:\Program Files\KeyBlocker\`
2. Tạo shortcut trên Desktop nếu cần

## 🚀 Cách sử dụng

### Chặn phím

1. **Chọn phím từ dropdown** hoặc **nhập tên phím** (ví dụ: `windows`, `alt`, `` ` ``)
2. Click **➕ Thêm** để thêm vào danh sách
3. Click **▶️ BẮT ĐẦU CHẶN** để kích hoạt

### Bỏ chặn phím

1. Click vào phím trong danh sách
2. Click **🗑️ Xóa phím đã chọn**

### 🎯 System Tray (chạy nền)

- Chương trình hiển thị **icon 🔒 ở system tray** (góc dưới bên phải taskbar)
- **Click phải vào icon** để: hiển thị cửa sổ, bắt đầu/dừng chặn, hoặc thoát
- Đóng cửa sổ (nút X) → tự động ẩn xuống tray (chương trình vẫn chạy nền)

### ✅ Lưu cài đặt tự động

- Danh sách phím đã chọn **tự động lưu** mỗi khi bạn thêm/xóa phím
- File cấu hình: `%LOCALAPPDATA%\KeyBlocker\settings.json`
- Mở lại chương trình → danh sách phím **tự động khôi phục**

### 🚀 Tự động khởi động cùng Windows

Tick vào checkbox **"🚀 Tự động khởi động cùng Windows (chạy nền + tự chặn)"**

Khi bật, mỗi lần Windows khởi động:
- ✨ Chương trình tự chạy ngầm dưới system tray (không hiện cửa sổ)
- ✨ Tự động bật chặn các phím đã lưu
- ✨ **KHÔNG cần** xác nhận UAC mỗi lần đăng nhập

Cơ chế: tạo Scheduled Task `KeyBlocker` (trigger `ONLOGON`, `/RL HIGHEST`) chạy lệnh có flag `--silent`. Vì Task Scheduler hỗ trợ "Run with highest privileges" nên process được elevated trực tiếp mà không cần UAC popup — đây là lý do phải dùng Task Scheduler thay cho Run registry key (Run key không tự nâng quyền, app yêu cầu admin sẽ bị Windows chặn ở silent mode).

Phiên bản cũ dùng Run key sẽ được tự động migrate sang Scheduled Task ở lần đầu chạy app phiên bản mới.

### 🔒 Chống chạy 2 instance

Chương trình tự kiểm tra qua lock file `%LOCALAPPDATA%\KeyBlocker\instance.lock`:
- Lần 2 mở thủ công → ghi wake file `instance.wake`, instance đang chạy phát hiện rồi tự hiện cửa sổ (instance 2 thoát im lặng — không có popup)
- Lần 2 từ silent mode → thoát im lặng
- Nếu instance trước crash → lock file stale tự động được dọn ở lần chạy kế tiếp (kiểm tra PID còn sống)

**Lưu ý khi build/test:** sau khi build EXE mới, nếu bản cũ vẫn đang chạy ngầm, double-click EXE mới sẽ chỉ làm bản cũ hiện UI lên (không spawn bản mới). Click chuột phải tray icon → **Thoát** rồi chạy lại EXE mới.

### 🆘 Thoát khẩn cấp

Nhấn **Ctrl + Alt + Q** để tắt chặn và thoát chương trình ngay lập tức (kể cả khi đang ẩn tray).

## 📝 Các phím có thể chặn

- Phím hệ thống: `windows`, `alt`, `ctrl`, `shift`, `tab`, `esc`, `caps lock`
- Phím chức năng: `f1`-`f12`
- Phím chữ: `a`-`z`
- Phím số: `0`-`9`
- Phím đặc biệt: `` ` ``, `~`, `-`, `=`, `[`, `]`, `\`, `;`, `'`, `,`, `.`, `/`
- Phím điều hướng: `up`, `down`, `left`, `right`, `home`, `end`, `page up`, `page down`
- Khác: `space`, `enter`, `backspace`, `delete`, `insert`, `print screen`

## ⚙️ Cấu trúc Project

```
key_blocker/
├── key_blocker.py          # Source code chính
├── KeyBlocker.spec         # PyInstaller specification
├── build.bat               # Build script tự động
├── run_key_blocker.bat     # Chạy từ source (không cần build)
├── requirements.txt        # Python dependencies
├── BUILD_INSTRUCTIONS.md   # File này
├── HUONG_DAN.md            # Hướng dẫn cho người dùng cuối
│
├── build/                  # Thư mục build tạm (tự động tạo, gitignored)
└── dist/                   # Thư mục chứa file .exe (tự động tạo)
    └── KeyBlocker.exe
```

## 🐛 Xử lý lỗi

### Lỗi: "Không thể chặn phím"
- ✅ Phải chạy với quyền Administrator (file .exe đã tự xin UAC, source mode cần dùng `run_key_blocker.bat`)
- ✅ Một số phần mềm chống virus có thể chặn keyboard hook → tạm tắt rồi thử lại

### Lỗi: "Module 'keyboard' not found"
```bash
pip install -r requirements.txt
```

### Lỗi: `'pyinstaller' is not recognized`
PyInstaller được cài qua pip nhưng `Scripts/` chưa nằm trong PATH. Dùng:
```bash
python -m PyInstaller --clean KeyBlocker.spec
```

### Lỗi khi build (PYZ/EXE corrupted)
- Xóa thư mục `build/` và `dist/`
- Chạy lại `build.bat`

### Chương trình không tự khởi động cùng Windows
- Vào UI tick lại checkbox "🚀 Tự động khởi động cùng Windows"
- Kiểm tra Scheduled Task: PowerShell `Get-ScheduledTask -TaskName KeyBlocker` phải tồn tại với State `Ready`
- Hoặc xem ở **Task Scheduler** (`taskschd.msc`) → tìm task tên `KeyBlocker`

## 📄 License

Tác giả: Vuong  
Free to use - Educational purpose

## ⚠️ Lưu ý

- Cần quyền Administrator để chặn phím hệ thống
- Luôn nhớ phím tắt khẩn cấp: **Ctrl + Alt + Q**
- Không nên chặn tất cả các phím cùng lúc (sẽ không thể điều khiển máy)
- Sử dụng có trách nhiệm
