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
    """Zwraca listę produktów w formacie [{'name': ..., 'price': ..., 'currency': ...}, ...]."""
    soup = BeautifulSoup(html, "lxml")
    products = []
    for product in soup.select("li.product"):
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
