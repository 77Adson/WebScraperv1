import requests
from requests.exceptions import HTTPError
from selenium_fetcher import fetch_html_selenium
from rate_limiter import limiter
from robot_parser import robot_manager
from urllib.parse import urlparse

def fetch_html(url, retries=1):
    """
    Pobiera kod HTML z podanego adresu URL, uwzględniając robots.txt i rate limiting.
    """
    if not robot_manager.can_fetch(url):
        print(f"[INFO] Pobieranie {url} zabronione przez robots.txt")
        return None

    domain = urlparse(url).netloc
    print(f"[INFO] Czekam na rate limit dla {domain}...")
    limiter.wait(url)
    
    print(f"[INFO] Pobieram {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Rzuci wyjątkiem dla kodów 4xx/5xx
        return response.text
    except HTTPError as e:
        if e.response.status_code == 429:
            print(f"[WARNING] Otrzymano błąd 429 (Too Many Requests) dla {url}.")
            limiter.handle_error_429(url)
            if retries > 0:
                print("[INFO] Ponawiam próbę pobrania...")
                return fetch_html(url, retries - 1)
        print(f"[ERROR] Nie udało się pobrać {url}: {e}")
        return None
    except requests.RequestException as e:
        print(f"[ERROR] Nie udało się pobrać {url}: {e}")
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
