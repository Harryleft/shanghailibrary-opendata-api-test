"""
Generate detailed statistics JSON for the web dashboard
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Handle Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def format_size(size_bytes):
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_category_from_filename(filename):
    """Extract category from filename like '[PDF] filename.json'"""
    if filename.startswith('[') and ']' in filename:
        return filename.split(']')[0][1:]
    return '其他'


def load_api_definitions():
    """Load all API definitions from api_lists.py"""
    try:
        with open('api_lists.py', 'r', encoding='utf-8') as f:
            content = f.read()
        # Simple extraction - count API definitions
        return content.count('{"name"')
    except:
        return 0


def scan_results_directory():
    """Scan api_results directory and collect detailed info"""
    results_dir = Path('api_results')
    if not results_dir.exists():
        return []

    apis = []
    categories = {}

    for file_path in results_dir.iterdir():
        if file_path.is_file():
            size = file_path.stat().st_size
            filename = file_path.name
            category = get_category_from_filename(filename)

            # Update category stats
            if category not in categories:
                categories[category] = {'count': 0, 'totalSize': 0}
            categories[category]['count'] += 1
            categories[category]['totalSize'] += size

            # Extract clean API name
            clean_name = filename
            if ']' in filename:
                clean_name = filename.split(']', 1)[1].rsplit('.', 1)[0]

            api_info = {
                'name': clean_name,
                'originalName': filename,
                'category': category,
                'size': format_size(size),
                'sizeBytes': size,
                'status': 'success',
                'url': str(file_path),
                'extension': file_path.suffix
            }

            # Try to load JSON preview
            if file_path.suffix == '.json':
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    # Create a preview (first 1000 chars)
                    preview = json.dumps(data, ensure_ascii=False, indent=2)
                    if len(preview) > 2000:
                        preview = preview[:2000] + '\n... (truncated)'
                    api_info['preview'] = preview
                except:
                    api_info['preview'] = '无法读取JSON数据'
            else:
                api_info['preview'] = f'二进制文件: {filename}'

            apis.append(api_info)

    return apis, categories


def load_error_logs():
    """Load error logs from log/error_log.json"""
    error_log_path = Path('log/error_log.json')
    errors = []

    if error_log_path.exists():
        try:
            with open(error_log_path, 'r', encoding='utf-8') as f:
                error_data = json.load(f)
                errors = error_data if isinstance(error_data, list) else []
        except:
            pass

    return errors


def generate_dashboard_data():
    """Generate complete dashboard data"""
    # Scan successful API results
    apis, categories = scan_results_directory()

    # Load error logs
    errors = load_error_logs()

    # Add failed APIs to the list
    for error in errors:
        api_name = error.get('api_name', 'Unknown API')
        category = get_category_from_filename(api_name)

        if category not in categories:
            categories[category] = {'count': 0, 'totalSize': 0}
        categories[category]['count'] += 1

        apis.append({
            'name': api_name,
            'originalName': api_name,
            'category': category,
            'size': 'N/A',
            'sizeBytes': 0,
            'status': 'error',
            'url': None,
            'preview': f"错误: {error.get('error', 'Unknown error')}"
        })

    # Calculate overall statistics
    total_apis = load_api_definitions()
    success_count = len([a for a in apis if a['status'] == 'success'])
    error_count = len([a for a in apis if a['status'] == 'error'])
    total_size = sum(a['sizeBytes'] for a in apis)

    dashboard_data = {
        'stats': {
            'totalApis': total_apis,
            'successCount': success_count,
            'errorCount': error_count,
            'successRate': round((success_count / total_apis * 100) if total_apis > 0 else 0, 1),
            'categoryCount': len(categories),
            'totalSize': format_size(total_size),
            'fileCount': len([a for a in apis if a['status'] == 'success']),
            'lastUpdate': datetime.now().isoformat()
        },
        'categories': categories,
        'apis': apis,
        'errors': errors
    }

    return dashboard_data


def main():
    """Generate and save dashboard data"""
    print("正在生成仪表板数据...")

    dashboard_data = generate_dashboard_data()

    # Create web_dashboard/data directory
    data_dir = Path('web_dashboard/data')
    data_dir.mkdir(parents=True, exist_ok=True)

    # Save stats.json
    output_path = data_dir / 'stats.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)

    print(f"✓ 仪表板数据已生成: {output_path}")
    print(f"  - 总API数: {dashboard_data['stats']['totalApis']}")
    print(f"  - 成功: {dashboard_data['stats']['successCount']}")
    print(f"  - 失败: {dashboard_data['stats']['errorCount']}")
    print(f"  - 成功率: {dashboard_data['stats']['successRate']}%")
    print(f"  - 分类数: {dashboard_data['stats']['categoryCount']}")
    print(f"\n请在浏览器中打开 web_dashboard/index.html 查看仪表板")


if __name__ == '__main__':
    main()
