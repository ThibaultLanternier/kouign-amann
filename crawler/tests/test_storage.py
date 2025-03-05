import unittest
from pathlib import Path
from unittest.mock import MagicMock

from app.controllers.backup import AbstractStorageConfigProvider
from app.controllers.picture import PictureAnalyzerFactory
from app.models.backup import StorageConfig, StorageType
from app.storage.aws_s3 import AbstractS3Client, S3BackupStorage
from app.storage.basic import AbstractStorage, BackupResult
from app.storage.factory import StorageFactory, StorageFactoryException

TEST_PICTURE = "tests/files/test-canon-eos70D-exif.jpg"
TEST_BUCKET = "picture.backup.test"
TEST_DIRECTORY = "test-directory-backup/"
TEST_PICTURE_HASH = "xxxx"


class TestS3BackupStorage(unittest.TestCase):
    def setUp(self):
        self.mock_S3_client = MagicMock(spec=AbstractS3Client)

        self.test_storage = S3BackupStorage(
            s3_client=self.mock_S3_client, bucket=TEST_BUCKET, prefix=TEST_DIRECTORY
        )

        self.picture_hash = (
            PictureAnalyzerFactory().perception_hash(TEST_PICTURE)._get_recorded_hash()
        )

    def test_backup_ok(self):
        self.mock_S3_client.upload_file.return_value = True

        self.assertTrue(
            self.test_storage.backup(
                picture_local_path=TEST_PICTURE, picture_hash=self.picture_hash
            )
        )
        self.mock_S3_client.upload_file.assert_called_once_with(
            TEST_PICTURE, TEST_BUCKET, TEST_DIRECTORY + self.picture_hash
        )

    def test_backup_not_ok(self):
        self.mock_S3_client.upload_file.return_value = False

        self.assertFalse(
            self.test_storage.backup(
                picture_local_path=TEST_PICTURE, picture_hash=self.picture_hash
            ).status
        )

        self.mock_S3_client.upload_file.assert_called_once_with(
            TEST_PICTURE, TEST_BUCKET, TEST_DIRECTORY + self.picture_hash
        )

    def test_backup_hash_missmatch(self):
        self.assertFalse(
            self.test_storage.backup(
                picture_local_path=TEST_PICTURE, picture_hash="xxxx"
            ).status
        )

    def test_check_still_exists_file_not_exists(self):
        self.mock_S3_client.list_objects.return_value = []

        self.assertFalse(self.test_storage.check_still_exists(self.picture_hash))

    def test_check_still_exists_file_exists(self):
        self.mock_S3_client.list_objects.return_value = [
            TEST_DIRECTORY + self.picture_hash
        ]

        self.assertTrue(self.test_storage.check_still_exists(self.picture_hash))

    def test_check_still_exists_not_found(self):
        self.assertFalse(self.test_storage.check_still_exists("AAAA"))

    def test_delete(self):
        self.test_storage.delete(picture_backup_id="BBBB")

        self.mock_S3_client.delete_object.assert_called_once_with(
            Bucket="picture.backup.test", Prefix="test-directory-backup/BBBB"
        )


class BasicStorage(AbstractStorage):
    def backup(self, picture_local_path: Path, picture_hash: str) -> BackupResult:
        raise NotImplementedError()

    def delete(self, picture_backup_id) -> bool:
        raise NotImplementedError()

    def check_still_exists(self, picture_backup_id: str) -> bool:
        raise NotImplementedError()


class TestAbstractStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.test_storage = BasicStorage()

        self.picture_hash = (
            PictureAnalyzerFactory()
            .perception_hash(Path(TEST_PICTURE))
            ._get_recorded_hash()
        )

    def test_check_hash_file_not_found(self):
        self.assertFalse(
            self.test_storage.check_hash("test/this-file-does-not-exists", "xxxx")
        )

    def test_check_hash_ok(self):
        self.assertTrue(self.test_storage.check_hash(TEST_PICTURE, self.picture_hash))

    def test_check_hash_not_ok(self):
        self.assertFalse(self.test_storage.check_hash(TEST_PICTURE, "incorrect_hash"))


class TestStorageFactory(unittest.TestCase):
    def setUp(self):
        self.mock_config_provider = MagicMock(spec=AbstractStorageConfigProvider)
        self.storage_config = StorageConfig(
            id="xxx",
            type=StorageType.AWS_S3,
            config={"key": "key", "secret": "secret", "bucket": "bucket"},
        )
        self.mock_config_provider.get_storage_config.return_value = self.storage_config

    def test_create_from_id(self):
        factory = StorageFactory(self.mock_config_provider)

        factory.create_from_id("xxx")
        s3_storage = factory.create_from_id("xxx")

        self.assertIsInstance(s3_storage, S3BackupStorage)

        self.mock_config_provider.get_storage_config.assert_called_once_with(
            storage_id="xxx"
        )

    def test_create_from_id_not_implemented(self):
        factory = StorageFactory(self.mock_config_provider)
        self.storage_config.type = StorageType.AWS_GLACIER

        with self.assertRaises(StorageFactoryException):
            factory.create_from_id("xxx")
