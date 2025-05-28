import psutil
import time
from datetime import datetime
import json
import os
from cryptography.fernet import Fernet
import base64

class AppMonitor:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.app_log_file = os.path.join(log_dir, "app_usage.json")
        self.encrypted_log_file = os.path.join(log_dir, "app_usage.enc")
        self.config_file = os.path.join(log_dir, "config.json")
        self.running = True
        self.app_usage = {}
        self.last_check = {}
        
        # Đảm bảo thư mục log tồn tại
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Khởi tạo mã hóa
        self.init_encryption()
        
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
        except Exception as e:
            print(f"Lỗi khi khởi tạo mã hóa: {e}")
            raise
            
    def get_active_window(self):
        """Lấy thông tin cửa sổ đang active"""
        try:
            # Sử dụng xdotool để lấy thông tin cửa sổ active
            process = subprocess.Popen(['xdotool', 'getactivewindow', 'getwindowname'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            if not error:
                return output.decode('utf-8').strip()
        except:
            pass
        return "Unknown"
        
    def get_process_info(self):
        """Lấy thông tin về các process đang chạy"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'create_time']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'username': pinfo['username'],
                    'create_time': datetime.fromtimestamp(pinfo['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes
        
    def update_usage(self):
        """Cập nhật thời gian sử dụng ứng dụng"""
        current_time = time.time()
        active_window = self.get_active_window()
        
        if active_window in self.last_check:
            duration = current_time - self.last_check[active_window]
            if active_window in self.app_usage:
                self.app_usage[active_window] += duration
            else:
                self.app_usage[active_window] = duration
                
        self.last_check[active_window] = current_time
        
    def save_usage(self):
        """Lưu thông tin sử dụng đã mã hóa"""
        try:
            data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'app_usage': self.app_usage,
                'processes': self.get_process_info()
            }
            
            # Mã hóa dữ liệu
            encrypted_data = self.cipher_suite.encrypt(json.dumps(data).encode())
            
            # Lưu vào file
            with open(self.encrypted_log_file, 'ab') as f:
                f.write(encrypted_data + b'\n')
                
            # Reset usage data
            self.app_usage = {}
            self.last_check = {}
            
        except Exception as e:
            print(f"Lỗi khi lưu thông tin sử dụng: {e}")
            
    def start_monitoring(self, interval=60):
        """Bắt đầu giám sát với khoảng thời gian cập nhật"""
        print(f"Bắt đầu giám sát ứng dụng. Cập nhật mỗi {interval} giây.")
        try:
            while self.running:
                self.update_usage()
                time.sleep(1)  # Cập nhật mỗi giây
                
                # Lưu dữ liệu mỗi interval giây
                if int(time.time()) % interval == 0:
                    self.save_usage()
                    
        except KeyboardInterrupt:
            print("\nDừng giám sát ứng dụng...")
            self.save_usage()
        except Exception as e:
            print(f"Lỗi không mong muốn: {e}")
        finally:
            self.save_usage()
            
    def stop_monitoring(self):
        """Dừng giám sát"""
        self.running = False 