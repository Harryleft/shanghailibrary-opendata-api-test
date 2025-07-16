"""
API客户端模块 - 处理HTTP请求和响应
"""
import requests
import time
import json
from datetime import datetime
from config import BASE_HEADERS, REQUEST_DELAY_SECONDS, OUTPUT_DIR, Colors, ERROR_LOG_FILE
from utils import sanitize_filename, ensure_directory_exists, format_response_size, log_error_to_json


class APIClient:
    """API客户端类，负责发送请求和处理响应"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(BASE_HEADERS)

    def make_request(self, endpoint_def):
        """
        根据端点定义发送HTTP请求

        Args:
            endpoint_def: API端点定义字���

        Returns:
            tuple: (success, response_data, status_code, error_message)
        """
        try:
            method = endpoint_def.get("method", "GET").upper()
            url = endpoint_def["url"]
            params = endpoint_def.get("params", {})
            json_data = endpoint_def.get("json_data", {})
            expect_json = endpoint_def.get("expect_json", True)

            # 发送请求
            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                if json_data:
                    response = self.session.post(url, json=json_data, params=params, timeout=30)
                else:
                    response = self.session.post(url, params=params, timeout=30)
            else:
                return False, None, None, f"不支持的HTTP方法: {method}"

            # 处理响应
            if expect_json:
                try:
                    data = response.json()
                    return True, data, response.status_code, None
                except json.JSONDecodeError:
                    return False, response.text, response.status_code, "响应不是有效的JSON"
            else:
                return True, response.content, response.status_code, None

        except requests.exceptions.RequestException as e:
            return False, None, None, str(e)

    def save_response(self, endpoint_name, data, file_ext=".json"):
        """
        保存响应数据到文件

        Args:
            endpoint_name: 端点名称
            data: 响应数据
            file_ext: 文件扩展名
        """
        ensure_directory_exists(OUTPUT_DIR)

        filename = sanitize_filename(endpoint_name) + file_ext
        filepath = f"{OUTPUT_DIR}/{filename}"

        try:
            if file_ext == ".json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                with open(filepath, 'wb') as f:
                    f.write(data)
            return filepath
        except Exception as e:
            print(f"{Colors.FAIL}保存文件失败: {e}{Colors.ENDC}")
            return None


def run_api_test(endpoint_def):
    """
    运行单个API测试

    Args:
        endpoint_def: API端点定义

    Returns:
        dict: 测试结果
    """
    client = APIClient()
    name = endpoint_def["name"]

    print(f"{Colors.INFO}测试: {name}{Colors.ENDC}")

    # 发送请求
    success, data, status_code, error = client.make_request(endpoint_def)

    result = {
        "name": name,
        "success": success,
        "status_code": status_code,
        "error": error,
        "data_size": 0,
        "saved_file": None
    }

    if success:
        # 计算数据大小
        result["data_size"] = len(str(data)) if data else 0

        # 保存响应
        file_ext = endpoint_def.get("file_ext", ".json")
        saved_file = client.save_response(name, data, file_ext)
        result["saved_file"] = saved_file

        # 显示成功信息
        size_info = format_response_size(data)
        print(f"{Colors.SUCCESS}✓ 成功 (状态码: {status_code}, 大小: {size_info}){Colors.ENDC}")

        if saved_file:
            print(f"  保存到: {saved_file}")
    else:
        # 显示错误信息
        print(f"{Colors.FAIL}✗ 失败 (状态码: {status_code}){Colors.ENDC}")
        if error:
            print(f"  错误: {error}")

        # 记录错误到JSON文件
        error_log_entry = {
            "timestamp": datetime.now().isoformat(),
            "api_name": name,
            "url": endpoint_def.get("url"),
            "status_code": status_code,
            "error_message": error,
            "response_body": data if isinstance(data, str) else "N/A"
        }
        log_error_to_json(error_log_entry, ERROR_LOG_FILE)

    # 请求间延时
    time.sleep(REQUEST_DELAY_SECONDS)

    return result
