import requests
from selenium_fetcher import fetch_html_selenium

def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return None


def fetch_with_fallback(url, wait_selector=None):
    """
    1. Próbuje pobrać Requests
    2. Jeśli HTML jest pusty lub za krótki → Selenium
    """
    html = fetch_html(url)

    if html is None or len(html) < 2000:
        print("[INFO] Przełączam na Selenium...")
        html = fetch_html_selenium(url, wait_selector=wait_selector) 

    return html
