from bs4 import BeautifulSoup
import re

# --- waluty ---
def parse_price(text):
    text = text.replace(",", ".")
    numbers = re.findall(r"[\d.]+", text)
    if numbers:
        return float(numbers[0])
    return None

def detect_currency(text):
    if "€" in text:
        return "EUR"
    if "£" in text:
        return "GBP"
    if "$" in text:
        return "USD"
    return None

def get_full_text(el):
    """Zwraca pełny tekst — najpierw atrybut title, potem alt, potem inner text"""
    if not el:
        return None

    # 1. najważniejsze: prawdziwa pełna nazwa
    if el.get("title"):
        return el.get("title").strip()

    # 2. czasem nazwy są w alt (np. <img alt="Pełna nazwa">)
    if el.get("alt"):
        return el.get("alt").strip()

    # 3. fallback: tekst widoczny
    return el.get_text(strip=True)


def safe_text(v):
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    return str(v).strip()

def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")

    # ---- DETEKCJA SHOP A ----
    shop_a_items = soup.select("li.product")
    if shop_a_items:
        print("[Parser] Rozpoznano strukturę: Shop A")
        products = []
        for item in shop_a_items:
            name = item.select_one("h2.woocommerce-loop-product__title")
            price = item.select_one("span.price")
            products.append({
                "name": safe_text(name),
                "price": safe_text(price),
            })
        return products

    # ---- DETEKCJA SHOP B ----
    shop_b_items = soup.select("article.product_pod")
    if shop_b_items:
        print("[Parser] Rozpoznano strukturę: Shop B")
        products = []
        for item in shop_b_items:
            name = item.find("h3").find("a")
            price = item.select_one("p.price_color")
            products.append({
                "name": safe_text(name),
                "price": safe_text(price),
            })
        return products

    # ---- DETEKCJA SHOP C (WebScraper.io) ----
    ws_items = soup.select(".thumbnail")
    if ws_items:
        print("[Parser] Rozpoznano strukturę: Shop C (WebScraper)")
        products = []
        for item in ws_items:
            name = item.select_one(".title")
            price = item.select_one(".price")
            products.append({
                "name": safe_text(name),
                "price": safe_text(price),
            })
        return products

    print("[Parser] Nie rozpoznano struktury strony.")
    return []