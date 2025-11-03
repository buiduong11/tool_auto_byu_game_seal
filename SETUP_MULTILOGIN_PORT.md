# Hướng dẫn cấu hình Multilogin Automation Port

## Bước 1: Mở file app.properties

1. Mở Multilogin app
2. Vào menu → **"Tài khoản của tôi"** (My Account)
3. Click **"Mở thư mục nhật ký"** (Open logs folder)
4. Điều hướng lên 1 cấp đến thư mục `/.multiloginapp.com`

Hoặc truy cập trực tiếp:
- **macOS**: `/Users/mac/.multiloginapp.com`
- **Windows**: `C:\Users\%username%\.multiloginapp.com`
- **Linux**: `/home/%username%/.multiloginapp.com`

**Lưu ý**: Thư mục có thể bị ẩn. Trên Mac:
- `Cmd + Shift + H` - hiển thị thư mục user
- `Cmd + Shift + .` - hiển thị file/folder ẩn

## Bước 2: Chỉnh sửa app.properties

1. Mở file `app.properties` bằng text editor
2. Thêm dòng này:
   ```
   multiloginapp.port=35000
   ```
3. Lưu file

## Bước 3: Restart Multilogin

1. Đóng hoàn toàn Multilogin app
2. Mở lại Multilogin

## Bước 4: Kiểm tra

Sau khi restart, Multilogin sẽ lắng nghe trên port 35000 cho automation API.

Bạn có thể kiểm tra bằng lệnh:
```bash
lsof -iTCP -sTCP:LISTEN -n -P | grep 35000
```

## Sau khi config xong

Chạy lại workflow:
```bash
python auto_workflow.py
```

Lúc này API sẽ trả về WebSocket endpoint với port để Selenium kết nối.
