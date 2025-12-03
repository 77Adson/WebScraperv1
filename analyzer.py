import sqlite3
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
import re

DB_PATH = "scraped_data.db"
TABLE_NAME = "scraped_data"

def load_history(days=7):
    """Pobiera dane z X dni do analizy."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute(f"""
        SELECT kategoria, wartosc, region, data_zdarzenia FROM {TABLE_NAME}
        WHERE data_zdarzenia >= datetime('now', ?)
    """, (f"-{days} days",))

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
    # usuń wszystko oprócz cyfr i kropki
    numbers = re.findall(r"[\d.]+", raw.replace(",", "."))
    if numbers:
        return float(numbers[0])
    return 0.0


def similar(a, b):
    """Używane do porównania nazw produktów między sklepami."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def compare_shops(history):
    """Porównuje ceny podobnych produktów między sklepami."""
    comparisons = []

    for i in range(len(history)):
        for j in range(i+1, len(history)):
            name1, price1, shop1, _ = history[i]
            name2, price2, shop2, _ = history[j]

            if shop1 == shop2:
                continue

            price1 = clean_price(price1)
            price2 = clean_price(price2)

            if similar(name1, name2) >= 0.7:  # dopasowanie nazw
                diff = price2 - price1
                comparisons.append((name1, shop1, price1, shop2, price2, diff))

    return comparisons


def detect_price_changes(history):
    """Wykrywa zmiany cen w historii."""
    changes = {}
    grouped = {}

    for name, price, shop, timestamp in history:
        price = clean_price(price)
        key = (name, shop)
        grouped.setdefault(key, []).append((timestamp, price))

    for key, entries in grouped.items():
        entries.sort()
        old_price = entries[0][1]
        new_price = entries[-1][1]

        if abs(new_price - old_price) >= 0.1:
            percent = (new_price - old_price) / old_price * 100
            changes[key] = percent

    return changes


def generate_report():
    history = load_history(7)

    print("\n===== ANALIZA DANYCH (7 dni) =====")

    # 1. Zmiany cen
    print("\n>>> ZMIANY CEN:")
    price_changes = detect_price_changes(history)

    if not price_changes:
        print("Brak zmian cen w ostatnich 7 dniach.")
    else:
        for (name, shop), percent in price_changes.items():
            direction = "⬆️" if percent > 0 else "⬇️"
            print(f"- {name} ({shop}): {direction} {percent:.1f}%")

    # 2. Porównanie sklepów
    print("\n>>> PORÓWNANIE SKLEPÓW:")
    comparisons = compare_shops(history)

    if not comparisons:
        print("Brak podobnych produktów między sklepami w analizowanym okresie.")
    else:
        for item in comparisons[:20]:  # ograniczenie do 20 wpisów
            name, s1, p1, s2, p2, diff = item
            arrow = "→ tańszy" if diff > 0 else "→ droższy"
            print(f"- {name}: {s1} {p1:.2f} vs {s2} {p2:.2f} ({arrow} {abs(diff):.2f})")

    print("\n===== KONIEC ANALIZY =====\n")

if __name__ == "__main__":
    generate_report()
