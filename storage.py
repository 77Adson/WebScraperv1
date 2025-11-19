import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "scraped_data.db"
TABLE_NAME = "scraped_data"


def init_db():
    """Inicjalizuje bazę danych i tworzy tabelę, jeśli nie istnieje."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_zdarzenia TIMESTAMP NOT NULL,
            kategoria TEXT NOT NULL,
            wartosc REAL NOT NULL,
            waluta TEXT,
            region TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print(f"Baza danych '{DB_NAME}' zainicjalizowana.")


def save_products(products: list[dict], source: str):
    """Zapisuje listę produktów do bazy danych."""
    if not products:
        return

    now = datetime.now()
    df = pd.DataFrame(products)
    df['data_zdarzenia'] = now
    df['region'] = source
    df.rename(columns={'name': 'kategoria', 'price': 'wartosc', 'currency': 'waluta'}, inplace=True)

    conn = sqlite3.connect(DB_NAME)
    df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
    conn.close()
    print(f"[{source}] Zapisano {len(df)} produktów do bazy danych.")