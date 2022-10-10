import unittest
from unittest.mock import MagicMock, patch

from requests import Response

from app.controllers.backup import BackupHandler, BackupHandlerException
from app.models.backup import (BackupRequest, BackupStatus, StorageConfig,
                               StorageType)


class TestBackup(unittest.TestCase):
    def setUp(self):
        self.backup_handler = BackupHandler("crawler_id", "BASE_URL")

        self.backup_request_dict = {
            "crawler_id": "AAA",
            "storage_id": "BBB",
            "file_path": "/file",
            "picture_hash": "acde",
            "status": "PENDING"
        }

        self.backup_request_object = BackupRequest(
            backup_id=None,
            **self.backup_request_dict
        )

        self.storage_config_dict = {
            "id": "xxxx",
            "type": "AWS_S3",
            "config": {
                "key": "AKIA4NMYHAFIIKLJZX45",
                "secret": "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",
            },
        }

        self.mock_response = MagicMock(name="mock_response", spec=Response)

    @patch("requests.get")
    def test_get_backup_request_ok(self, mock_get):
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = [self.backup_request_dict]

        mock_get.return_value = self.mock_response

        response = self.backup_handler.get_backup_requests()

        self.assertEqual([self.backup_request_object], response)
        self.assertEqual(BackupStatus.PENDING, response[0].status)
        mock_get.assert_called_once_with("BASE_URL/crawler/backup/crawler_id")

    @patch("requests.get")
    def test_get_backup_request_ok_with_backup_id(self, mock_get):
        self.mock_response.status_code = 200

        self.backup_request_dict["backup_id"] = 1234
        self.mock_response.json.return_value = [self.backup_request_dict]

        mock_get.return_value = self.mock_response

        response = self.backup_handler.get_backup_requests()

        self.backup_request_object.backup_id = 1234

        self.assertEqual([self.backup_request_object], response)
        self.assertEqual(BackupStatus.PENDING, response[0].status)
        mock_get.assert_called_once_with("BASE_URL/crawler/backup/crawler_id")


    @patch("requests.get")
    def test_get_backup_request_malformed_answer(self, mock_get):
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = [{"toto": "xxxx"}]

        mock_get.return_value = self.mock_response

        with self.assertRaises(BackupHandlerException):
            self.backup_handler.get_backup_requests()

    @patch("requests.get")
    def test_get_backup_request_not_ok(self, mock_get):
        self.mock_response.status_code = 500

        mock_get.return_value = self.mock_response

        with self.assertRaises(BackupHandlerException):
            self.backup_handler.get_backup_requests()

    @patch("requests.get")
    def test_get_storage_config(self, mock_get):
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = self.storage_config_dict

        mock_get.return_value = self.mock_response

        response = self.backup_handler.get_storage_config("yyyy")

        expected_config = StorageConfig(**self.storage_config_dict)
        expected_config.type = StorageType.AWS_S3

        self.assertEqual(expected_config, response)
        mock_get.assert_called_once_with("BASE_URL/crawler/storage/yyyy")

    @patch("requests.post")
    def test_send_backup_completed(self, mock_post):
        self.mock_response.status_code = 201

        mock_post.return_value = self.mock_response

        self.assertTrue(
            self.backup_handler.send_backup_completed(
                self.backup_request_object
            )
        )
        mock_post.assert_called_once_with(
            "BASE_URL/crawler/backup/crawler_id", json=self.backup_request_dict
        )

    @patch("requests.delete")
    def test_send_backup_error(self, mock_delete):
        self.mock_response.status_code = 201

        mock_delete.return_value = self.mock_response

        self.assertTrue(
            self.backup_handler.send_backup_error(
                self.backup_request_object
            )
        )
        mock_delete.assert_called_once_with(
            "BASE_URL/crawler/backup/crawler_id", json=self.backup_request_dict
        )
