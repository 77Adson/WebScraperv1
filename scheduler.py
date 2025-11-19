import time
from datetime import datetime
from fetcher import fetch_html
from parser import parse_products
from storage import save_products

def run_scrape_once(urls: dict):
    """Jednorazowe pobranie danych."""
    print("\n===== NOWE WYKONANIE SCRAPERA =====")
    print(f"Data: {datetime.now()}\n")

    for source, url in urls.items():
        print(f"[{source}] Pobieram dane...")
        html = fetch_html(url)
        if not html:
            print(f"[{source}] Błąd pobierania.")
            continue

        products = parse_products(html)
        print(f"[{source}] Znaleziono {len(products)} produktów.")
        save_products(products, source)

    print("\n===== KONIEC WYKONANIA =====\n")


def run_scheduler(urls: dict, interval_minutes: int = 1):
    """
    Uruchamia scraper co X minut.
    Zatrzymanie: Ctrl + C
    """
    print(f"Scheduler uruchomiony. Odpytuję co {interval_minutes} minut.")
    print("Aby przerwać — wciśnij CTRL + C.\n")

    try:
        while True:
            run_scrape_once(urls)
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        print("\nZatrzymano scheduler.")
