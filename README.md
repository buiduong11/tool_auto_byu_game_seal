# Tool Auto Buy - Proxy Automation

Tool tự động lấy proxy US từ 9proxy và tạo profile Multilogin với proxy đó.

## Cài đặt

1. Cài đặt Python packages cần thiết:
```bash
pip install -r requirements.txt
```

2. Tạo file `.env` trong thư mục gốc với các thông tin sau:
```
NINEPROXY_API_KEY=your_api_key_here  # Khi có API key của 9proxy
MULTILOGIN_FOLDER_ID=your_folder_id  # Optional: ID folder trong Multilogin để lưu profile
```

## Cách sử dụng

1. Đảm bảo Multilogin đã được cài đặt và đang chạy trên máy
2. Chạy script:
```bash
python main.py
```

Script sẽ:
1. Lấy một proxy US từ 9proxy
2. Tạo profile mới trên Multilogin với proxy đó
3. Start profile và kiểm tra proxy có hoạt động không
4. Trả về kết quả trong terminal

## Troubleshooting

1. Nếu gặp lỗi "Import không tìm thấy":
```bash
pip install -r requirements.txt
```

2. Nếu Multilogin không phản hồi:
- Kiểm tra Multilogin đã chạy chưa
- Kiểm tra ports 35000 và 45000 có đang được mở không

3. Nếu proxy không hoạt động:
- Kiểm tra IP có thuộc US không
- Kiểm tra proxy có yêu cầu authentication không
- Thử proxy khác

## Cấu hình

Bạn có thể điều chỉnh các cấu hình trong file `config.py`:
- MULTILOGIN_LOCAL_API: API endpoint của Multilogin local (mặc định: http://127.0.0.1:35000)
- MULTILOGIN_LAUNCHER_API: API endpoint của Multilogin launcher (mặc định: http://127.0.0.1:45000/api/v2)# tool_auto_byu_game_seal
