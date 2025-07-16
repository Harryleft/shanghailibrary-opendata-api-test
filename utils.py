"""
工具模块 - 通用工具函数
"""
import re
import os
import json


def sanitize_filename(name):
    """
    清理文件名，移除不合法字符
    """
    # 移除或替换不合法的文件名字符
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # 移除前后空格
    name = name.strip()
    # 限制文件名长度
    if len(name) > 200:
        name = name[:200]
    return name


def ensure_directory_exists(directory):
    """
    确保目录存在，如果不存在则创建
    """
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def format_response_size(content):
    """
    格式化响应大小显示
    """
    if isinstance(content, bytes):
        size = len(content)
    elif isinstance(content, str):
        size = len(content.encode('utf-8'))
    else:
        size = len(str(content))

    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"

def log_error_to_json(error_data, log_file):
    """
    将错误信息记录到JSON日志文件

    Args:
        error_data (dict): 包含错误信息的字典
        log_file (str): 日志文件的路径
    """
    ensure_directory_exists(os.path.dirname(log_file))

    try:
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                errors = json.load(f)
        else:
            errors = []
    except (json.JSONDecodeError, FileNotFoundError):
        errors = []

    errors.append(error_data)

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(errors, f, ensure_ascii=False, indent=2)
