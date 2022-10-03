import unittest
from datetime import datetime, timedelta, timezone

from pymongo import MongoClient

from src.app.models import (Backup, BackupRequest, BackupStatus, File,
                            GoogleAccessToken, GoogleRefreshToken, Picture,
                            PictureCount, PictureInfo)
from src.persistence.adapteurs import (MongoCredentialsPersistence,
                                       MongoPersistence)

CURRENT_TIME = datetime(1980, 11, 30, tzinfo=timezone.utc)


class TestMongoCredentialsPersistence(unittest.TestCase):
    def setUp(self):
        self.client = MongoClient("mongodb-test", 27017, tz_aware=True)
        self.db_name = "credentials-test"
        self.persistence = MongoCredentialsPersistence(
            client=self.client, db_name=self.db_name
        )

    def test_get_current_state(self):
        self.assertIsNotNone(self.persistence.get_current_state())

    def test_retrieve_record_refresh_token(self):
        self.assertIsNone(self.persistence.get_refresh_token())

        token_1 = GoogleRefreshToken(
            refresh_token="aaa",
            scope=[],
            issued_at=datetime(1980, 11, 1, 13, 15, 1, tzinfo=timezone.utc),
        )

        token_2 = GoogleRefreshToken(
            refresh_token="aaa",
            scope=[],
            issued_at=datetime(1980, 11, 1, 13, 14, 1, tzinfo=timezone.utc),
        )

        self.persistence.record_refresh_token(token_1)
        self.persistence.record_refresh_token(token_2)

        self.assertEqual(token_1, self.persistence.get_refresh_token())

    def test_retrieve_record_access_token(self):
        self.assertIsNone(self.persistence.get_access_token())

        token_1 = GoogleAccessToken(
            **{
                "access_token": "ya29",
                "scope": [
                    "https://www.googleapis.com/auth/photoslibrary.readonly",
                    "https://www.googleapis.com/auth/photoslibrary.appendonly",
                ],
                "token_type": "Bearer",
                "expires_at": datetime(1980, 11, 1, 13, 15, 1, tzinfo=timezone.utc),
            }
        )

        token_2 = GoogleAccessToken(
            **{
                "access_token": "wZ42",
                "scope": [
                    "https://www.googleapis.com/auth/photoslibrary.readonly",
                    "https://www.googleapis.com/auth/photoslibrary.appendonly",
                ],
                "token_type": "Bearer",
                "expires_at": datetime(1980, 11, 1, 13, 12, 1, tzinfo=timezone.utc),
            }
        )

        self.persistence.record_access_token(token_1)
        self.persistence.record_access_token(token_2)

        self.assertEqual(token_1, self.persistence.get_access_token())

    def tearDown(self):
        self.client.drop_database(self.db_name)


