import unittest
from dataclasses import asdict
from datetime import datetime, timedelta, timezone

from src.app.models import (Backup, BackupException, BackupStatus, DictFactory,
                            File, Picture, PictureInfo, Storage)

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
        )

        self.maxDiff = None

    def test_record_done(self):
        self.test_picture.backup_list = [self.pending_backup]

        self.test_picture.record_done(
            storage_id=self.pending_backup.storage_id,
            crawler_id=self.pending_backup.crawler_id,
        )

        self.assertEqual(BackupStatus.DONE, self.test_picture.backup_list[0].status)

    def test_record_deleted(self):
        pending_backup_2 = Backup(
            crawler_id="B",
            storage_id="b",
            file_path="/picture_1_large",
            status=BackupStatus.PENDING_DELETE,
            creation_time=OTHER_TEST_TIME,
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
                storage_id="X",
                crawler_id="Y",
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
