import sqlite3
from datetime import datetime

DB_NAME = "products.db"

def init_db():
    """Tworzy tabelę, jeśli nie istnieje."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT,
            source TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_products(products: list[dict], source: str):
    """Zapisuje produkty do bazy z informacją o źródle."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for p in products:
        cursor.execute(
            "INSERT INTO products (name, price, currency, source, timestamp) VALUES (?, ?, ?, ?, ?)",
            (p["name"], p["price"], p["currency"], source, datetime.now())
        )
    conn.commit()
    conn.close()
