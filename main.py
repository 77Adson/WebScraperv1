import json
from scheduler import run_scheduler
from storage import init_db

def main():
    """
    Główna funkcja uruchamiająca cykliczne scrapowanie.

    Ten skrypt inicjalizuje bazę danych i uruchamia scheduler, który
    cyklicznie pobiera dane z predefiniowanych adresów URL co 60 minut.
    """
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

    print("Uruchamianie cyklicznego pobierania danych co 60 minut...")
    if email_config and email_config.get("alerts_enabled"):
        print(f"Powiadomienia email włączone. Wysyłanie na: {email_config.get('email_address')}")
    else:
        print("Powiadomienia email wyłączone.")
    print("Aby zatrzymać, naciśnij Ctrl+C.")
    
    try:
        run_scheduler(urls, interval_minutes=60, email_config=email_config)
    except KeyboardInterrupt:
        print("\nZatrzymano cykliczne pobieranie.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    main()
