from fetcher import fetch_html
from parser import parse_products
from storage import init_db, save_products
import sqlite3
import pandas as pd
import os
from datetime import datetime

def main():
    # Inicjalizacja bazy
    init_db()

    # Lista stron do porównania
    urls = {
        "Shop A": "https://scrapeme.live/shop/",
        "Shop B": "https://books.toscrape.com/catalogue/category/books_1/index.html",
    }

    for source, url in urls.items():
        print(f"\nPobieram dane z: {source}")
        html = fetch_html(url)
        if not html:
            continue

        products = parse_products(html)
        print(f"Znaleziono {len(products)} produktów.")
        for p in products[:5]:
            print(f" - {p['name']}: {p['price']}")
        save_products(products, source)

    # --- Krok eksportu danych do CSV dla frontendu ---
    print("\nEksportowanie danych do pliku CSV dla panelu...")
    export_for_frontend()

def export_for_frontend():
    """
    Pobiera dane z bazy SQLite i zapisuje je w formacie CSV,
    którego oczekuje frontend (panel.py).
    """
    db_path = 'products.db'
    output_dir = 'data'
    csv_path = os.path.join(output_dir, 'scraped_data.csv')

    # Utwórz katalog 'data', jeśli nie istnieje
    os.makedirs(output_dir, exist_ok=True)

    try:
        con = sqlite3.connect(db_path)
        # Pobieramy wszystkie produkty z bazy danych
        df = pd.read_sql_query("SELECT name, price, source FROM products", con)
        con.close()

        # Mapowanie kolumn na te oczekiwane przez frontend
        df.rename(columns={'price': 'wartosc', 'source': 'kategoria'}, inplace=True)
        df['data_zdarzenia'] = datetime.now().strftime('%Y-%m-%d') # Używamy dzisiejszej daty jako daty zdarzenia
        df['region'] = 'Online' # Dodajemy stałą wartość dla regionu
        
        df.to_csv(csv_path, index=False)
        print(f"Pomyślnie wyeksportowano {len(df)} rekordów do {csv_path}")
    except Exception as e:
        print(f"Wystąpił błąd podczas eksportu danych do CSV: {e}")

if __name__ == "__main__":
    main()
