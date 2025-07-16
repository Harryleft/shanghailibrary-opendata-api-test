"""
配置模块 - 集中管理所有配置常量
"""
import os

# API配置
# 需要向上海图书馆申请API密钥
# 会首先检查环境变量中是否设置了API密钥，如果没有设置，则可以在第二个参数中自定义输入
API_KEY = os.getenv('SHANGHAI_LIBRARY_API_KEY', "")

# 输出配置
OUTPUT_DIR = "api_results"
ERROR_LOG_FILE = "log/error_log.json"

# HTTP配置
BASE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
REQUEST_DELAY_SECONDS = 2

# 终端颜色配置
class Colors:
    SUCCESS = '\033[92m'  # Green
    WARNING = '\033[93m'  # Yellow
    FAIL = '\033[91m'  # Red
    INFO = '\033[94m'  # Blue
    ENDC = '\033[0m'  # Reset
