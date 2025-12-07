import sqlite3
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
import re
import argparse

DB_PATH = "scraped_data.db"
TABLE_NAME = "scraped_data"

def load_history(date_from=None, date_to=None):
    """Pobiera dane z zadanego okresu do analizy."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    query = f"SELECT kategoria, wartosc, region, data_zdarzenia FROM {TABLE_NAME}"
    params = []

    if date_from and date_to:
        query += " WHERE data_zdarzenia BETWEEN ? AND ?"
        params.extend([date_from, date_to])
    elif date_from:
        query += " WHERE data_zdarzenia >= ?"
        params.append(date_from)
    elif date_to:
        query += " WHERE data_zdarzenia <= ?"
        params.append(date_to)

    c.execute(query, params)

    rows = c.fetchall()
    conn.close()
    return rows
    
def clean_price(raw):
    """Zamienia HTML lub string z walutą na float."""
    if not raw:
        return 0.0
    if isinstance(raw, (int, float)):
        return float(raw)
    # jeśli HTML
    if "<" in raw:
        soup = BeautifulSoup(raw, "html.parser")
        raw = soup.get_text()
    
    # usuń spacje, zamień przecinek na kropkę
    cleaned_raw = raw.replace(" ", "").replace(",", ".")
    
    # znajdź pierwszą liczbę w stringu
    numbers = re.findall(r"[\d.]+", cleaned_raw)
    
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return 0.0 # Błąd konwersji, np. dla "1.2.3"
    return 0.0





def detect_price_changes(history):
    """Wykrywa zmiany cen w historii."""
    changes = {}
    grouped = {}

    for name, price, shop, timestamp in history:
        price = clean_price(price)
        key = name
        grouped.setdefault(key, []).append((timestamp, price))

    for key, entries in grouped.items():
        entries.sort()

        # Potrzebujemy co najmniej dwóch punktów danych do porównania.
        if len(entries) < 2:
            continue

        old_price = entries[0][1]
        new_price = entries[-1][1]

        # Unikaj dzielenia przez zero i upewnij się, że zmiana jest znacząca.
        if old_price > 0 and abs(new_price - old_price) >= 0.01:
            percent = (new_price - old_price) / old_price * 100
            # Ignoruj mikroskopijne zmiany wynikające z błędów zaokrągleń.
            if abs(percent) < 0.01:
                continue
            changes[key] = percent

    return changes


def generate_report(date_from=None, date_to=None):
    history = load_history(date_from, date_to)

    if date_from and date_to:
        period_str = f"od {date_from} do {date_to}"
    elif date_from:
        period_str = f"od {date_from}"
    elif date_to:
        period_str = f"do {date_to}"
    else:
        period_str = "cały okres"

    print(f"\n===== ANALIZA DANYCH ({period_str}) =====")

    # 1. Zmiany cen
    print("\n>>> ZMIANY CEN:")
    price_changes = detect_price_changes(history)
    product_names = sorted(list(set(item[0] for item in history)))

    if not product_names:
        print(f"Brak produktów w analizowanym okresie: {period_str}.")
    else:
        for name in product_names:
            percent = price_changes.get(name)
            if percent is not None:
                direction = "⬆️" if percent > 0 else "⬇️"
                print(f"- {name}: {direction} {percent:.1f}%")
            else:
                print(f"- {name}: Brak zmian")

    print("\n===== KONIEC ANALIZY =====\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analizator danych z web scrapingu.")
    parser.add_argument("--date-from", help="Data początkowa w formacie YYYY-MM-DD.")
    parser.add_argument("--date-to", help="Data końcowa w formacie YYYY-MM-DD.")
    args = parser.parse_args()

    generate_report(args.date_from, args.date_to)
