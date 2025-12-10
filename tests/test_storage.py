
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from scraper.storage import save_products
from datetime import datetime

class TestStorage(unittest.TestCase):

    @patch('scraper.storage.sqlite3.connect')
    @patch('pandas.DataFrame.to_sql')
    def test_save_products(self, mock_to_sql, mock_connect):
        # Arrange
        products = [
            {"name": "Test Product 1", "price": 19.99, "currency": "USD"},
            {"name": "Test Product 2", "price": 25.50, "currency": "EUR"}
        ]
        source = "test_shop"
        
        # Act
        save_products(products, source)
        
        # Assert
        mock_connect.assert_called_once_with("scraped_data.db")
        
        # We can't easily assert the dataframe content, but we can check to_sql call
        mock_to_sql.assert_called_once()
        args, kwargs = mock_to_sql.call_args
        
        self.assertEqual(args[0], "scraped_data") # table name
        self.assertEqual(kwargs['if_exists'], 'append')
        self.assertEqual(kwargs['index'], False)
        
    def test_save_products_empty_list(self):
        # Arrange
        products = []
        source = "test_shop"

        with patch('scraper.storage.pd.DataFrame') as mock_df:
            # Act
            save_products(products, source)

            # Assert
            mock_df.assert_not_called()

if __name__ == '__main__':
    unittest.main()
