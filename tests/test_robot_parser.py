
import unittest
from unittest.mock import patch, MagicMock
from scraper.robot_parser import RobotManager

class TestRobotManager(unittest.TestCase):

    def setUp(self):
        self.manager = RobotManager()

    @patch('urllib.robotparser.RobotFileParser')
    def test_can_fetch_allowed(self, MockRobotFileParser):
        # Arrange
        mock_parser = MockRobotFileParser.return_value
        mock_parser.can_fetch.return_value = True
        
        # Act
        allowed = self.manager.can_fetch("http://example.com/allowed")
        
        # Assert
        self.assertTrue(allowed)
        mock_parser.set_url.assert_called_once_with("http://example.com/robots.txt")
        mock_parser.read.assert_called_once()
        mock_parser.can_fetch.assert_called_once_with('*', "http://example.com/allowed")

    @patch('urllib.robotparser.RobotFileParser')
    def test_can_fetch_disallowed(self, MockRobotFileParser):
        # Arrange
        mock_parser = MockRobotFileParser.return_value
        mock_parser.can_fetch.return_value = False
        
        # Act
        allowed = self.manager.can_fetch("http://example.com/disallowed")
        
        # Assert
        self.assertFalse(allowed)

    @patch('urllib.robotparser.RobotFileParser')
    def test_can_fetch_read_error(self, MockRobotFileParser):
        # Arrange
        mock_parser = MockRobotFileParser.return_value
        mock_parser.read.side_effect = Exception("Failed to fetch robots.txt")
        
        # Act
        allowed = self.manager.can_fetch("http://example.com/any")
        
        # Assert
        self.assertTrue(allowed)

    def test_can_fetch_disabled(self):
        # Arrange
        self.manager.disabled = True
        
        # Act
        allowed = self.manager.can_fetch("http://example.com/any")
        
        # Assert
        self.assertTrue(allowed)
        # Ensure no parser was created
        self.assertEqual(len(self.manager.parsers), 0)

    @patch('urllib.robotparser.RobotFileParser')
    def test_can_fetch_cached_parser(self, MockRobotFileParser):
        # Arrange
        mock_parser = MockRobotFileParser.return_value
        mock_parser.can_fetch.return_value = True
        
        # Act
        self.manager.can_fetch("http://example.com/page1")
        self.manager.can_fetch("http://example.com/page2")
        
        # Assert
        # set_url and read should only be called once
        mock_parser.set_url.assert_called_once_with("http://example.com/robots.txt")
        mock_parser.read.assert_called_once()
        self.assertEqual(mock_parser.can_fetch.call_count, 2)

if __name__ == '__main__':
    unittest.main()
