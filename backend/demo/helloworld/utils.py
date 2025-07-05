import os
import json
from datetime import datetime

def read_config(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def write_log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    return log_entry

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

class FileHandler:
    def __init__(self, base_path):
        self.base_path = base_path
    
    def read_file(self, filename):
        filepath = os.path.join(self.base_path, filename)
        with open(filepath, 'r') as f:
            return f.read()
    
    def write_file(self, filename, content):
        filepath = os.path.join(self.base_path, filename)
        with open(filepath, 'w') as f:
            f.write(content)