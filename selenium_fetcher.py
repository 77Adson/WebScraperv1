# selenium_fetcher.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


# selenium_fetcher.py
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import shutil
import os

def create_driver():
    """
    Tworzy headless Firefox driver.
    Selenium automatycznie użyje geckodriver, jeśli jest w PATH.
    """
    options = Options()
    options.headless = True  # tryb niewidoczny
    options.add_argument("--width=1920")
    options.add_argument("--height=1080")

    # jeśli geckodriver nie jest w PATH, próbujemy znaleźć w systemie
    geckodriver_path = shutil.which("geckodriver")
    if geckodriver_path is None:
        raise RuntimeError("Nie znaleziono geckodriver w PATH! Zainstaluj go z https://github.com/mozilla/geckodriver/releases")

    service = Service(geckodriver_path)
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def fetch_html_selenium(url, wait_selector=None, timeout=10):
    """
    Pobiera HTML dynamicznej strony za pomocą Selenium + Firefox.
    wait_selector -> CSS selector, na który Selenium czeka (opcjonalne)
    """
    print(f"[Selenium] Pobieram stronę: {url}")

    driver = create_driver()
    driver.get(url)

    try:
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

