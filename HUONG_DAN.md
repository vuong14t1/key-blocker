# 🔒 Key Blocker - Phần mềm chặn phím cho Windows

Phần mềm đơn giản giúp bạn chặn các phím không mong muốn trên Windows. Hữu ích khi:
- Chặn phím Windows khi đang chơi game
- Khóa phím để tránh trẻ em nhấn linh tinh
- Vô hiệu hóa phím Caps Lock, Insert gây phiền
- Chặn các phím F1-F12 trong một số ứng dụng

## 📋 Yêu cầu hệ thống

- Windows 7/8/10/11
- Python 3.7 trở lên ([Tải tại đây](https://www.python.org/downloads/))
- Quyền Administrator (để chặn phím hệ thống)

## 🚀 Cách cài đặt

### Bước 1: Cài Python
Tải và cài Python từ https://www.python.org/downloads/  
**Quan trọng:** Tích vào ô **"Add Python to PATH"** khi cài.

### Bước 2: Cài thư viện keyboard
Mở Command Prompt và chạy:
```bash
pip install keyboard
```

### Bước 3: Chạy chương trình
**Cách 1 (Khuyên dùng):** Click chuột phải vào `run_key_blocker.bat` → chọn **Run as administrator**

**Cách 2:** Mở CMD với quyền Admin, sau đó chạy:
```bash
python key_blocker.py
```

## 🎯 Cách sử dụng

1. **Thêm phím cần chặn:**
   - Chọn từ danh sách có sẵn → bấm **➕ Thêm**
   - Hoặc nhập tên phím tùy ý vào ô bên dưới → bấm **➕ Thêm**

2. **Bắt đầu chặn:** Bấm nút **▶️ BẮT ĐẦU CHẶN**

3. **Dừng chặn:** Bấm nút **⏸️ DỪNG CHẶN**

4. **Xóa phím:** Chọn phím trong danh sách → bấm **🗑️ Xóa phím đã chọn**

5. **Đóng cửa sổ:** Bấm X → chương trình ẩn xuống system tray (góc dưới bên phải, icon 🔒). Click chuột phải vào icon để hiển thị lại hoặc thoát hẳn.

## 🚀 Chạy ngầm cùng Windows

Tick vào checkbox **"🚀 Tự động khởi động cùng Windows (chạy nền + tự chặn)"**.

Khi bật:
- Tạo Scheduled Task `KeyBlocker` chạy với quyền cao nhất khi user đăng nhập
- Mỗi lần Windows khởi động → chương trình tự chạy ẩn dưới tray, tự bật chặn phím
- **Không cần** xác nhận UAC mỗi lần đăng nhập (khác với Run registry key)

Khi tắt: bỏ tick → Scheduled Task tự xoá.

> Lưu ý: lần đầu bật phải đang chạy app với quyền Administrator để tạo được Task.

## 🔒 Chỉ một instance tại 1 thời điểm

Chương trình tự chống chạy 2 bản cùng lúc. Nếu double-click EXE khi đã có bản chạy ngầm → bản đang chạy sẽ tự **hiện cửa sổ lên** (instance thứ 2 thoát im lặng).

Muốn chạy bản EXE mới sau khi build: click chuột phải tray icon 🔒 → **Thoát**, sau đó mở EXE mới.

## ⌨️ Tên các phím phổ biến

| Phím | Tên trong chương trình |
|------|------------------------|
| Phím Windows | `windows` |
| Alt | `alt` |
| Ctrl | `ctrl` |
| Shift | `shift` |
| Caps Lock | `caps lock` |
| Tab | `tab` |
| Esc | `esc` |
| Enter | `enter` |
| Space (cách) | `space` |
| Backspace | `backspace` |
| Delete | `delete` |
| Mũi tên | `up`, `down`, `left`, `right` |
| F1-F12 | `f1`, `f2`, ..., `f12` |
| Print Screen | `print screen` |

## 🆘 Thoát khẩn cấp

Nhấn **Ctrl + Alt + Q** để thoát chương trình ngay lập tức (kể cả khi đang chặn phím).

## ⚠️ Lưu ý quan trọng

- **Phải chạy với quyền Administrator** mới chặn được phím hệ thống như `Windows`, `Ctrl`, `Alt`
- Không chặn tất cả các phím cùng lúc → bạn sẽ không thể điều khiển máy
- Luôn nhớ tổ hợp **Ctrl+Alt+Q** để thoát khẩn cấp
- Khi tắt chương trình, tất cả phím sẽ tự động được mở lại

## 🐛 Khắc phục sự cố

**Lỗi "ImportError: No module named 'keyboard'":**
```bash
pip install keyboard
```

**Lỗi không chặn được phím Windows:**
→ Phải chạy bằng quyền Administrator

**Phím vẫn hoạt động sau khi bấm "Bắt đầu chặn":**
→ Đóng chương trình, click chuột phải file `.bat` → Run as administrator

## 📝 Giấy phép

Phần mềm miễn phí - sử dụng cho mục đích cá nhân.
