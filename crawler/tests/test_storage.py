import unittest
from pathlib import Path
from typing import Any, Callable, Dict
from unittest.mock import MagicMock, call, patch

from app.controllers.backup import AbstractStorageConfigProvider
from app.controllers.picture import PictureAnalyzerFactory
from app.models.backup import StorageConfig, StorageType
from app.storage.aws_s3 import AbstractS3Client, S3BackupStorage
from app.storage.basic import AbstractStorage, BackupResult
from app.storage.factory import StorageFactory, StorageFactoryException
from app.storage.google_photos import (AbstractCaller, AbstractTokenProvider,
                                       GooglePhotosAPIAuthenficationException,
                                       GooglePhotosAPIClient,
                                       GooglePhotosStorage,
                                       RefreshAccessTokenCaller,
                                       RESTTokenProvider)

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


class SimpleCaller(AbstractCaller):
    def call(self, func: Callable, params: Dict) -> Any:
        return func(**params)


class TestGoogleStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_google_client = MagicMock(spec=GooglePhotosAPIClient)
        self.simple_caller = SimpleCaller()
        self.mock_caller = MagicMock(wraps=self.simple_caller)
        self.google_storage = GooglePhotosStorage(
            api_client=self.mock_google_client, caller=self.mock_caller
        )

        self.mock_check_hash = MagicMock()
        self.mock_check_hash.return_value = True

        self.google_storage.__setattr__("check_hash", self.mock_check_hash)

    def test_check_still_exists_not_exists(self):
        self.mock_google_client.get_picture_info.return_value = None

        self.assertFalse(
            self.google_storage.check_still_exists(picture_backup_id="1234")
        )
        self.mock_google_client.get_picture_info.assert_called_once_with(
            picture_id="1234"
        )

        self.mock_caller.call.assert_called_once_with(
            func=self.mock_google_client.get_picture_info, params={"picture_id": "1234"}
        )

    def test_check_still_exists_exists(self):
        self.mock_google_client.get_picture_info.return_value = None

        self.assertFalse(
            self.google_storage.check_still_exists(picture_backup_id="1234")
        )
        self.mock_google_client.get_picture_info.assert_called_once_with(
            picture_id="1234"
        )

        self.mock_caller.call.assert_called_once_with(
            func=self.mock_google_client.get_picture_info, params={"picture_id": "1234"}
        )

    def test_backup_ok(self):
        self.mock_google_client.upload_picture.return_value = "google_backup_id"

        self.assertEqual(
            BackupResult(status=True, picture_bckup_id="google_backup_id"),
            self.google_storage.backup(
                picture_local_path="/xxx/test", picture_hash="xxx"
            ),
        )

        self.mock_google_client.upload_picture.assert_called_once_with(
            picture_file_path="/xxx/test", picture_hash="xxx"
        )

        self.mock_caller.call.assert_called_once_with(
            func=self.mock_google_client.upload_picture,
            params={"picture_file_path": "/xxx/test", "picture_hash": "xxx"},
        )

        self.mock_check_hash.assert_called_once_with("/xxx/test", "xxx")

    def test_backup_check_hash_failed(self):
        self.mock_check_hash.return_value = False

        self.assertEqual(
            BackupResult(status=False, picture_bckup_id="xxx"),
            self.google_storage.backup(
                picture_local_path="/xxx/test", picture_hash="xxx"
            ),
        )

        self.mock_check_hash.assert_called_once_with("/xxx/test", "xxx")

    def test_delete_ok(self):
        self.mock_google_client.edit_picture_description.return_value = True

        self.assertEqual(True, self.google_storage.delete(picture_backup_id="xxx"))

        self.mock_google_client.edit_picture_description.assert_called_once_with(
            picture_id="xxx", new_description="TO BE DELETED"
        )

        self.mock_caller.call.assert_called_once_with(
            func=self.mock_google_client.edit_picture_description,
            params={"picture_id": "xxx", "new_description": "TO BE DELETED"},
        )


class TestRefreshAccessTokenCaller(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=GooglePhotosAPIClient)
        self.token_provider = MagicMock(spec=AbstractTokenProvider)

    def test_ok_call(self):
        caller = RefreshAccessTokenCaller(
            client=self.mock_client, token_provider=self.token_provider
        )

        func = MagicMock()
        func.return_value = "Hello"

        self.assertEqual("Hello", caller.call(func=func, params={"param": 1}))

        self.mock_client.refresh_token.assert_not_called()
        self.token_provider.get_new_token.assert_not_called()

    def test_any_exception_call(self):
        caller = RefreshAccessTokenCaller(
            client=self.mock_client, token_provider=self.token_provider
        )

        func = MagicMock()

        func.side_effect = Exception("N'importe quelle exception !")

        def make_call():
            caller.call(func=func, params={"param": 1})

        self.assertRaises(Exception, make_call)

        self.mock_client.refresh_token.assert_not_called()
        self.token_provider.get_new_token.assert_not_called()

    def test_authentification_exception_call(self):
        caller = RefreshAccessTokenCaller(
            client=self.mock_client, token_provider=self.token_provider
        )

        self.token_provider.get_new_token.return_value = "NOUVEAU_TOKEN"

        func = MagicMock()
        func.side_effect = [GooglePhotosAPIAuthenficationException(), "Hello"]

        self.assertEqual("Hello", caller.call(func=func, params={"param": 1}))

        self.mock_client.refresh_token.assert_called_once_with(
            new_token="NOUVEAU_TOKEN"
        )
        self.token_provider.get_new_token.assert_called_once_with()

        self.assertEqual([call(param=1), call(param=1)], func.call_args_list)


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

    @patch("app.storage.google_photos.RESTTokenProvider")
    def test_create_from_id_google_photos(self, mock_RESTTokenProvider):
        mock_RESTTokenProvider.return_value = MagicMock(spec=RESTTokenProvider)
        mock_RESTTokenProvider.get_current_token.return_value = "abcdef"

        storage_config_google_photos = StorageConfig(
            id="yyy",
            type=StorageType.GOOGLE_PHOTOS,
            config={"config_file": "config.json", "token_url": "http://token_url"},
        )
        self.mock_config_provider.get_storage_config.return_value = (
            storage_config_google_photos
        )

        factory = StorageFactory(self.mock_config_provider)

        google_photos_storage = factory.create_from_id("yyy")

        self.assertIsInstance(google_photos_storage, GooglePhotosStorage)

        self.mock_config_provider.get_storage_config.assert_called_once_with(
            storage_id="yyy"
        )

    def test_create_from_id_not_implemented(self):
        factory = StorageFactory(self.mock_config_provider)
        self.storage_config.type = StorageType.AWS_GLACIER

        with self.assertRaises(StorageFactoryException):
            factory.create_from_id("xxx")
