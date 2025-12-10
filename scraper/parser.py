from bs4 import BeautifulSoup
import re

# --- waluty ---
def parse_price(text):
    """
    Parses a string to find a price and convert it to a float.
    Handles both '.' and ',' as decimal separators, and ',' as a thousand separator.
    """
    if not text:
        return None

    # For formats like "1,234.56", remove thousand separators
    if ',' in text and '.' in text:
        text = text.replace(',', '')
    # For formats like "123,45", treat comma as a decimal point
    else:
        text = text.replace(',', '.')
    
    numbers = re.findall(r"[\d.]+", text)
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return None # Handle cases like "1.2.3"
    return None

def detect_currency(text):
    if "€" in text:
        return "EUR"
    if "£" in text:
        return "GBP"
    if "$" in text:
        return "USD"
    return None


def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")

    # --- SHOP A ---
    shop_a = soup.select(".product")
    if shop_a:
        print("[Parser] Rozpoznano strukturę: Shop A")
        products = []

        for item in shop_a:
            name = item.select_one(".woocommerce-loop-product__title")
            price = item.select_one(".price")

            if name and price:
                raw_price = price.get_text(strip=True)
                products.append({
                    "name": name.get_text(strip=True),
                    "price": parse_price(raw_price),
                    "currency": detect_currency(raw_price),
                })

        return products

    # --- SHOP B ---
    shop_b = soup.select(".product_pod")
    if shop_b:
        print("[Parser] Rozpoznano strukturę: Shop B")
        products = []

        for item in shop_b:
            name = item.select_one("h3 a")
            price = item.select_one(".price_color")

            if name and price:
                raw_price = price.get_text(strip=True)
                products.append({
                    "name": name.get("title"),
                    "price": parse_price(raw_price),
                    "currency": detect_currency(raw_price),
                })

        return products

    # --- SHOP C (webscraper.io laptops) ---
    shop_c = soup.select(".thumbnail")
    if shop_c:
        print("[Parser] Rozpoznano strukturę: Shop C (webscraper.io)")
        products = []

        for item in shop_c:
            name_el = item.select_one(".title")
            price_el = item.select_one(".pull-right.price")

            if name_el and price_el:
                raw_price = price_el.get_text(strip=True)
                products.append({
                    "name": name_el.get('title', name_el.get_text(strip=True)),
                    "price": parse_price(raw_price),
                    "currency": detect_currency(raw_price),
                })

        return products


    # --- KONIEC: brak dopasowania ---
    print("[Parser] Nie rozpoznano struktury strony.")
    return []   
