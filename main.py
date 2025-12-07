import json
from scraper.scheduler import run_scheduler
from scraper.storage import init_db
from scraper.robot_parser import robot_manager

def main():
    """
    Główna funkcja uruchamiająca cykliczne scrapowanie.

    Ten skrypt inicjalizuje bazę danych i uruchamia scheduler, który
    cyklicznie pobiera dane z predefiniowanych adresów URL.
    """
    # Get interval from user
    while True:
        try:
            interval_str = input("Podaj interwał scrapowania w minutach (domyślnie: 60): ")
            if not interval_str:
                interval = 60
                break
            interval = int(interval_str)
            if interval > 0:
                break
            else:
                print("Interwał musi być liczbą dodatnią.")
        except ValueError:
            print("Nieprawidłowa wartość. Podaj liczbę całkowitą.")

    # Wczytaj konfigurację
    config = {}
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Plik config.json nie znaleziony lub jest pusty. Używam domyślnych ustawień.")

    # Ustawienia robots.txt
    if not config.get("respect_robots_txt", True):
        robot_manager.disabled = True
        print("Sprawdzanie robots.txt jest wyłączone (zgodnie z config.json).")
    else:
        robot_manager.disabled = False
        print("Sprawdzanie robots.txt jest włączone (zgodnie z config.json).")

    init_db()

    urls = {
        "Shop A": "https://scrapeme.live/shop/",
        "Shop B": "https://books.toscrape.com/catalogue/category/books_1/index.html",
        "Shop C": "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops",
    }

    # Ustawienia email
    email_config = config if "sender_email" in config else None

    print(f"Uruchamianie cyklicznego pobierania danych co {interval} minut...")
    if email_config and email_config.get("alerts_enabled"):
        print(f"Powiadomienia email włączone. Wysyłanie na: {email_config.get('email_address')}")
    else:
        print("Powiadomienia email wyłączone.")
    print("Aby zatrzymać, naciśnij Ctrl+C.")
    
    try:
        run_scheduler(urls, interval_minutes=interval, email_config=email_config)
    except KeyboardInterrupt:
        print("\nZatrzymano cykliczne pobieranie.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    main()
