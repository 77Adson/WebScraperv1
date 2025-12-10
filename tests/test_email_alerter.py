
import unittest
from unittest.mock import patch, mock_open
from scraper.email_alerter import send_email_alert
import json

class TestEmailAlerter(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "smtp_server": "smtp.test.com",
        "smtp_port": 587,
        "sender_email": "sender@test.com",
        "email_password": "password"
    }))
    @patch('smtplib.SMTP')
    def test_send_email_alert_success(self, mock_smtp, mock_file):
        # Act
        send_email_alert("receiver@test.com", "Subject", "Body")
        
        # Assert
        mock_smtp.assert_called_once_with("smtp.test.com", 587)
        server = mock_smtp.return_value.__enter__.return_value
        server.starttls.assert_called_once()
        server.login.assert_called_once_with("sender@test.com", "password")
        server.sendmail.assert_called_once()

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_send_email_alert_config_not_found(self, mock_open):
        # Act
        with patch('builtins.print') as mock_print:
            send_email_alert("receiver@test.com", "Subject", "Body")
            
            # Assert
            mock_print.assert_called_with("Błąd: Plik konfiguracyjny 'config.json' nie został znaleziony.")

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "smtp_server": "smtp.test.com"
        # Missing other configs
    }))
    def test_send_email_alert_incomplete_config(self, mock_file):
        # Act
        with patch('builtins.print') as mock_print:
            send_email_alert("receiver@test.com", "Subject", "Body")

            # Assert
            mock_print.assert_called_with("Błąd: Brak pełnej konfiguracji email w pliku 'config.json'. Wymagane są: smtp_server, smtp_port, sender_email, email_password.")

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        "smtp_server": "smtp.test.com",
        "smtp_port": 587,
        "sender_email": "sender@test.com",
        "email_password": "password"
    }))
    @patch('smtplib.SMTP', side_effect=Exception("Connection failed"))
    def test_send_email_alert_smtp_exception(self, mock_smtp, mock_file):
        # Act
        with patch('builtins.print') as mock_print:
            send_email_alert("receiver@test.com", "Subject", "Body")

            # Assert
            mock_print.assert_called_with("Nie udało się wysłać emaila: Connection failed")


if __name__ == '__main__':
    unittest.main()
