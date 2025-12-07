import json
import argparse
from scraper.scheduler import run_scheduler
from scraper.storage import init_db
from scraper.robot_parser import robot_manager

def main():
    """
    Główna funkcja uruchamiająca cykliczne scrapowanie.

    Ten skrypt inicjalizuje bazę danych i uruchamia scheduler, który
    cyklicznie pobiera dane z predefiniowanych adresów URL.
    """
    parser = argparse.ArgumentParser(description="Uruchamia cykliczne scrapowanie.")
    parser.add_argument("--interval", type=int, default=60, help="Interwał scrapowania w minutach (domyślnie: 60).")
    parser.add_argument("--no-robots", action="store_true", help="Wyłącza sprawdzanie pliku robots.txt.")
    args = parser.parse_args()

    if args.no_robots:
        robot_manager.disabled = True
        print("Sprawdzanie robots.txt jest wyłączone.")

    init_db()

    urls = {
        "Shop A": "https://scrapeme.live/shop/",
        "Shop B": "https://books.toscrape.com/catalogue/category/books_1/index.html",
        "Shop C": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
    }

    # Wczytaj konfigurację email
    try:
        with open("config.json", "r") as f:
            email_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        email_config = None

    print(f"Uruchamianie cyklicznego pobierania danych co {args.interval} minut...")
    if email_config and email_config.get("alerts_enabled"):
        print(f"Powiadomienia email włączone. Wysyłanie na: {email_config.get('email_address')}")
    else:
        print("Powiadomienia email wyłączone.")
    print("Aby zatrzymać, naciśnij Ctrl+C.")
    
    try:
        run_scheduler(urls, interval_minutes=args.interval, email_config=email_config)
    except KeyboardInterrupt:
        print("\nZatrzymano cykliczne pobieranie.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    main()
