# Key Blocker

Phần mềm chặn phím đơn giản cho Windows. Giao diện Tkinter, chạy ngầm dưới system tray, hỗ trợ tự khởi động cùng Windows mà không cần UAC popup.

## Tính năng

- Chặn phím tuỳ chọn: phím Windows, Alt, Ctrl, Shift, F1-F12, Caps Lock, ký tự, ...
- Lưu danh sách phím tự động (`%LOCALAPPDATA%\KeyBlocker\settings.json`)
- Chạy ngầm dưới system tray (icon 🔒)
- Tự khởi động cùng Windows qua **Scheduled Task** chạy quyền cao nhất → không bị UAC chặn ở chế độ silent
- Single-instance: double-click lần 2 sẽ đưa cửa sổ đang chạy hiện lên thay vì spawn bản mới
- Hotkey thoát khẩn cấp: **Ctrl + Alt + Q**

## Yêu cầu

- Windows 10/11
- Python 3.8+ (nếu chạy từ source)
- Quyền Administrator (để chặn phím hệ thống như `windows`, `ctrl`, `alt`)

## Chạy từ source

```bash
pip install -r requirements.txt
```

Click chuột phải `run_key_blocker.bat` → **Run as administrator**, hoặc:

```bash
python key_blocker.py
```

## Build file .exe

```bash
build.bat
```

File `KeyBlocker.exe` (~19 MB) sẽ nằm trong `dist/`. Manifest đã nhúng `uac_admin=True` nên tự xin quyền Admin khi double-click.

## Cách dùng

1. Chọn phím trong combobox hoặc nhập tay → bấm **➕ Thêm**
2. Bấm **▶️ BẮT ĐẦU CHẶN**
3. Đóng cửa sổ (X) → ẩn xuống tray, vẫn chạy nền
4. Click phải tray icon 🔒 để mở lại / dừng / thoát

Tick **🚀 Tự động khởi động cùng Windows** để Key Blocker tự chạy ẩn và bật chặn ngay khi đăng nhập.

## Tài liệu chi tiết

- [HUONG_DAN.md](HUONG_DAN.md) — Hướng dẫn cho người dùng cuối
- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) — Hướng dẫn build, kiến trúc, xử lý lỗi

## License

Free to use - Educational purpose. Tác giả: Vuong.
