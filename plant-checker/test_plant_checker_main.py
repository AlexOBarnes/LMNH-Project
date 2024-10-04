"""Tests for main.py."""
import unittest
from unittest.mock import patch, MagicMock
from main import (
    config_logs,
    get_connection,
    send_emergency_email
)


class TestPlantConditions(unittest.TestCase):
    """Testing plant condition measuring functions in main.py."""
    @patch('main.logging')
    def test_config_logs(self, mock_logging):
        """Tests that logging is enabled."""
        logger = config_logs()
        self.assertIsNotNone(logger)
        mock_logging.basicConfig.assert_called_once_with(level=mock_logging.INFO)


    @patch('main.connect')
    def test_get_connection(self, mock_connect):
        """Tests that connection is established."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        with patch.dict('os.environ', {
            'DB_HOST': 'localhost',
            'DB_PORT': '1433',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PW': 'test_pw'
        }):
            connection = get_connection()

        self.assertEqual(connection, mock_connection)
        mock_connect.assert_called_once()

    @patch('main.client')
    @patch('main.get_date')
    def test_send_emergency_email(self, mock_get_date, mock_client):
        """Tests that email is sent when plant is in danger."""
        mock_ses = MagicMock()
        mock_client.return_value = mock_ses
        mock_get_date.return_value = "Friday 03 October 2024 @ 15:30:00"

        plants = [1, 2, 3]
        with patch.dict('os.environ', {
            'MY_AWS_ACCESS_KEY': 'test_access_key',
            'MY_AWS_SECRET_KEY': 'test_secret_key',
            'FROM': 'test_from@example.com',
            'TO': 'test_to@example.com'
        }):
            send_emergency_email(plants)

        mock_ses.send_email.assert_called_once()  # Ensure email was sent


if __name__ == '__main__':
    unittest.main()
