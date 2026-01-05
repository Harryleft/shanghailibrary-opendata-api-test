"""
Real-time API monitoring server with WebSocket support
"""
import asyncio
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from flask import Flask, render_template_string, send_from_directory
from flask_sock import Sock
import requests
from threading import Thread, Event
import time

# Handle Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
sock = Sock(app)

# Configuration
API_KEY = os.environ.get('SHANGHAI_LIBRARY_API_KEY', 'YOUR_API_KEY_HERE')
BASE_URL = 'https://data.library.sh.cn/api'
CHECK_INTERVAL = 30  # seconds between API checks
MAX_CONCURRENT_CHECKS = 5

# Global state
api_status: Dict[str, Dict[str, Any]] = {}
initial_check_complete = False
monitoring_active = Event()
monitoring_active.set()
connected_clients = set()


def format_size(size_bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def load_api_definitions():
    """Load API definitions from api_lists.py"""
    try:
        # Import the module directly to get proper context with API_KEY
        import importlib.util
        import sys

        # Set environment variable before importing api_lists
        # so config.py can read it
        os.environ['SHANGHAI_LIBRARY_API_KEY'] = API_KEY

        spec = importlib.util.spec_from_file_location("api_lists", "api_lists.py")
        api_lists = importlib.util.module_from_spec(spec)

        # Inject API_KEY into the module's namespace before execution
        # This ensures the API_KEY is available when api_lists.py is executed
        api_lists.API_KEY = API_KEY

        # Also inject into sys.modules so config.py can use it
        sys.modules['config'] = type('obj', (object,), {'API_KEY': API_KEY})

        spec.loader.exec_module(api_lists)

        # Verify API_KEY was set correctly
        if hasattr(api_lists, 'API_KEY') and api_lists.API_KEY:
            logger.info(f"API_KEY loaded successfully: {api_lists.API_KEY[:10]}...")
        else:
            logger.warning("API_KEY may not be set correctly in api_lists module")

        return api_lists.API_DEFINITIONS
    except Exception as e:
        logger.error(f"Error loading API definitions: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def get_category_from_filename(filename):
    """Extract category from filename"""
    if filename.startswith('[') and ']' in filename:
        return filename.split(']')[0][1:]
    return '其他'


def check_single_api(api_def: Dict[str, Any]) -> Dict[str, Any]:
    """Check a single API endpoint and return status"""
    api_name = api_def.get('name', 'Unknown')
    method = api_def.get('method', 'GET')
    url = api_def.get('url', '')
    category = api_def.get('category', '其他')

    result = {
        'name': api_name,
        'category': category,
        'url': url,
        'method': method,
        'status': 'unknown',
        'response_time': 0,
        'size': 0,
        'timestamp': datetime.now().isoformat(),
        'error': None
    }

    try:
        # Process URL - replace {API_KEY} placeholder if present
        full_url = BASE_URL + url if not url.startswith('http') else url

        # Replace {API_KEY} placeholder in URL
        if '{API_KEY}' in full_url:
            full_url = full_url.replace('{API_KEY}', API_KEY)

        # Fix URLs that have empty key parameter (key= or key=&)
        # This happens when API_KEY was empty when api_lists.py was loaded
        if '?key=' in full_url or '&key=' in full_url:
            import re
            # Replace ?key= or &key= (when followed by & or end of string)
            # Only replace if empty (key=& or key= at end)
            full_url = re.sub(r'([?&])key=(&|$)', r'\1key=' + API_KEY + r'\2', full_url)

        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        start_time = time.time()
        if method.upper() == 'GET':
            # Use params for GET requests
            params = api_def.get('params', {}).copy() if api_def.get('params') else {}

            # Fix empty key in params
            if 'key' in params and params['key'] in ['', None]:
                params['key'] = API_KEY

            response = requests.get(full_url, headers=headers, params=params, timeout=10)
        else:
            # Use json_data for POST requests
            json_data = api_def.get('json_data', {})
            # Replace apiKey in json_data if present
            if json_data and isinstance(json_data, dict):
                json_data_copy = json_data.copy()
                if 'apiKey' in json_data_copy and json_data_copy['apiKey'] in ['', None]:
                    json_data_copy['apiKey'] = API_KEY
            else:
                json_data_copy = json_data
            response = requests.post(full_url, headers=headers, json=json_data_copy, timeout=10)

        result['response_time'] = round((time.time() - start_time) * 1000, 2)
        result['status_code'] = response.status_code

        if response.status_code == 200:
            result['status'] = 'success'
            try:
                data = response.json()
                result['size'] = len(json.dumps(data))
                result['size_formatted'] = format_size(result['size'])
            except:
                result['size'] = len(response.content)
                result['size_formatted'] = format_size(result['size'])
        else:
            result['status'] = 'error'
            # Include response body for debugging
            try:
                response_text = response.text[:200]
                result['error'] = f"HTTP {response.status_code}: {response_text}"
            except:
                result['error'] = f"HTTP {response.status_code}"

    except requests.exceptions.Timeout:
        result['status'] = 'timeout'
        result['error'] = 'Request timeout (>10s)'
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)

    return result


async def check_apis_batch(apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check multiple APIs in batches"""
    results = []
    for i in range(0, len(apis), MAX_CONCURRENT_CHECKS):
        batch = apis[i:i + MAX_CONCURRENT_CHECKS]
        for api in batch:
            result = check_single_api(api)
            results.append(result)
            # Update global state
            key = f"{result['category']}::{result['name']}"
            api_status[key] = result
            # Add delay between individual requests to avoid rate limiting
            await asyncio.sleep(0.5)
        # Delay between batches
        if i + MAX_CONCURRENT_CHECKS < len(apis):
            await asyncio.sleep(2)
    return results


def broadcast_status():
    """Broadcast status to all connected WebSocket clients"""
    if not connected_clients:
        return

    # Prepare summary data
    summary = {
        'type': 'status_update',
        'timestamp': datetime.now().isoformat(),
        'total_apis': len(api_status),
        'success_count': sum(1 for s in api_status.values() if s['status'] == 'success'),
        'error_count': sum(1 for s in api_status.values() if s['status'] in ['error', 'timeout']),
        'categories': {}
    }

    # Count by category
    for status in api_status.values():
        cat = status['category']
        if cat not in summary['categories']:
            summary['categories'][cat] = {'total': 0, 'success': 0, 'error': 0}
        summary['categories'][cat]['total'] += 1
        if status['status'] == 'success':
            summary['categories'][cat]['success'] += 1
        else:
            summary['categories'][cat]['error'] += 1

    # Send to all clients
    message = json.dumps(summary)
    for client in list(connected_clients):
        try:
            client.send(message)
        except:
            connected_clients.remove(client)


async def monitoring_loop():
    """Background loop to continuously monitor APIs"""
    logger.info("Starting real-time monitoring loop...")
    apis = load_api_definitions()
    logger.info(f"Loaded {len(apis)} API definitions for monitoring")

    global initial_check_complete

    while monitoring_active.is_set():
        try:
            logger.info("Checking API status...")
            results = await check_apis_batch(apis)
            logger.info(f"Checked {len(results)} APIs: "
                       f"{sum(1 for r in results if r['status'] == 'success')} success, "
                       f"{sum(1 for r in results if r['status'] in ['error', 'timeout'])} failed")

            # Mark initial check as complete
            initial_check_complete = True
            logger.info("Initial API check complete. Data ready for clients.")

            # Broadcast to connected clients
            broadcast_status()

        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")

        # Wait for next check
        await asyncio.sleep(CHECK_INTERVAL)


def run_monitoring_in_thread():
    """Run the monitoring loop in a separate thread"""
    async def run_loop():
        await monitoring_loop()

    def start_loop():
        asyncio.run(run_loop())

    thread = Thread(target=start_loop, daemon=True)
    thread.start()
    return thread


@app.route('/')
def index():
    """Serve the dashboard HTML"""
    return send_from_directory('web_dashboard', 'realtime_index.html')


@app.route('/data/stats.json')
def get_stats():
    """Serve current statistics as JSON"""
    # Calculate summary
    success_count = sum(1 for s in api_status.values() if s['status'] == 'success')
    error_count = sum(1 for s in api_status.values() if s['status'] in ['error', 'timeout'])

    categories = {}
    for status in api_status.values():
        cat = status['category']
        if cat not in categories:
            categories[cat] = {'count': 0, 'totalSize': 0, 'success': 0, 'error': 0}
        categories[cat]['count'] += 1
        categories[cat]['totalSize'] += status.get('size', 0)
        if status['status'] == 'success':
            categories[cat]['success'] += 1
        else:
            categories[cat]['error'] += 1

    data = {
        'stats': {
            'totalApis': len(api_status),
            'successCount': success_count,
            'errorCount': error_count,
            'successRate': round(success_count / len(api_status) * 100, 1) if api_status else 0,
            'categoryCount': len(categories),
            'totalSize': format_size(sum(s.get('size', 0) for s in api_status.values())),
            'fileCount': success_count,
            'lastUpdate': datetime.now().isoformat()
        },
        'categories': categories,
        'apis': list(api_status.values()),
        'realtime': True
    }
    return data


@app.route('/data/apis')
def get_apis():
    """Get all API statuses"""
    return {'apis': list(api_status.values())}


@sock.route('/ws')
def websocket_connection(ws):
    """Handle WebSocket connections"""
    global initial_check_complete, api_status

    connected_clients.add(ws)
    logger.info(f"Client connected. Total clients: {len(connected_clients)}")

    # Send initial status immediately (even if still loading)
    try:
        success_count = sum(1 for s in api_status.values() if s['status'] == 'success')
        error_count = sum(1 for s in api_status.values() if s['status'] in ['error', 'timeout'])

        initial_data = {
            'type': 'initial',
            'timestamp': datetime.now().isoformat(),
            'total_apis': len(api_status),
            'success_count': success_count,
            'error_count': error_count,
            'apis': list(api_status.values()),
            'loading': not initial_check_complete
        }
        ws.send(json.dumps(initial_data))
        logger.info(f"Sent initial data to client (loading: {not initial_check_complete}, apis: {len(api_status)})")
    except Exception as e:
        logger.error(f"Error sending initial data: {e}")

    try:
        # Keep connection alive and handle incoming messages
        while True:
            message = ws.receive()
            if message is None:
                break
            # Handle client messages if needed
            data = json.loads(message)
            if data.get('type') == 'ping':
                ws.send(json.dumps({'type': 'pong'}))
            elif data.get('type') == 'request_status':
                # Client explicitly requests current status
                try:
                    success_count = sum(1 for s in api_status.values() if s['status'] == 'success')
                    error_count = sum(1 for s in api_status.values() if s['status'] in ['error', 'timeout'])

                    status_data = {
                        'type': 'status_update',
                        'timestamp': datetime.now().isoformat(),
                        'total_apis': len(api_status),
                        'success_count': success_count,
                        'error_count': error_count,
                        'categories': {},
                        'loading': not initial_check_complete
                    }

                    # Add category breakdown
                    for status in api_status.values():
                        cat = status['category']
                        if cat not in status_data['categories']:
                            status_data['categories'][cat] = {'total': 0, 'success': 0, 'error': 0}
                        status_data['categories'][cat]['total'] += 1
                        if status['status'] == 'success':
                            status_data['categories'][cat]['success'] += 1
                        else:
                            status_data['categories'][cat]['error'] += 1

                    ws.send(json.dumps(status_data))
                except Exception as e:
                    logger.error(f"Error sending status update: {e}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(ws)
        logger.info(f"Client disconnected. Total clients: {len(connected_clients)}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("上海图书馆开放数据API - 实时监控服务器")
    print("=" * 60)
    print()
    print("功能特性:")
    print("  - 实时API状态监控 (每30秒自动检查)")
    print("  - WebSocket实时推送状态更新")
    print("  - 响应时间统计")
    print("  - 可视化仪表板")
    print()
    print(f"API Key: {API_KEY[:10]}..." if len(API_KEY) > 10 else f"API Key: {API_KEY}")
    print(f"检查间隔: {CHECK_INTERVAL}秒")
    print(f"并发检查数: {MAX_CONCURRENT_CHECKS}")
    print()
    print("服务器启动中...")
    print("仪表板地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()

    # Start monitoring loop
    run_monitoring_in_thread()

    # Start Flask server
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        monitoring_active.clear()
        print("服务器已停止")


if __name__ == '__main__':
    main()
