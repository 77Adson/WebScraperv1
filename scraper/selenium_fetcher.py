# selenium_fetcher.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from .rate_limiter import limiter
from .robot_parser import robot_manager
from urllib.parse import urlparse

def create_driver():
    """
    Tworzy headless Chrome driver.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"[ERROR] Nie udało się zainstalować lub uruchomić Chrome Drivera: {e}")
        return None

def fetch_html_selenium(url, wait_selector=None, timeout=10, retries=1):
    """
    Pobiera HTML dynamicznej strony za pomocą Selenium + Chrome.
    wait_selector -> CSS selector, na który Selenium czeka (opcjonalne)
    """
    if not robot_manager.can_fetch(url):
        print(f"[INFO] Pobieranie {url} zabronione przez robots.txt")
        return None

    domain = urlparse(url).netloc
    print(f"[INFO] Czekam na rate limit dla {domain}...")
    limiter.wait(url)

    print(f"[Selenium] Pobieram stronę: {url}")

    driver = create_driver()
    if not driver:
        return None
        
    driver.get(url)

    try:
        # Check for 429 error
        if "Too Many Requests" in driver.title or "429" in driver.page_source:
            print(f"[WARNING] Otrzymano błąd 429 (Too Many Requests) dla {url}.")
            limiter.handle_error_429(url)
            driver.quit()
            if retries > 0:
                print("[INFO] Ponawiam próbę pobrania...")
                return fetch_html_selenium(url, wait_selector, timeout, retries - 1)
            return None

        if wait_selector:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
            )
        else:
            time.sleep(2)  # minimalne oczekiwanie, jeśli nie ma wait_selector
            
    except Exception as e:
        print(f"[Selenium] Timeout lub błąd podczas oczekiwania na element: {e}")

    html = driver.page_source
    driver.quit()
    return html
