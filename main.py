from scheduler import run_scrape_once, run_scheduler
from storage import init_db

def main():
    init_db()

    urls = {
        "Shop A": "https://scrapeme.live/shop/",
        "Shop B": "https://books.toscrape.com/catalogue/category/books_1/index.html",
    }

    print("Wybierz tryb:")
    print("1 — Jednorazowe pobranie danych")
    print("2 — Uruchom scheduler (cykliczne pobieranie)")
    choice = input("> ")

    if choice == "1":
        run_scrape_once(urls)
    elif choice == "2":
        try:
            minutes_input = input("Co ile minut wykonywać pobranie? > ")
            minutes = int(minutes_input)
            run_scheduler(urls, interval_minutes=minutes)
        except ValueError:
            print("Niepoprawna wartość. Proszę podać liczbę całkowitą.")
    else:
        print("Niepoprawny wybór.")

if __name__ == "__main__":
    main()
