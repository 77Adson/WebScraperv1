import time
from datetime import datetime
from fetcher import fetch_with_fallback
from parser import parse_products
from storage import save_products

def run_scrape_once(urls: dict):
    """Jednorazowe pobranie danych."""
    print("\n===== NOWE WYKONANIE SCRAPERA =====")
    print(f"Data: {datetime.now()}\n")

    for source, url in urls.items():
        print(f"[{source}] Pobieram dane...")

        # --- Krok 1: Requests ---
        html = fetch_with_fallback(url)

        if not html:
            print(f"[{source}] Błąd pobierania (Requests).")
            continue

        products = parse_products(html)

        # --- Krok 2: Jeśli parser nic nie wykrył → Selenium ---
        if len(products) == 0:
            print(f"[{source}] Parser nic nie znalazł — próbuję Selenium...")

            html = fetch_with_fallback(url, wait_selector=".thumbnail")  
            # ".thumbnail" jest OGÓLNYM selektorem produktów dla wielu sklepów

            if html:
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
