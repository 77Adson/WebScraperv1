from bs4 import BeautifulSoup
import re

def parse_price(raw_text: str) -> tuple[float, str]:
    """Zwraca (wartość, waluta) z tekstu np. '£63.00' → (63.0, '£')."""
    match = re.match(r"([^\d]+)?([\d.,]+)", raw_text.strip())
    if not match:
        return 0.0, ""
    currency = match.group(1).strip() if match.group(1) else ""
    value = match.group(2).replace(",", ".")
    try:
        price = float(value)
    except ValueError:
        price = 0.0
    return price, currency

def parse_products(html: str) -> list[dict]:
    """Obsługuje różne typy stron (Scrapeme i BooksToScrape)."""
    soup = BeautifulSoup(html, "lxml")
    products = []

    # --- Scrapeme.live/shop/ ---
    shop_a = soup.select("li.product")
    if shop_a:
        for product in shop_a:
            name = product.select_one("h2.woocommerce-loop-product__title")
            price_el = product.select_one("span.woocommerce-Price-amount")
            if name and price_el:
                price_value, currency = parse_price(price_el.get_text(strip=True))
                products.append({
                    "name": name.get_text(strip=True),
                    "price": price_value,
                    "currency": currency,
                })
        return products

    # --- Books.toscrape.com ---
    shop_b = soup.select("article.product_pod")
    if shop_b:
        for product in shop_b:
            name_el = product.select_one("h3 a[title]")
            price_el = product.select_one("p.price_color")
            if name_el and price_el:
                price_value, currency = parse_price(price_el.get_text(strip=True))
                products.append({
                    "name": name_el["title"],
                    "price": price_value,
                    "currency": currency,
                })
        return products

    print("[Parser] Nie rozpoznano struktury strony.")
    return products

