import unittest
from unittest.mock import patch

from src.app.models import StorageConfig
from src.tools.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    @patch("os.getenv")
    def test_config(self, mock_getenv):
        mock_getenv.return_value = "toto"

        expected_config = StorageConfig(
            **{
                "id": "id_test",
                "type": "AWS_S3",
                "config": {"key": "toto", "bucket": "bucket_test"},
            }
        )

        expected_list = [expected_config]

        actual_list = ConfigManager(
            "unittests/files/test_config.json"
        ).storage_config_list()

        self.assertEqual(expected_list, actual_list)
        mock_getenv.assert_called_once_with("TEST_KEY")
