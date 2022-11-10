import unittest
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from src.app.models import (Backup, BackupException, BackupStatus, DictFactory,
                            File, GoogleAccessToken, Picture, PictureInfo,
                            Storage, StorageConfig, StorageType,
                            google_access_token_factory)

TEST_TIME = datetime(1980, 11, 30, tzinfo=timezone.utc)
OTHER_TEST_TIME = datetime(1980, 11, 30, 12, tzinfo=timezone.utc)
ANOTHER_TEST_TIME = datetime(1980, 11, 30, 14, tzinfo=timezone.utc)


class TestPicture(unittest.TestCase):
    def setUp(self):
        self.storage = Storage(id="a")

        self.file_1 = File(
            crawler_id="B",
            resolution=(100, 100),
            picture_path="/picture_1_large",
            last_seen=OTHER_TEST_TIME,
        )
        self.file_2 = File(
            crawler_id="B",
            resolution=(50, 50),
            picture_path="/picture_1_small",
            last_seen=TEST_TIME,
        )

        self.test_picture = Picture(
            hash="xxx",
            info=PictureInfo(
                thumbnail="AAAA",
                creation_time=datetime(1980, 11, 30, tzinfo=timezone.utc),
                orientation="LANDSCAPE",
            ),
            backup_required=True,
            file_list=[self.file_1, self.file_2],
            backup_list=[],
        )
        self.pending_backup = Backup(
            crawler_id="B",
            storage_id="a",
            file_path="/picture_1_large",
            status=BackupStatus.PENDING,
            creation_time=OTHER_TEST_TIME,
            backup_id=None,
        )

        self.maxDiff = None

    def test_record_done(self):
        self.test_picture.backup_list = [self.pending_backup]

        self.test_picture.record_done(
            storage_id=self.pending_backup.storage_id,
            crawler_id=self.pending_backup.crawler_id,
            backup_id="ABCDEF",
        )

        self.assertEqual(BackupStatus.DONE, self.test_picture.backup_list[0].status)
        self.assertEqual("ABCDEF", self.test_picture.backup_list[0].backup_id)

    def test_record_deleted(self):
        pending_backup_2 = Backup(
            crawler_id="B",
            storage_id="b",
            file_path="/picture_1_large",
            status=BackupStatus.PENDING_DELETE,
            creation_time=OTHER_TEST_TIME,
            backup_id=None,
        )
        self.test_picture.backup_list = [self.pending_backup, pending_backup_2]

        self.test_picture.record_deleted(
            storage_id=self.pending_backup.storage_id,
            crawler_id=self.pending_backup.crawler_id,
        )

        self.assertEqual([pending_backup_2], self.test_picture.backup_list)

    def test_backup_error(self):
        self.test_picture.backup_list = [self.pending_backup]

        self.test_picture.record_backup_error(
            storage_id=self.pending_backup.storage_id,
            crawler_id=self.pending_backup.crawler_id,
        )

        self.assertEqual(BackupStatus.ERROR, self.test_picture.backup_list[0].status)

    def test_done_missing_backup(self):
        with self.assertRaises(BackupException):
            self.test_picture.record_done(
                storage_id="X", crawler_id="Y", backup_id="ABCDEF"
            )

    def test_plan_backup_ok(self):
        self.test_picture.plan_backup(
            storage_list=[self.storage],
            current_time=TEST_TIME,
        )

        self.assertEqual(
            self.test_picture.backup_list,
            [
                Backup(
                    crawler_id="B",
                    storage_id="a",
                    file_path="/picture_1_large",
                    status=BackupStatus.PENDING,
                    creation_time=TEST_TIME,
                    backup_id=None,
                )
            ],
        )

    def test_plan_backup_already_planned(self):
        self.test_picture.backup_list = [self.pending_backup]

        self.test_picture.plan_backup(
            storage_list=[self.storage],
            current_time=TEST_TIME,
        )

        self.assertEqual(self.test_picture.backup_list, [self.pending_backup])

    def test_plan_backup_switch_done_backup_to_pending_delete(self):
        self.pending_backup.status = BackupStatus.DONE
        self.test_picture.backup_list = [self.pending_backup]
        self.test_picture.backup_required = False

        self.test_picture.plan_backup(
            storage_list=[self.storage],
            current_time=TEST_TIME,
        )

        self.assertEqual(
            self.test_picture.backup_list[0].status, BackupStatus.PENDING_DELETE
        )

    def test_plan_backup_remove_pending_backup(self):
        self.test_picture.backup_list = [self.pending_backup]
        self.test_picture.backup_required = False

        self.test_picture.plan_backup(
            storage_list=[self.storage],
            current_time=TEST_TIME,
        )

        self.assertEqual(self.test_picture.backup_list, [])

    def test_update_file_new_file(self):
        other_file = File(
            crawler_id="B",
            resolution=(50, 50),
            picture_path="/picture_1_small_other",
            last_seen=TEST_TIME,
        )

        self.test_picture.update_file(other_file)

        expectect_list = [self.file_1, self.file_2, other_file]

        self.assertEqual(expectect_list, self.test_picture.file_list)

    def test_update_file_existing_file(self):
        updated_file = File(
            crawler_id="B",
            resolution=(50, 50),
            picture_path="/picture_1_small",
            last_seen=ANOTHER_TEST_TIME,
        )

        self.test_picture.update_file(updated_file)

        expected = [self.file_1, updated_file]

        self.assertEqual(expected, self.test_picture.file_list)


