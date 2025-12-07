# selenium_fetcher.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
<<<<<<< HEAD:selenium_fetcher.py
=======
from .rate_limiter import limiter
from .robot_parser import robot_manager
>>>>>>> origin/main:scraper/selenium_fetcher.py
from urllib.parse import urlparse

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from rate_limiter import limiter
from robot_parser import robot_manager


# ---------------------------
#  Uniwersalny wybór przeglądarki
# ---------------------------
def create_driver():
    """
    Tworzy driver Chrome lub Firefox.
    Chrome → priorytet
    Firefox → fallback
    """
    # ---- CHROME ----
    try:
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("[INFO] Uruchomiono Chrome WebDriver")
        return driver
    except Exception as e:
        print(f"[WARN] Chrome WebDriver niedostępny: {e}")

    # ---- FIREFOX ----
    try:
        options = FirefoxOptions()
        options.add_argument("--headless")

        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        print("[INFO] Uruchomiono Firefox WebDriver")
        return driver
    except Exception as e:
        print(f"[ERROR] Firefox WebDriver niedostępny: {e}")

    return None


# ---------------------------
#  Pobieranie HTML
# ---------------------------
def fetch_html_selenium(url, wait_selector=None, timeout=10, retries=1):

    if not robot_manager.can_fetch(url):
        print(f"[INFO] Pobieranie {url} zabronione przez robots.txt")
        return None

    domain = urlparse(url).netloc
    print(f"[INFO] Czekam na rate limit dla {domain}...")
    limiter.wait(url)

    print(f"[Selenium] Pobieram stronę: {url}")

    driver = create_driver()
    if not driver:
        print("[ERROR] Brak dostępnej przeglądarki Selenium!")
        return None

    try:
        driver.get(url)

        # 429 Too Many Requests
        if "Too Many Requests" in driver.title or "429" in driver.page_source:
            print("[WARNING] Otrzymano błąd 429 (Too Many Requests)")
            limiter.handle_error_429(url)
            driver.quit()

            if retries > 0:
                print("[INFO] Ponawiam próbę pobrania…")
                return fetch_html_selenium(url, wait_selector, timeout, retries - 1)

            return None

        # Czekamy na element (jeśli wskazany)
        if wait_selector:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
            )
        else:
            time.sleep(2)

        html = driver.page_source
        driver.quit()
        return html

    except Exception as e:
        print(f"[Selenium ERROR] {e}")
        driver.quit()
        return None
