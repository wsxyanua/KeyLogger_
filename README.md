# Keylogger Xyanua

Keylogger được viết bằng Python với các tính năng bảo mật và giám sát nâng cao.

## Tính năng chính

### 1. Ghi lại phím
- Ghi lại tất cả các phím được nhấn
- Hỗ trợ các phím đặc biệt và tổ hợp phím
- Lưu thời gian nhấn phím
- Mã hóa dữ liệu trước khi lưu

### 2. Theo dõi clipboard
- Ghi lại nội dung được copy/paste
- Hỗ trợ text và hình ảnh
- Lưu thời gian thao tác
- Mã hóa dữ liệu clipboard

### 3. Chụp ảnh màn hình
- Tự động chụp ảnh màn hình định kỳ
- Lưu ảnh với timestamp
- Nén ảnh để tiết kiệm dung lượng
- Mã hóa tên file ảnh

### 4. Báo cáo qua email
- Gửi báo cáo định kỳ qua email
- Đính kèm file log và ảnh chụp
- Tùy chỉnh tần suất gửi báo cáo
- Hỗ trợ Gmail SMTP

## Cài đặt

### Yêu cầu hệ thống
- Python 3.10 trở lên
- Linux (đã test trên Ubuntu)
- Các thư viện trong requirements.txt

### Cài đặt dependencies
```bash
# Cài đặt system packages
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 libcairo2-dev pkg-config python3-dev

# Cài đặt Python packages
pip install -r requirements.txt
```

## Sử dụng

### 1. Chạy keylogger
```bash
python keylogger.py
```

### 2. Xem log
```bash
# Xem keylog
python decrypt_log.py

# Xem log ứng dụng
python decrypt_app_log.py
```

### 3. Cấu hình email
1. Tạo file `logs/email_config.json`:
```json
{
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-gmail@gmail.com",
    "sender_password": "your-app-password",
    "receiver_email": "your-gmail@gmail.com",
    "report_interval": 24
}
```

2. Chạy email reporter:
```bash
python email_reporter.py
```

## Cấu trúc thư mục
```
keylogger_xyanua/
├── keylogger.py          # Chương trình chính
├── app_monitor.py        # Theo dõi ứng dụng
├── email_reporter.py     # Gửi báo cáo email
├── decrypt_log.py        # Giải mã file log
├── decrypt_app_log.py    # Giải mã log ứng dụng
├── requirements.txt      # Thư viện cần thiết
├── README.md            # Hướng dẫn sử dụng
└── logs/                # Thư mục chứa log
    ├── keylog.enc      # File log đã mã hóa
    ├── app_usage.enc   # Log ứng dụng đã mã hóa
    ├── config.json     # Cấu hình mã hóa
    ├── email_config.json # Cấu hình email
    └── screenshots/    # Ảnh chụp màn hình
```

## Bảo mật
- Mã hóa dữ liệu với Fernet
- Bảo vệ file cấu hình
- Xác thực email
- Lưu trữ an toàn

## Lưu ý quan trọng
1. Chỉ sử dụng cho mục đích hợp pháp
2. Cần quyền root để chạy một số tính năng
3. Đảm bảo bảo mật file cấu hình
4. Sao lưu key mã hóa

## Hỗ trợ
Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log lỗi
2. Xác nhận đã cài đặt đầy đủ dependencies
3. Kiểm tra quyền truy cập thư mục
4. Xác nhận cấu hình email đúng 