class TestPictureInfo(unittest.TestCase):
    def setUp(self):
        self.picture_info = PictureInfo(
            creation_time=datetime(
                2007, 5, 24, 19, 53, 39, tzinfo=timezone(timedelta(seconds=3600))
            ),
            thumbnail="THUMBNAIL",
            orientation="LANDSCAPE",
        )

    def test_date_conversion(self):
        picture_info_string = PictureInfo(
            creation_time="2007-05-24T18:53:39.000000Z",
            thumbnail="THUMBNAIL",
            orientation="LANDSCAPE",
        )

        self.assertEqual(picture_info_string, self.picture_info)

    def test_as_dict_dictfactory(self):
        expected = {
            "creation_time": "2007-05-24T18:53:39.000000Z",
            "thumbnail": "THUMBNAIL",
            "orientation": "LANDSCAPE",
        }

        self.assertEqual(expected, asdict(self.picture_info, dict_factory=DictFactory))

    def test_as_dict(self):
        expected = {
            "creation_time": datetime(2007, 5, 24, 18, 53, 39, tzinfo=timezone.utc),
            "thumbnail": "THUMBNAIL",
            "orientation": "LANDSCAPE",
        }

        self.assertEqual(expected, asdict(self.picture_info))


class TestFile(unittest.TestCase):
    def setUp(self):
        self.small_file_a = File(
            crawler_id="B",
            resolution=(50, 50),
            picture_path="/picture_1_small",
            last_seen=TEST_TIME,
        )
        self.small_file_e = File(
            crawler_id="E",
            resolution=(50, 50),
            picture_path="/picture_2_small",
            last_seen=TEST_TIME,
        )
        self.large_file_c = File(
            crawler_id="C",
            resolution=(100, 100),
            picture_path="/picture_1_small",
            last_seen=TEST_TIME,
        )
        self.large_younger_file_d = File(
            crawler_id="D",
            resolution=(100, 100),
            picture_path="/picture_1_small",
            last_seen=OTHER_TEST_TIME,
        )

    def test_date_conversion(self):
        test_file = File(
            crawler_id="B",
            resolution=(50, 50),
            picture_path="/picture_1_small",
            last_seen="1980-11-30T00:00:00.000000Z",
        )

        self.assertEqual(test_file.last_seen, self.small_file_a.last_seen)

    def test_equal_files(self):
        self.assertTrue(self.small_file_a == self.small_file_e)
        self.assertFalse(self.small_file_a == self.large_file_c)

        self.assertFalse(self.small_file_a < self.small_file_e)

    def test_larger_file(self):
        self.assertTrue(self.large_file_c > self.small_file_a)
        self.assertTrue(self.small_file_a < self.large_file_c)

    def test_younger_file(self):
        self.assertTrue(self.large_file_c < self.large_younger_file_d)
        self.assertTrue(self.large_younger_file_d > self.large_file_c)

    def test_younger_file_greater_than_or_equal(self):
        self.assertTrue(self.large_file_c <= self.large_younger_file_d)
        self.assertTrue(self.large_file_c <= self.large_file_c)
        self.assertTrue(self.large_younger_file_d >= self.large_file_c)

    def test_sort(self):
        test_list = [self.small_file_a, self.large_file_c, self.small_file_e]

        test_list.sort()

        self.assertEqual(
            [self.small_file_a, self.small_file_e, self.large_file_c], test_list
        )

    def test_sort_descending(self):
        test_list = [self.small_file_a, self.large_file_c, self.small_file_e]

        test_list.sort(reverse=True)

        self.assertEqual(
            [self.large_file_c, self.small_file_e, self.small_file_a], test_list
        )