class TestMongoPersistence(unittest.TestCase):
    def _create_backup(self, status: BackupStatus = BackupStatus.DONE) -> Backup:
        return Backup(
            crawler_id="AAA",
            storage_id="BBB",
            file_path="/file",
            status=status,
            creation_time=CURRENT_TIME,
        )

    def _create_backup_request(self, backup: Backup, picture: Picture) -> BackupRequest:
        return BackupRequest(
            crawler_id=backup.crawler_id,
            storage_id=backup.storage_id,
            file_path=backup.file_path,
            picture_hash=picture.hash,
            status=backup.status,
        )

    def _create_file(self) -> File:
        return File(
            crawler_id="AAA",
            resolution=(12, 12),
            picture_path="/file",
            last_seen=CURRENT_TIME,
        )

    def _create_picture(self, hash: str, creation_time: datetime) -> Picture:
        picture_info = PictureInfo(
            creation_time=creation_time,
            thumbnail="/9j/4AAQSkZ",
            orientation="LANDSCAPE",
        )

        return Picture(
            hash=hash,
            info=picture_info,
            backup_required=False,
            file_list=[],
            backup_list=[],
        )

    def setUp(self):
        self.client = MongoClient("mongodb-test", 27017, tz_aware=True)
        self.db_name = "test-db"
        # self.client.drop_database(self.db_name)

        self.persistence = MongoPersistence(client=self.client, db_name=self.db_name)

        self.test_hash = "c643dbe5e4d60e0a"
        self.test_picture = self._create_picture(
            hash=self.test_hash,
            creation_time=datetime(2019, 11, 19, 12, 46, 56, tzinfo=timezone.utc),
        )

        self.test_picture_2 = self._create_picture(
            hash="BBBBBB",
            creation_time=datetime(2019, 11, 19, 12, 48, 12, tzinfo=timezone.utc),
        )

        self.assertIsNone(self.persistence.get_picture(self.test_hash))

    def tearDown(self):
        self.client.drop_database(self.db_name)

    def test_get_pending_backup_request_all_done(self):
        self.test_picture.backup_list = [self._create_backup(status=BackupStatus.DONE)]

        self.persistence.record_picture(self.test_picture)

        self.assertEqual(
            [], self.persistence.get_pending_backup_request(crawler_id="AAA", limit=10)
        )

    def test_get_pending_backup_request_done_and_pending(self):
        pending_backup = self._create_backup(status=BackupStatus.PENDING)
        pending_delete_backup = self._create_backup(status=BackupStatus.PENDING_DELETE)

        self.test_picture.backup_list = [
            self._create_backup(status=BackupStatus.DONE),
            pending_backup,
            pending_delete_backup,
        ]

        expected_backup_request = self._create_backup_request(
            backup=pending_backup, picture=self.test_picture
        )
        expected_backup_delete_request = self._create_backup_request(
            backup=pending_delete_backup, picture=self.test_picture
        )
        self.persistence.record_picture(self.test_picture)

        backup_list = self.persistence.get_pending_backup_request(
            crawler_id="AAA", limit=10
        )
        self.maxDiff = None

        self.assertEqual(
            [expected_backup_request, expected_backup_delete_request], backup_list
        )

    def test_get_pending_backup_limit(self):
        self.test_picture.backup_list = [
            self._create_backup(status=BackupStatus.PENDING),
            self._create_backup(status=BackupStatus.PENDING),
        ]

        self.persistence.record_picture(self.test_picture)

        backup_list = self.persistence.get_pending_backup_request(
            crawler_id="AAA", limit=1
        )

        self.assertEqual(
            1,
            len(backup_list),
        )

    def test_get_pending_backup_no_matching_crawler_id(self):
        self.test_picture.backup_list = [
            self._create_backup(status=BackupStatus.PENDING)
        ]
        self.persistence.record_picture(self.test_picture)

        backup_list = self.persistence.get_pending_backup_request(
            crawler_id="BBB", limit=10
        )

        self.assertEqual(
            [],
            backup_list,
        )

    def test_record(self):
        self.persistence.record_picture(self.test_picture)

        self.assertEqual(
            self.test_picture, self.persistence.get_picture(self.test_hash)
        )

    def test_record_with_updated_on(self):
        test_datetime = datetime(1980, 11, 30, 12, 10, 0, tzinfo=timezone.utc)

        self.persistence.record_picture(
            picture=self.test_picture, updated_on=test_datetime
        )

        updated_picture = self.client[self.db_name].pictures.find_one(
            {"hash": self.test_picture.hash}
        )
        self.assertEqual(test_datetime, updated_picture["updated_on"])

    def test_record_with_updated_on_default(self):
        test_now = datetime.now(tz=timezone.utc)

        self.persistence.record_picture(picture=self.test_picture)

        updated_picture = self.client[self.db_name].pictures.find_one(
            {"hash": self.test_picture.hash}
        )

        time_difference = test_now - updated_picture["updated_on"]
        self.assertLess(time_difference, timedelta(seconds=1))

    def test_list_recently_updated_pictures(self):
        self.persistence.record_picture(self.test_picture)

        list_pictures = self.persistence.list_recently_updated_pictures(
            timedelta(seconds=1)
        )

        self.assertEqual(1, len(list_pictures))

    def test_record_bckp_and_file(self):
        self.test_picture.backup_list = [self._create_backup()]
        self.test_picture.file_list = [self._create_file()]

        self.persistence.record_picture(self.test_picture)
        recorded_picture = self.persistence.get_picture(self.test_hash)

        self.assertEqual(self.test_picture, recorded_picture)

        self.assertEqual(
            self.test_picture.backup_list[0].status,
            recorded_picture.backup_list[0].status,
        )

    def test_record_update(self):
        self.persistence.record_picture(self.test_picture)
        self.test_picture.info.creation_time = datetime(
            1980, 11, 30, 12, 10, 12, tzinfo=timezone.utc
        )
        self.persistence.record_picture(self.test_picture)

        result = self.persistence.get_picture(self.test_hash)

        self.assertEqual(self.test_picture, result)

    def test_list_ok_order(self):
        self.persistence.record_picture(self.test_picture_2)
        self.persistence.record_picture(self.test_picture)
        test_picture_3 = self._create_picture(
            hash="CCCCC",
            creation_time=datetime(2019, 11, 19, 12, 47, 12, tzinfo=timezone.utc),
        )
        self.persistence.record_picture(test_picture_3)

        result = self.persistence.list_pictures(
            start=datetime(2019, 11, 19, 12, 46, 56, tzinfo=timezone.utc),
            end=datetime(2019, 11, 19, 12, 49, 57, tzinfo=timezone.utc),
        )

        self.assertEqual(
            [self.test_picture, test_picture_3, self.test_picture_2],
            result,
        )

    def test_list_ok(self):
        self.persistence.record_picture(self.test_picture)
        self.persistence.record_picture(self.test_picture)
        self.persistence.record_picture(self.test_picture_2)

        self.assertEqual(
            [self.test_picture],
            self.persistence.list_pictures(
                start=datetime(2019, 11, 19, 12, 46, 56, tzinfo=timezone.utc),
                end=datetime(2019, 11, 19, 12, 46, 57, tzinfo=timezone.utc),
            ),
        )

    def test_list_timezone(self):
        test_picture = self._create_picture(
            "ZZZZZ",
            datetime(1980, 11, 30, 12, 15, tzinfo=timezone(timedelta(seconds=3600))),
        )

        self.persistence.record_picture(test_picture)

        self.assertEqual(
            [test_picture],
            self.persistence.list_pictures(
                start=datetime(1980, 11, 30, 11, 15, tzinfo=timezone.utc),
                end=datetime(1980, 11, 30, 11, 16, tzinfo=timezone.utc),
            ),
        )

        self.assertEqual(
            [],
            self.persistence.list_pictures(
                start=datetime(1980, 11, 30, 12, 15, tzinfo=timezone.utc),
                end=datetime(1980, 11, 30, 12, 16, tzinfo=timezone.utc),
            ),
        )

    def test_list_not_ok(self):
        self.persistence.record_picture(self.test_picture)
        self.persistence.record_picture(self.test_picture_2)

        result = self.persistence.list_pictures(
            start=datetime(2019, 11, 20, 12, 47, 57, tzinfo=timezone.utc),
            end=datetime(2019, 11, 20, 12, 47, 58, tzinfo=timezone.utc),
        )

        self.assertEqual(
            [],
            result,
        )

    def test_count_picture(self):
        date_november = datetime(1980, 11, 30, 12, 10, 5, tzinfo=timezone.utc)
        date_december = datetime(1980, 12, 2, 12, 10, 5, tzinfo=timezone.utc)

        self.persistence.record_picture(
            self._create_picture(
                "AAAA",
                date_november,
            )
        )

        self.persistence.record_picture(
            self._create_picture(
                "BBBBB",
                date_december,
            )
        )

        result = self.persistence.count_picture()

        self.assertEqual(
            result,
            [
                PictureCount(datetime(1980, 11, 1), 1, date_november, date_november),
                PictureCount(datetime(1980, 12, 1), 1, date_december, date_december),
            ],
        )
