
import unittest
from unittest.mock import patch, MagicMock
from scraper.rate_limiter import RateLimiter
import time
from collections import deque

class TestRateLimiter(unittest.TestCase):

    def setUp(self):
        self.limiter = RateLimiter(min_delay=1, max_delay=2, requests_per_minute=5)

    @patch('time.sleep', MagicMock())
    @patch('time.time')
    def test_wait_initial_delay(self, mock_time):
        # Arrange
        mock_time.return_value = 1000
        
        # Act
        self.limiter.wait("http://example.com")
        
        # Assert
        # No sleep on first call
        time.sleep.assert_not_called()
        self.assertEqual(self.limiter.last_request_times["example.com"], 1000)

    @patch('time.sleep')
    @patch('time.time')
    def test_wait_respects_delay(self, mock_time, mock_sleep):
        # Arrange
        self.limiter.last_request_times["example.com"] = 1000
        mock_time.return_value = 1000.1 # 0.1s elapsed
        
        # Act
        self.limiter.wait("http://example.com")
        
        # Assert
        # min_delay is 1, so it should sleep
        self.assertGreater(mock_sleep.call_args[0][0], 0.9)
        self.assertLess(mock_sleep.call_args[0][0], 2.0)
        
    @patch('time.sleep')
    @patch('time.time')
    def test_wait_rpm_limit(self, mock_time, mock_sleep):
        # Arrange
        mock_time.return_value = 1000
        self.limiter.requests_per_minute = 5
        self.limiter.domain_requests["example.com"] = deque()
        
        # Add 5 requests, with the oldest being more than 60s ago
        self.limiter.domain_requests["example.com"].append(1000 - 70) # 70 seconds ago
        self.limiter.domain_requests["example.com"].append(1000 - 15)
        self.limiter.domain_requests["example.com"].append(1000 - 10)
        self.limiter.domain_requests["example.com"].append(1000 - 5)
        self.limiter.domain_requests["example.com"].append(1000 - 1)

        # Act
        self.limiter.wait("http://example.com")

        # Assert
        # The while loop in `wait` should be entered because the queue is full (5/5).
        # Inside the loop, `now` (1000) - `oldest` (930) is 70, which is > 60.
        # This should trigger `popleft()` and the loop should terminate.
        # The while loop itself should not call sleep.
        
        # The while loop should have popped one element, and the function appends one.
        # The final length should be 5.
        self.assertEqual(len(self.limiter.domain_requests["example.com"]), 5)

    def test_handle_error_429(self):
        # Act
        self.limiter.handle_error_429("http://example.com")
        
        # Assert
        min_delay, max_delay = self.limiter.domain_delays["example.com"]
        self.assertEqual(min_delay, 2) # 1 * 2
        self.assertEqual(max_delay, 4) # 2 * 2


if __name__ == '__main__':
    unittest.main()
