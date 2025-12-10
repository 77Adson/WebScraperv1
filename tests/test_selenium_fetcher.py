
import unittest
from unittest.mock import patch, MagicMock
from scraper.selenium_fetcher import fetch_html_selenium

class TestSeleniumFetcher(unittest.TestCase):

    @patch('scraper.selenium_fetcher.create_driver')
    @patch('scraper.selenium_fetcher.robot_manager')
    @patch('scraper.selenium_fetcher.limiter')
    @patch('scraper.selenium_fetcher.WebDriverWait')
    def test_fetch_html_selenium_success(self, MockWebDriverWait, mock_limiter, mock_robot_manager, mock_create_driver):
        # Arrange
        mock_robot_manager.can_fetch.return_value = True
        mock_driver = MagicMock()
        mock_driver.page_source = "<html><body><div class='content'></div></body></html>"
        mock_create_driver.return_value = mock_driver
        
        # Act
        html = fetch_html_selenium("http://example.com", wait_selector=".content")
        
        # Assert
        self.assertEqual(html, "<html><body><div class='content'></div></body></html>")
        mock_robot_manager.can_fetch.assert_called_once_with("http://example.com")
        mock_limiter.wait.assert_called_once_with("http://example.com")
        mock_create_driver.assert_called_once()
        mock_driver.get.assert_called_once_with("http://example.com")
        MockWebDriverWait.assert_called_once()
        mock_driver.quit.assert_called_once()

    @patch('scraper.selenium_fetcher.robot_manager')
    def test_fetch_html_selenium_robots_disallowed(self, mock_robot_manager):
        # Arrange
        mock_robot_manager.can_fetch.return_value = False
        
        # Act
        html = fetch_html_selenium("http://example.com")
        
        # Assert
        self.assertIsNone(html)
        mock_robot_manager.can_fetch.assert_called_once_with("http://example.com")

    @patch('scraper.selenium_fetcher.create_driver')
    @patch('scraper.selenium_fetcher.robot_manager')
    @patch('scraper.selenium_fetcher.limiter')
    def test_fetch_html_selenium_429_retry(self, mock_limiter, mock_robot_manager, mock_create_driver):
        # Arrange
        mock_robot_manager.can_fetch.return_value = True
        
        mock_driver_429 = MagicMock()
        mock_driver_429.title = "Too Many Requests"

        mock_driver_success = MagicMock()
        mock_driver_success.page_source = "<html>Success</html>"
        
        mock_create_driver.side_effect = [mock_driver_429, mock_driver_success]
        
        # Act
        html = fetch_html_selenium("http://example.com", retries=1)
        
        # Assert
        self.assertEqual(html, "<html>Success</html>")
        self.assertEqual(mock_create_driver.call_count, 2)
        mock_limiter.handle_error_429.assert_called_once_with("http://example.com")

    @patch('scraper.selenium_fetcher.create_driver', return_value=None)
    def test_fetch_html_selenium_driver_creation_fails(self, mock_create_driver):
        # Act
        html = fetch_html_selenium("http://example.com")
        
        # Assert
        self.assertIsNone(html)
        
    @patch('scraper.selenium_fetcher.create_driver')
    @patch('scraper.selenium_fetcher.robot_manager')
    @patch('scraper.selenium_fetcher.limiter')
    @patch('scraper.selenium_fetcher.WebDriverWait')
    def test_fetch_html_selenium_wait_timeout(self, MockWebDriverWait, mock_limiter, mock_robot_manager, mock_create_driver):
        # Arrange
        mock_robot_manager.can_fetch.return_value = True
        mock_driver = MagicMock()
        mock_driver.page_source = "<html>No content</html>"
        mock_create_driver.return_value = mock_driver
        MockWebDriverWait.return_value.until.side_effect = Exception("Timeout")

        # Act
        html = fetch_html_selenium("http://example.com", wait_selector=".content")

        # Assert
        self.assertEqual(html, "<html>No content</html>")
        mock_driver.quit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
