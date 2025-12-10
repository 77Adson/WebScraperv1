
import unittest
from scraper.parser import parse_price, detect_currency, parse_products

class TestParser(unittest.TestCase):

    def test_parse_price(self):
        self.assertEqual(parse_price("123,45 zł"), 123.45)
        self.assertEqual(parse_price("54.99"), 54.99)
        self.assertEqual(parse_price("Price: $1,234.56"), 1234.56)
        self.assertIsNone(parse_price("No price here"))

    def test_detect_currency(self):
        self.assertEqual(detect_currency("123,45 €"), "EUR")
        self.assertEqual(detect_currency("£54.99"), "GBP")
        self.assertEqual(detect_currency("$1,234.56"), "USD")
        self.assertIsNone(detect_currency("123.45 zł"))

    def test_parse_products_shop_a(self):
        html = """
        <div class="product">
            <a class="woocommerce-LoopProduct-link woocommerce-loop-product__link" href="#">
                <h2 class="woocommerce-loop-product__title">Test Product 1</h2>
                <span class="price"><span class="woocommerce-Price-amount amount"><bdi>12,34<span class="woocommerce-Price-currencySymbol">€</span></bdi></span></span>
            </a>
        </div>
        """
        products = parse_products(html)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['name'], "Test Product 1")
        self.assertEqual(products[0]['price'], 12.34)
        self.assertEqual(products[0]['currency'], "EUR")
        
    def test_parse_products_shop_b(self):
        html = """
        <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
            <article class="product_pod">
                <h3><a href="#" title="Test Product 2">Test Product 2</a></h3>
                <div class="product_price">
                    <p class="price_color">£23.45</p>
                </div>
            </article>
        </li>
        """
        products = parse_products(html)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['name'], "Test Product 2")
        self.assertEqual(products[0]['price'], 23.45)
        self.assertEqual(products[0]['currency'], "GBP")

    def test_parse_products_shop_c(self):
        html = """
        <div class="thumbnail">
            <div class="caption">
                <h4 class="pull-right price">$34.56</h4>
                <h4><a class="title" href="#">Test Product 3</a></h4>
            </div>
        </div>
        """
        products = parse_products(html)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['name'], "Test Product 3")
        self.assertEqual(products[0]['price'], 34.56)
        self.assertEqual(products[0]['currency'], "USD")

    def test_parse_products_no_match(self):
        html = "<div>No products here</div>"
        products = parse_products(html)
        self.assertEqual(len(products), 0)

if __name__ == '__main__':
    unittest.main()
