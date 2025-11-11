import requests

def fetch_html(url: str) -> str:
    """Pobiera kod HTML ze wskazanego URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; WebScraper/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[Fetcher] Błąd pobierania {url}: {e}")
        return ""
