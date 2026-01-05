"""
Diagnostic script - Check if API Key is properly used
"""
import os
import sys

# Handle Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set API Key
API_KEY = os.environ.get('SHANGHAI_LIBRARY_API_KEY', 'eca15f528602adb9480d04f286183d133f03f860')

print(f"Current API_KEY: {API_KEY}")
print(f"API_KEY length: {len(API_KEY)}")
print()

# Try to import api_lists
try:
    # Set environment variable
    os.environ['SHANGHAI_LIBRARY_API_KEY'] = API_KEY

    # Import module
    import importlib.util

    spec = importlib.util.spec_from_file_location("api_lists", "api_lists.py")
    api_lists = importlib.util.module_from_spec(spec)

    # Set API_KEY
    api_lists.API_KEY = API_KEY

    # Execute module
    spec.loader.exec_module(api_lists)

    # Check API_DEFINITIONS
    definitions = api_lists.API_DEFINITIONS
    print(f"Loaded {len(definitions)} API definitions")
    print()

    # Check first few APIs' URLs
    print("Check if API_KEY is in first 5 API URLs:")
    for i, api_def in enumerate(definitions[:5]):
        name = api_def.get('name', 'Unknown')
        url = api_def.get('url', '')
        params = api_def.get('params', {})
        json_data = api_def.get('json_data', {})

        print(f"\n{i+1}. {name}")
        print(f"   URL: {url[:100]}...")

        if API_KEY in url:
            print(f"   [OK] URL contains API_KEY")
        else:
            print(f"   [X] URL does NOT contain API_KEY")

        if params and 'key' in params:
            if params['key'] == API_KEY:
                print(f"   [OK] params.key is correct")
            elif params['key']:
                print(f"   [?] params.key = {str(params['key'])[:20]}...")
            else:
                print(f"   [X] params.key is empty")

        if json_data and 'apiKey' in json_data:
            if json_data['apiKey'] == API_KEY:
                print(f"   [OK] json_data.apiKey is correct")
            elif json_data['apiKey']:
                print(f"   [?] json_data.apiKey = {str(json_data['apiKey'])[:20]}...")
            else:
                print(f"   [X] json_data.apiKey is empty")

    print()
    print("="*60)
    print("Testing a simple API request:")
    print("="*60)

    # Test a simple API
    import requests

    test_api = definitions[0]  # First API
    print(f"\nTesting: {test_api['name']}")
    print(f"URL: {test_api['url']}")
    print(f"Method: {test_api['method']}")

    response = requests.get(test_api['url'], params=test_api.get('params', {}), timeout=10)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print(f"[OK] Success!")
    else:
        print(f"[X] Failed: {response.text[:200]}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
