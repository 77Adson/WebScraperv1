import unittest
from analyzer import clean_price, detect_price_changes

class TestAnalyzer(unittest.TestCase):

    def test_clean_price(self):
        self.assertEqual(clean_price(123), 123.0)
        self.assertEqual(clean_price(123.45), 123.45)
        self.assertEqual(clean_price("123,45 zł"), 123.45)
        self.assertEqual(clean_price("54.99"), 54.99)
        self.assertEqual(clean_price("Price: $1 234.56"), 1234.56)
        self.assertEqual(clean_price("<span>1,000.99</span>"), 1000.99)
        self.assertEqual(clean_price(None), 0.0)
        self.assertEqual(clean_price(""), 0.0)
        self.assertEqual(clean_price("No price"), 0.0)

    def test_detect_price_changes(self):
        history = [
            # Product 1: Increase
            ("Product 1", 100, "ShopA", "2023-01-01 10:00:00"),
            ("Product 1", 120, "ShopA", "2023-01-02 10:00:00"),
            # Product 2: Decrease
            ("Product 2", 200, "ShopB", "2023-01-01 10:00:00"),
            ("Product 2", 150, "ShopB", "2023-01-02 10:00:00"),
            # Product 3: No change
            ("Product 3", 50, "ShopC", "2023-01-01 10:00:00"),
            ("Product 3", 50, "ShopC", "2023-01-02 10:00:00"),
            # Product 4: Only one entry
            ("Product 4", 300, "ShopA", "2023-01-01 10:00:00"),
            # Product 5: First and last
            ("Product 5", 99, "ShopB", "2023-01-01 10:00:00"),
            ("Product 5", 105, "ShopB", "2023-01-02 10:00:00"),
            ("Product 5", 90, "ShopB", "2023-01-03 10:00:00"),
             # Product 6: Zero price
            ("Product 6", 0, "ShopC", "2023-01-01 10:00:00"),
            ("Product 6", 10, "ShopC", "2023-01-02 10:00:00"),
        ]
        
        changes = detect_price_changes(history)
        
        self.assertIn("Product 1", changes)
        self.assertAlmostEqual(changes["Product 1"], 20.0)
        
        self.assertIn("Product 2", changes)
        self.assertAlmostEqual(changes["Product 2"], -25.0)

        # In this version, no change means the key is not in the dict
        self.assertNotIn("Product 3", changes)
        
        self.assertNotIn("Product 4", changes)
        
        self.assertIn("Product 5", changes)
        self.assertAlmostEqual(changes["Product 5"], (90-99)/99 * 100)

        self.assertNotIn("Product 6", changes) # old_price is 0, so no division

if __name__ == '__main__':
    unittest.main()
