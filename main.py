from fetcher import fetch_html
from parser import parse_products
from storage import init_db, save_products

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

if __name__ == "__main__":
    main()
