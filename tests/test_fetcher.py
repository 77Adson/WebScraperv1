
import unittest
from unittest.mock import patch, MagicMock
import requests
from scraper.fetcher import fetch_html

class TestFetchHTML(unittest.TestCase):

    @patch('scraper.fetcher.robot_manager')
    @patch('scraper.fetcher.limiter')
    @patch('scraper.fetcher.requests.get')
    def test_fetch_html_success(self, mock_get, mock_limiter, mock_robot_manager):
        # Arrange
        mock_robot_manager.can_fetch.return_value = True
        mock_response = MagicMock()
        mock_response.text = "<html><body><h1>Test</h1></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Act
        html = fetch_html("http://example.com")
        
        # Assert
        self.assertEqual(html, "<html><body><h1>Test</h1></body></html>")
        mock_robot_manager.can_fetch.assert_called_once_with("http://example.com")
        mock_limiter.wait.assert_called_once_with("http://example.com")
        mock_get.assert_called_once_with("http://example.com", timeout=10)
        mock_response.raise_for_status.assert_called_once()

    @patch('scraper.fetcher.robot_manager')
    def test_fetch_html_robots_disallowed(self, mock_robot_manager):
        # Arrange
        mock_robot_manager.can_fetch.return_value = False
        
        # Act
        html = fetch_html("http://example.com")
        
        # Assert
        self.assertIsNone(html)
        mock_robot_manager.can_fetch.assert_called_once_with("http://example.com")

    @patch('scraper.fetcher.robot_manager')
    @patch('scraper.fetcher.limiter')
    @patch('scraper.fetcher.requests.get')
    def test_fetch_html_http_error(self, mock_get, mock_limiter, mock_robot_manager):
        # Arrange
        mock_robot_manager.can_fetch.return_value = True
        mock_response = MagicMock()
        http_error = requests.exceptions.HTTPError(response=MagicMock(status_code=404))
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        # Act
        html = fetch_html("http://example.com")
        
        # Assert
        self.assertIsNone(html)

    @patch('scraper.fetcher.robot_manager')
    @patch('scraper.fetcher.limiter')
    @patch('scraper.fetcher.requests.get')
    def test_fetch_html_request_exception(self, mock_get, mock_limiter, mock_robot_manager):
        # Arrange
        mock_robot_manager.can_fetch.return_value = True
        mock_get.side_effect = requests.exceptions.RequestException
        
        # Act
        html = fetch_html("http://example.com")
        
        # Assert
        self.assertIsNone(html)
        
    @patch('scraper.fetcher.robot_manager')
    @patch('scraper.fetcher.limiter')
    @patch('scraper.fetcher.requests.get')
    def test_fetch_html_429_retry(self, mock_get, mock_limiter, mock_robot_manager):
        # Arrange
        mock_robot_manager.can_fetch.return_value = True
        
        # First call raises 429, second call is successful
        mock_429_response = MagicMock()
        error_response_obj = MagicMock(status_code=429)
        http_error = requests.exceptions.HTTPError(response=error_response_obj)
        mock_429_response.raise_for_status.side_effect = http_error

        success_response = MagicMock()
        success_response.text = "<html>Success</html>"
        
        mock_get.side_effect = [
            mock_429_response,
            success_response
        ]
        
        # Act
        html = fetch_html("http://example.com", retries=1)
        
        # Assert
        self.assertEqual(html, "<html>Success</html>")
        self.assertEqual(mock_get.call_count, 2)
        mock_limiter.handle_error_429.assert_called_once_with("http://example.com")

if __name__ == '__main__':
    unittest.main()
