import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.app.adapteurs import BackupManager, PictureManager
from src.app.models import (File, Picture, PictureInfo, StorageConfig,
                            StorageType)
from src.app.ports import MissingPictureException
from src.persistence.ports import PersistencePort

DATE_1 = datetime(1980, 11, 30, tzinfo=timezone.utc)
DATE_2 = datetime(1980, 12, 2, 14, 53, 2, tzinfo=timezone.utc)


class TestBackupManager(unittest.TestCase):
    def setUp(self):
        self.mock_persistence: PersistencePort = MagicMock(spec=PersistencePort)

        self.test_storage_config = StorageConfig(
            id="aaaa", type=StorageType.AWS_GLACIER, config={"value": 12}
        )

        self.backup_manager = BackupManager(
            persistence=self.mock_persistence,
            storage_config_list=[self.test_storage_config],
        )

    def test_get_storages(self):
        expected_storage_ids = ["aaaa"]

        storage_list = self.backup_manager.get_storages()
        storage_ids = [storage.id for storage in storage_list]
        self.assertEqual(expected_storage_ids, storage_ids)

    def test_get_storage_config(self):
        self.assertEqual(
            self.test_storage_config, self.backup_manager.get_storage_config("aaaa")
        )

    def test_get_storage_config_not_found(self):
        self.assertIsNone(self.backup_manager.get_storage_config("bbbb"))


class TestPictureManager(unittest.TestCase):
    def setUp(self):
        self.mock_persistence: PersistencePort = MagicMock(spec=PersistencePort)
        self.picture_manager = PictureManager(persistence=self.mock_persistence)

    def _get_picture(self):
        picture_info = PictureInfo(creation_time=DATE_1, thumbnail="ABCDEF")

        return Picture(
            hash="AAAA",
            backup_required=False,
            file_list=[],
            info=picture_info,
            backup_list=[],
        )

    def _get_picture_file(self):
        return File(
            crawler_id="CRAWLER_1",
            resolution=(12, 12),
            picture_path="/path",
            last_seen=DATE_1,
        )

    def test_list_pictures(self):
        self.mock_persistence.list_pictures.return_value = ["PICTURE_1", "PICTURE_2"]

        pictures = self.picture_manager.list_pictures(
            start_date=DATE_1, end_date=DATE_2
        )

        self.assertEqual(pictures, ["PICTURE_1", "PICTURE_2"])
        self.mock_persistence.list_pictures.assert_called_once_with(
            start=DATE_1, end=DATE_2
        )

    def test_picture_exists_none(self):
        self.mock_persistence.get_picture.return_value = None

        self.assertFalse(self.picture_manager.get_picture("AAAA"))
        self.mock_persistence.get_picture.assert_called_once_with("AAAA")

    def test_picture_exists_ok(self):
        self.mock_persistence.get_picture.return_value = MagicMock(spec=Picture)

        self.assertTrue(self.picture_manager.get_picture("AAAA"))
        self.mock_persistence.get_picture.assert_called_once_with("AAAA")

    def test_record_picture_info_new(self):
        self.mock_persistence.get_picture.return_value = None

        picture_info = PictureInfo(
            creation_time=DATE_1, thumbnail="CXSTTS", orientation="LANDSCAPE"
        )

        self.picture_manager.record_picture_info(hash="AAAA", info=picture_info)

        self.mock_persistence.record_picture.assert_called_once_with(
            Picture(
                hash="AAAA",
                backup_required=False,
                file_list=[],
                info=picture_info,
                backup_list=[],
            )
        )

    def test_record_picture_info_update(self):
        old_picture_info = PictureInfo(
            creation_time=DATE_1, thumbnail="ABCDEF", orientation="LANDSCAPE"
        )

        self.mock_persistence.get_picture.return_value = Picture(
            hash="AAAA",
            backup_required=False,
            file_list=[],
            info=old_picture_info,
            backup_list=[],
        )

        picture_info = PictureInfo(
            creation_time=DATE_1, thumbnail="CXSTTS", orientation="LANDSCAPE"
        )

        self.picture_manager.record_picture_info(hash="AAAA", info=picture_info)

        self.mock_persistence.record_picture.assert_called_once_with(
            Picture(
                hash="AAAA",
                backup_required=False,
                file_list=[],
                info=picture_info,
                backup_list=[],
            )
        )

    def test_record_picture_file_ok(self):
        picture_mock = MagicMock(spec=Picture)
        picture_file_mock = MagicMock(spec=File)
        self.mock_persistence.get_picture.return_value = picture_mock

        self.picture_manager.record_picture_file("AAAAA", picture_file_mock)

        self.mock_persistence.get_picture.assert_called_once_with("AAAAA")
        picture_mock.update_file.assert_called_once_with(picture_file_mock)
        self.mock_persistence.record_picture.assert_called_once_with(picture_mock)

    def test_record_picture_file_missing_file(self):
        picture_file_mock = MagicMock(spec=File)
        self.mock_persistence.get_picture.return_value = None

        with self.assertRaises(MissingPictureException):
            self.picture_manager.record_picture_file("AAAAA", picture_file_mock)
