# Keylogger Nâng Cao

Một chương trình keylogger được viết bằng Python, có khả năng ghi lại các phím được nhấn, clipboard, chụp ảnh màn hình và theo dõi ứng dụng.

## Tính Năng
- Ghi lại các phím được nhấn với thời gian chính xác
- Theo dõi và lưu nội dung clipboard
- Tự động chụp ảnh màn hình theo khoảng thời gian
- Giám sát thời gian sử dụng các ứng dụng
- Mã hóa tất cả dữ liệu được lưu
- Nhấn phím 'Esc' để dừng ghi log

## Yêu Cầu Hệ Thống
- Python 3.x
- Linux (đã test trên Kali Linux)
- Các thư viện Python được liệt kê trong file requirements.txt
- Các công cụ hệ thống: xdotool, scrot

## Cài Đặt
1. Sao chép repository này về máy
2. Cài đặt các công cụ hệ thống:
```bash
sudo apt install xdotool scrot
```

3. Cài đặt các thư viện Python:
```bash
pip install -r requirements.txt
```

## Cách Sử Dụng
1. Chạy chương trình keylogger:
```bash
python keylogger.py
```

2. Chương trình sẽ:
   - Bắt đầu ghi lại các phím được nhấn
   - Theo dõi clipboard
   - Chụp ảnh màn hình sau mỗi 100 phím
   - Giám sát thời gian sử dụng ứng dụng

3. Nhấn phím 'Esc' để dừng keylogger

4. Xem log:
   - Keylog: `python decrypt_log.py`
   - App usage: `python decrypt_app_log.py`

## Cấu Trúc Thư Mục
```
logs/
├── config.json          # Chứa key mã hóa
├── keylog.txt          # Log bàn phím (đã mã hóa)
├── clipboard.txt       # Log clipboard
├── app_usage.enc       # Log ứng dụng (đã mã hóa)
├── screenshots/        # Thư mục chứa ảnh chụp màn hình
└── decrypted_*.txt     # Các file log đã giải mã
```

## Lưu Ý
- Công cụ này chỉ dành cho mục đích học tập và kiểm thử
- Hãy đảm bảo bạn có quyền hạn phù hợp trước khi sử dụng
- Tất cả dữ liệu được mã hóa để bảo vệ thông tin
- Cần quyền root để theo dõi process
- Cần X server để chụp ảnh màn hình 