"""Simple test script to verify API key"""
import sys
import os

# Handle Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests

API_KEY = os.environ.get('SHANGHAI_LIBRARY_API_KEY', 'eca15f528602adb9480d04f286183d133f03f860')
print(f"Testing with API_KEY: {API_KEY[:20]}...")
print()

# Test 1: API that doesn't require authentication
print("Test 1: Public API (no auth required)")
url1 = "http://data.library.sh.cn/entity/architecture/yyknd1unz1xonxp7.json"
response = requests.get(url1, timeout=10)
print(f"  URL: {url1}")
print(f"  Status: {response.status_code}")
if response.status_code == 200:
    print(f"  Result: SUCCESS")
else:
    print(f"  Result: FAILED - {response.text[:100]}")
print()

# Test 2: API with key in params
print("Test 2: API with key in params")
url2 = "https://data1.library.sh.cn/data/jsonld"
params2 = {
    "uri": "http://data.library.sh.cn/entity/architecture/yyknd1unz1xonxp7",
    "key": API_KEY
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
response = requests.get(url2, params=params2, headers=headers, timeout=10)
print(f"  URL: {url2}")
print(f"  Full URL: {response.url}")
print(f"  Status: {response.status_code}")
if response.status_code == 200:
    print(f"  Result: SUCCESS")
    print(f"  Response size: {len(response.content)} bytes")
else:
    print(f"  Result: FAILED")
    print(f"  Response: {response.text[:200]}")
print()

# Test 3: API with key in URL (f-string style)
print("Test 3: API with key in URL")
url3 = f"https://data1.library.sh.cn/webapi/beitie/search?key={API_KEY}"
json_data3 = {
    "searchType": "1",
    "freetext": "化度寺",
    "pager": {"pageth": 1, "pageSize": 1}
}
response = requests.post(url3, json=json_data3, headers=headers, timeout=10)
print(f"  URL: {url3[:80]}...")
print(f"  Status: {response.status_code}")
if response.status_code == 200:
    print(f"  Result: SUCCESS")
    print(f"  Response size: {len(response.content)} bytes")
else:
    print(f"  Result: FAILED")
    print(f"  Response: {response.text[:200]}")
