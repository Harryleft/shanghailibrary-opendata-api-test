"""
Capture screenshot of the dashboard using Playwright or Selenium
"""
import asyncio
import sys
from pathlib import Path

def capture_with_playwright():
    """Try to capture screenshot using Playwright"""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            page.goto(f'file://{Path(__file__).parent.absolute() / "index.html"}')
            page.wait_for_load_state('networkidle')
            page.screenshot(path='dashboard_screenshot.png', full_page=True)
            browser.close()
        print("Screenshot captured using Playwright: dashboard_screenshot.png")
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Playwright error: {e}")
        return False


def capture_with_selenium():
    """Try to capture screenshot using Selenium"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--window-size=1920,1080')

        driver = webdriver.Chrome(options=options)
        driver.get(f'file://{Path(__file__).parent.absolute() / "index.html"}')

        # Wait for page to load
        import time
        time.sleep(2)

        driver.save_screenshot('dashboard_screenshot.png')
        driver.quit()
        print("Screenshot captured using Selenium: dashboard_screenshot.png")
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"Selenium error: {e}")
        return False


def capture_with_weasyprint():
    """Try to capture screenshot using WeasyPrint"""
    try:
        import weasyprint
        from pathlib import Path

        html_path = Path(__file__).parent / 'index.html'
        css_path = Path(__file__).parent / 'index.html'  # CSS is embedded

        doc = weasyprint.HTML(filename=str(html_path))
        doc.write_png('dashboard_screenshot.png')
        print("Screenshot captured using WeasyPrint: dashboard_screenshot.png")
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"WeasyPrint error: {e}")
        return False


def main():
    """Try different methods to capture screenshot"""
    print("Attempting to capture dashboard screenshot...")

    # Try Playwright first (best for modern web apps)
    if capture_with_playwright():
        return 0

    # Try Selenium
    if capture_with_selenium():
        return 0

    # Try WeasyPrint
    if capture_with_weasyprint():
        return 0

    print("\nCould not capture screenshot automatically.")
    print("Please open web_dashboard/index.html in a browser and take a screenshot manually.")
    print("\nTo install required packages, try:")
    print("  pip install playwright && playwright install chromium")
    print("  or")
    print("  pip install selenium")
    return 1


if __name__ == '__main__':
    sys.exit(main())
