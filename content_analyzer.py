import re
import json
from collections import Counter
from datetime import datetime
from typing import Dict, List, Set
import os

class ContentAnalyzer:
    def __init__(self):
        self.sensitive_patterns = {
            'password': r'(?i)(password|passwd|pwd)[\s]*[:=]\s*[\w@#$%^&*]+',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'credit_card': r'\b(?:\d[ -]*?){13,19}\b',
            'phone': r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'url': r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',
            'api_key': r'(?i)(api[_-]?key|apikey)[\s]*[:=]\s*[\w-]+',
            'token': r'(?i)(token|access_token)[\s]*[:=]\s*[\w-]+'
        }
        
        self.keyword_stats = Counter()
        self.clipboard_history = []
        self.sensitive_data_found = set()
        
        # Tạo thư mục logs nếu chưa tồn tại
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # File để lưu thống kê
        self.stats_file = 'logs/content_analysis.json'
        self.load_stats()

    def load_stats(self):
        """Load thống kê từ file nếu tồn tại"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.keyword_stats = Counter(data.get('keywords', {}))
                    self.sensitive_data_found = set(data.get('sensitive_data', []))
            except:
                pass

    def save_stats(self):
        """Lưu thống kê vào file"""
        data = {
            'keywords': dict(self.keyword_stats),
            'sensitive_data': list(self.sensitive_data_found),
            'last_updated': datetime.now().isoformat()
        }
        with open(self.stats_file, 'w') as f:
            json.dump(data, f, indent=4)

    def analyze_text(self, text: str) -> Dict:
        """Phân tích văn bản để tìm thông tin nhạy cảm"""
        results = {
            'sensitive_data': [],
            'keywords': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Tìm thông tin nhạy cảm
        for data_type, pattern in self.sensitive_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                sensitive_item = {
                    'type': data_type,
                    'value': match.group(),
                    'position': match.span()
                }
                results['sensitive_data'].append(sensitive_item)
                self.sensitive_data_found.add(f"{data_type}: {match.group()}")
        
        # Phân tích từ khóa
        words = re.findall(r'\b\w+\b', text.lower())
        self.keyword_stats.update(words)
        
        # Lấy top 10 từ khóa phổ biến
        results['keywords'] = [word for word, _ in self.keyword_stats.most_common(10)]
        
        # Lưu thống kê
        self.save_stats()
        
        return results

    def analyze_clipboard(self, content: str) -> Dict:
        """Phân tích nội dung clipboard"""
        # Thêm vào lịch sử clipboard
        self.clipboard_history.append({
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Giới hạn lịch sử clipboard
        if len(self.clipboard_history) > 100:
            self.clipboard_history = self.clipboard_history[-100:]
        
        # Phân tích nội dung
        return self.analyze_text(content)

    def get_keyword_stats(self, limit: int = 10) -> List[tuple]:
        """Lấy thống kê từ khóa"""
        return self.keyword_stats.most_common(limit)

    def get_sensitive_data_stats(self) -> List[str]:
        """Lấy thống kê thông tin nhạy cảm"""
        return list(self.sensitive_data_found)

    def get_clipboard_history(self, limit: int = 10) -> List[Dict]:
        """Lấy lịch sử clipboard gần đây"""
        return self.clipboard_history[-limit:]

    def clear_stats(self):
        """Xóa thống kê"""
        self.keyword_stats.clear()
        self.sensitive_data_found.clear()
        self.clipboard_history.clear()
        self.save_stats() 