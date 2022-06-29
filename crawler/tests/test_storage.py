import os
import secrets
import shutil
import unittest
from unittest.mock import MagicMock

from app.controllers.backup import AbstractStorageConfigProvider
from app.controllers.picture import PictureAnalyzerFactory
from app.models.backup import StorageConfig, StorageType
from app.storage.basic import (PictureHashMissmatch, PictureWithNoHash,
                               S3BackupStorage, SimpleFileStorage,
                               StorageFactory, StorageFactoryException, AbstractS3Client)

TEST_PICTURE = "tests/files/test-canon-eos70D-exif.jpg"
TEST_BUCKET = "picture.backup.test"
TEST_DIRECTORY = "test-directory-backup/"
TEST_PICTURE_HASH = "xxxx"
class TestSimpleFileStorage(unittest.TestCase):
    def setUp(self):
        uniq_id = secrets.token_hex(8)
        self.test_file_copy = f"tests/files/{uniq_id}.jpg"
        shutil.copyfile(TEST_PICTURE, self.test_file_copy)

        self.backup_directory = f"tests/files/bckp_{uniq_id}"
        os.mkdir(self.backup_directory)

        self.test_storage = SimpleFileStorage(self.backup_directory)
        self.picture_hash = (
            PictureAnalyzerFactory()
            .perception_hash(self.test_file_copy)
            .get_recorded_hash()
        )

    def tearDown(self):
        os.remove(self.test_file_copy)
        os.rmdir(self.backup_directory)

    def test_backup(self):
        self.assertTrue(
            self.test_storage.backup(self.test_file_copy, self.picture_hash)
        )

        with open(f"{self.backup_directory}/{self.picture_hash}") as backup_file:
            self.assertIsNotNone(backup_file)

        self.assertTrue(self.test_storage.delete(self.picture_hash))

    def test_backup_incorrect_hash(self):
        with self.assertRaises(PictureHashMissmatch):
            self.test_storage.backup(self.test_file_copy, "XXXXXX")

    def test_backup_no_hash(self):
        with self.assertRaises(PictureWithNoHash):
            self.test_storage.backup("tests/files/picture-no-exif.jpg", "XXXXXX")


class TestS3BackupStorage(unittest.TestCase):
    def setUp(self):
        self.mock_S3_client = MagicMock(spec=AbstractS3Client)

        self.test_storage = S3BackupStorage(
            s3_client=self.mock_S3_client,
            bucket=TEST_BUCKET,
            prefix = TEST_DIRECTORY
        )

        self.picture_hash = (
            PictureAnalyzerFactory().perception_hash(TEST_PICTURE).get_recorded_hash()
        )

    def test_backup_ok(self):
        self.mock_S3_client.upload_file.return_value = True

        self.assertTrue(
            self.test_storage.backup(
                picture_local_path=TEST_PICTURE,
                picture_hash=self.picture_hash
            )
        )
        self.mock_S3_client.upload_file.assert_called_once_with(
            TEST_PICTURE,
            TEST_BUCKET,
            TEST_DIRECTORY+self.picture_hash
        )

    def test_backup_not_ok(self):
        self.mock_S3_client.upload_file.return_value = False

        self.assertFalse(
            self.test_storage.backup(
                picture_local_path=TEST_PICTURE,
                picture_hash=self.picture_hash
            )
        )

        self.mock_S3_client.upload_file.assert_called_once_with(
            TEST_PICTURE,
            TEST_BUCKET,
            TEST_DIRECTORY+self.picture_hash
        )

    def test_backup_hash_missmatch(self):
        with self.assertRaises(PictureHashMissmatch):
            self.test_storage.backup(
                picture_local_path=TEST_PICTURE, picture_hash="xxxx"
            )

    def test_check_still_exists_file_not_exists(self):
        self.mock_S3_client.list_objects.return_value = []

        self.assertFalse(self.test_storage.check_still_exists(self.picture_hash))

    def test_check_still_exists_file_exists(self):
        self.mock_S3_client.list_objects.return_value = [
            TEST_DIRECTORY+self.picture_hash
        ]

        self.assertTrue(self.test_storage.check_still_exists(self.picture_hash))

    def test_check_still_exists_not_found(self):
        self.assertFalse(self.test_storage.check_still_exists("AAAA"))


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
