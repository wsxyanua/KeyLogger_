import os
import json
import base64
from cryptography.fernet import Fernet

def decrypt_logs():
    # Đường dẫn đến các file
    log_dir = "logs"
    encrypted_log = os.path.join(log_dir, "keylog.txt")
    config_file = os.path.join(log_dir, "config.json")
    decrypted_log = os.path.join(log_dir, "decrypted_keylog.txt")
    
    try:
        # Đọc key mã hóa từ file config
        if not os.path.exists(config_file):
            print("Không tìm thấy file config.json")
            return
            
        with open(config_file, 'rb') as f:
            config = json.load(f)
            encryption_key = base64.b64decode(config['key'])
            
        # Khởi tạo Fernet với key
        cipher_suite = Fernet(encryption_key)
        
        # Đọc và giải mã log
        print("Đang giải mã log...")
        with open(encrypted_log, 'rb') as f:
            encrypted_data = f.read()
            
        # Giải mã từng dòng
        decrypted_lines = []
        for line in encrypted_data.split(b'\n'):
            if line:  # Bỏ qua dòng trống
                try:
                    decrypted_line = cipher_suite.decrypt(line)
                    decrypted_lines.append(decrypted_line.decode('utf-8'))
                except Exception as e:
                    print(f"Lỗi khi giải mã dòng: {e}")
        
        # Lưu log đã giải mã
        with open(decrypted_log, 'w', encoding='utf-8') as f:
            f.write('\n'.join(decrypted_lines))
            
        print(f"Đã giải mã xong. Log đã được lưu tại: {decrypted_log}")
        
    except Exception as e:
        print(f"Lỗi khi giải mã: {e}")

if __name__ == "__main__":
    decrypt_logs() 