class TestGoogleAccessToken(unittest.TestCase):
    def test_google_access_token_factory(self):
        input = {
            "access_token": "ya29",
            "expires_in": 35,
            "scope": ["https://toto"],
            "token_type": "Bearer",
            "expires_at": 1663104574.3838615,
        }
        now = datetime(1980, 11, 30, 15, 0, 0, tzinfo=timezone.utc)
        expected_expiry = datetime(1980, 11, 30, 15, 0, 35, tzinfo=timezone.utc)

        result = google_access_token_factory(input, now)

        self.assertEqual(
            GoogleAccessToken(
                access_token="ya29",
                scope=["https://toto"],
                token_type="Bearer",
                expires_at=expected_expiry,
            ),
            result,
        )


class TestStorageConfig(unittest.TestCase):
    @patch("os.getenv")
    def test_missing_env_variable(self, mock_env):
        mock_env.return_value = None

        def missing_env_variable():
            input = {
                "id": "id_test",
                "type": "AWS_S3",
                "config": {"key": "key", "bucket": {"from_env": "ENV_TOTO"}},
            }

            StorageConfig(**input)

        self.assertRaisesRegex(
            Exception, "Environment variable ENV_TOTO", missing_env_variable
        )

    def test_incorrect_dict_in_config(self):
        def incorrect_dict_in_config():
            input = {
                "id": "id_test",
                "type": "AWS_S3",
                "config": {"key": {"sub_key": "sub_value"}},
            }

            StorageConfig(**input)

        self.assertRaisesRegex(Exception, "not string", incorrect_dict_in_config)

    def test_int_in_config(self):
        def int_in_config():
            input = {"id": "id_test", "type": "AWS_S3", "config": {"key_int": 1245}}

            StorageConfig(**input)

        self.assertRaisesRegex(Exception, "not string", int_in_config)

    def test_incorrect_storage_type(self):
        def incorrect_storage_type_init():
            input = {"id": "id_test", "type": "NIMPORTE_QUOI", "config": {}}

            StorageConfig(**input)

        self.assertRaisesRegex(
            Exception, "Unknown storage type NIMPORTE_QUOI", incorrect_storage_type_init
        )

    @patch("os.getenv")
    def test_ok(self, mock_getenv):
        mock_getenv.return_value = "toto"

        input = {
            "id": "id_test",
            "type": "AWS_S3",
            "config": {"key": "key", "bucket": {"from_env": "ENV_TOTO"}},
        }

        result = StorageConfig(**input)

        self.assertEqual("id_test", result.id)
        self.assertEqual(StorageType.AWS_S3, result.type)

        expected_config = {"key": "key", "bucket": "toto"}

        self.assertEqual(expected_config, result.config)


FAKE_CURRENT_TIME = datetime(1980, 11, 30, tzinfo=timezone.utc)


class TestBackup(unittest.TestCase):
    def test_asdict_none_value(self):
        backup = Backup(
            crawler_id="AAAA",
            storage_id="XXX",
            status=BackupStatus.PENDING,
            creation_time=FAKE_CURRENT_TIME,
            file_path="/file",
            backup_id=None,
        )

        expected_dict = {
            "crawler_id": "AAAA",
            "storage_id": "XXX",
            "status": "PENDING",
            "creation_time": "1980-11-30T00:00:00.000000Z",
            "file_path": "/file",
        }

        self.assertEqual(expected_dict, asdict(backup, dict_factory=DictFactory))

    def test_asdict_with_value(self):
        backup = Backup(
            crawler_id="AAAA",
            storage_id="XXX",
            status=BackupStatus.PENDING,
            creation_time=FAKE_CURRENT_TIME,
            file_path="/file",
            backup_id="xyz",
        )

        expected_dict = {
            "crawler_id": "AAAA",
            "storage_id": "XXX",
            "status": "PENDING",
            "creation_time": "1980-11-30T00:00:00.000000Z",
            "file_path": "/file",
            "backup_id": "xyz",
        }

        self.assertEqual(expected_dict, asdict(backup, dict_factory=DictFactory))
