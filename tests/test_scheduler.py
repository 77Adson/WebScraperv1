
import unittest
from unittest.mock import patch, call
from scraper.scheduler import run_scrape_once

class TestScheduler(unittest.TestCase):

    @patch('scraper.scheduler.fetch_with_fallback')
    @patch('scraper.scheduler.parse_products')
    @patch('scraper.scheduler.save_products')
    def test_run_scrape_once_success_first_try(self, mock_save, mock_parse, mock_fetch):
        # Arrange
        urls = {"shop1": "http://shop1.com"}
        mock_fetch.return_value = "<html></html>"
        mock_parse.return_value = [{"name": "product1", "price": 10}]
        
        # Act
        total_products = run_scrape_once(urls)
        
        # Assert
        self.assertEqual(total_products, 1)
        mock_fetch.assert_called_once_with("http://shop1.com")
        mock_parse.assert_called_once_with("<html></html>")
        mock_save.assert_called_once_with([{"name": "product1", "price": 10}], "shop1")

    @patch('scraper.scheduler.fetch_with_fallback')
    @patch('scraper.scheduler.parse_products')
    @patch('scraper.scheduler.save_products')
    def test_run_scrape_once_fallback_success(self, mock_save, mock_parse, mock_fetch):
        # Arrange
        urls = {"shop2": "http://shop2.com"}
        # First call to parse_products returns nothing, triggering fallback
        mock_parse.side_effect = [[], [{"name": "product2", "price": 20}]]
        mock_fetch.side_effect = ["<html>short</html>", "<html>long_selenium</html>"]
        
        # Act
        total_products = run_scrape_once(urls)
        
        # Assert
        self.assertEqual(total_products, 1)
        self.assertEqual(mock_fetch.call_count, 2)
        # The first call to fetch_with_fallback has no wait_selector
        # The second call (the fallback) has a wait_selector
        mock_fetch.assert_has_calls([call("http://shop2.com"), call("http://shop2.com", wait_selector=".thumbnail")])
        self.assertEqual(mock_parse.call_count, 2)
        mock_save.assert_called_once_with([{"name": "product2", "price": 20}], "shop2")
        
    @patch('scraper.scheduler.fetch_with_fallback')
    @patch('scraper.scheduler.parse_products')
    @patch('scraper.scheduler.save_products')
    def test_run_scrape_once_all_fails(self, mock_save, mock_parse, mock_fetch):
        # Arrange
        urls = {"shop3": "http://shop3.com"}
        mock_fetch.return_value = None # Both initial and fallback fetch fail
        
        # Act
        total_products = run_scrape_once(urls)
        
        # Assert
        self.assertEqual(total_products, 0)
        mock_fetch.assert_called_once_with("http://shop3.com")
        mock_parse.assert_not_called()
        mock_save.assert_not_called()

    @patch('scraper.scheduler.fetch_with_fallback')
    @patch('scraper.scheduler.parse_products')
    @patch('scraper.scheduler.save_products')
    def test_run_scrape_once_multiple_urls(self, mock_save, mock_parse, mock_fetch):
        # Arrange
        urls = {"shopA": "http://shopA.com", "shopB": "http://shopB.com"}
        mock_fetch.side_effect = ["<html>A</html>", "<html>B</html>"]
        mock_parse.side_effect = [[{"name": "prodA"}], [{"name": "prodB"}, {"name": "prodC"}]]
        
        # Act
        total_products = run_scrape_once(urls)
        
        # Assert
        self.assertEqual(total_products, 3)
        self.assertEqual(mock_fetch.call_count, 2)
        self.assertEqual(mock_parse.call_count, 2)
        mock_save.assert_has_calls([
            call([{"name": "prodA"}], "shopA"),
            call([{"name": "prodB"}, {"name": "prodC"}], "shopB")
        ])

if __name__ == '__main__':
    unittest.main()
