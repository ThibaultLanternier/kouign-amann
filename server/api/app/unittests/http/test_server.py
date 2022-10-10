import logging
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from src.app.models import (Backup, BackupRequest, BackupStatus, File, Picture,
                            PictureCount, PictureInfo, Storage, StorageConfig,
                            StorageType)
from src.app.ports import (AbstractBackupManager, AbstractPictureManager,
                           MissingPictureException)
from src.http.resources import GoogleAuthAccessTokenAnswer
from src.http.server import get_flask_app

FAKE_CURRENT_TIME = datetime(1980, 11, 30, tzinfo=timezone.utc)


class TestSchema(unittest.TestCase):
    def test_google_auth_answer(self):
        input = {
            "access_token": "ya29.",
            "expires_in": 3599,
            "refresh_token": "1//03IcJ",
            "scope": [
                "https://www.googleapis.com/auth/photoslibrary.readonly",
                "https://www.googleapis.com/auth/photoslibrary.appendonly",
            ],
            "token_type": "Bearer",
            "expires_at": 1663104574.3838615,
        }

        GoogleAuthAccessTokenAnswer().load(input)

    def test_google_auth_answer_no_refresh(self):
        input = {
            "access_token": "ya29.",
            "expires_in": 3599,
            "scope": [
                "https://www.googleapis.com/auth/photoslibrary.readonly",
                "https://www.googleapis.com/auth/photoslibrary.appendonly",
            ],
            "token_type": "Bearer",
            "expires_at": 1663104574.3838615,
        }

        GoogleAuthAccessTokenAnswer().load(input)


class TestServer(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        self.app = get_flask_app()
        self.mock_app: AbstractPictureManager = MagicMock(spec=AbstractPictureManager)
        self.app.config["picture_manager"] = self.mock_app

        self.mock_backup_app: AbstractBackupManager = MagicMock(
            spec=AbstractBackupManager
        )
        self.app.config["backup_manager"] = self.mock_backup_app

        self.client = self.app.test_client()

        self.sample_picture = Picture(
            hash="AAAAA",
            info=PictureInfo(
                creation_time=datetime(
                    2019, 11, 30, 12, 15, 5, 2000, tzinfo=timezone.utc
                ),
                thumbnail="BBBBB",
                orientation="LANDSCAPE",
            ),
            file_list=[],
            backup_required=False,
            backup_list=[],
        )

        self.sample_picture_dict = {
            "hash": "AAAAA",
            "backup_required": False,
            "backup_list": [],
            "file_list": [],
            "info": {
                "creation_time": "2019-11-30T12:15:05.002000Z",
                "thumbnail": "BBBBB",
                "orientation": "LANDSCAPE",
            },
        }

    def test_picture_exists_OK(self):
        self.mock_app.get_picture.return_value = MagicMock(spec=Picture)

        response = self.client.get("/picture/exists/AAAAA")

        self.assertEqual(200, response.status_code)
        self.mock_app.get_picture.assert_called_once_with("AAAAA")

    def test_picture_exists_NOT_OK(self):
        self.mock_app.get_picture.return_value = None

        response = self.client.get("/picture/exists/AAAAA")

        self.assertEqual(404, response.status_code)
        self.mock_app.get_picture.assert_called_once_with("AAAAA")

    def test_picture_exists_EXCEPTION(self):
        self.mock_app.get_picture.side_effect = Exception

        response = self.client.get("/picture/exists/AAAAA")

        self.assertEqual(500, response.status_code)
        self.mock_app.get_picture.assert_called_once_with("AAAAA")

    def test_put_picture_file(self):
        test_file_json = {
            "crawler_id": "A",
            "resolution": [12, 12],
            "picture_path": "/path",
            "last_seen": "2019-11-30T12:15:05.000000Z",
        }

        response = self.client.put("/picture/file/AAAAA", json=test_file_json)

        expected_file = File(**test_file_json)
        expected_file.last_seen = datetime(2019, 11, 30, 12, 15, 5, tzinfo=timezone.utc)

        self.assertEqual(201, response.status_code)
        self.mock_app.record_picture_file.assert_called_once_with(
            "AAAAA", expected_file
        )

    def test_put_picture_file_unkown_picture(self):
        test_file_json = {
            "crawler_id": "A",
            "resolution": [12, 12],
            "picture_path": "/path",
            "last_seen": "2019-11-30T12:15:05.000000Z",
        }

        self.mock_app.record_picture_file.side_effect = MissingPictureException

        response = self.client.put("/picture/file/AAAAA", json=test_file_json)

        self.assertEqual(404, response.status_code)

    def test_get_picture_ok(self):
        self.mock_app.get_picture.return_value = Picture(
            hash="AAAAA",
            info=PictureInfo(
                creation_time=datetime(
                    2019, 11, 30, 12, 15, 5, 2000, tzinfo=timezone.utc
                ),
                thumbnail="BBBBB",
                orientation="LANDSCAPE",
            ),
            file_list=[],
            backup_required=False,
            backup_list=[],
        )

        response = self.client.get("/picture/AAAAA")

        expected_content = {
            "hash": "AAAAA",
            "backup_required": False,
            "backup_list": [],
            "file_list": [],
            "info": {
                "creation_time": "2019-11-30T12:15:05.002000Z",
                "thumbnail": "BBBBB",
                "orientation": "LANDSCAPE",
            },
        }

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_content, response.get_json())

    def test_get_picture_missing(self):
        self.mock_app.get_picture.return_value = None

        response = self.client.get("/picture/AAAAA")

        self.assertEqual(404, response.status_code)

    def test_post_picture(self):
        test_info_json = {
            "creation_time": "2019-11-30T12:15:05.000000Z",
            "thumbnail": "BBBBB",
            "orientation": "PORTRAIT",
        }

        response = self.client.post("/picture/AAAAA", json=test_info_json)

        self.assertEqual(201, response.status_code)
        self.mock_app.record_picture_info.assert_called_once_with(
            "AAAAA",
            PictureInfo(
                creation_time=datetime(2019, 11, 30, 12, 15, 5, tzinfo=timezone.utc),
                thumbnail="BBBBB",
                orientation="PORTRAIT",
            ),
        )

    def test_list_recently_updated_pictures(self):
        self.mock_app.list_recently_updated_pictures.return_value = [
            self.sample_picture
        ]

        response = self.client.get("/picture/updated/5")

        self.assertEqual(200, response.status_code)
        self.assertEqual([self.sample_picture_dict], response.get_json())

        self.mock_app.list_recently_updated_pictures.assert_called_once_with(
            duration=timedelta(seconds=5)
        )

    def test_list_picture(self):
        self.mock_app.list_pictures.return_value = [
            Picture(
                hash="AAAAA",
                info=PictureInfo(
                    creation_time=datetime(
                        2019, 11, 30, 12, 15, 5, 2000, tzinfo=timezone.utc
                    ),
                    thumbnail="BBBBB",
                    orientation="LANDSCAPE",
                ),
                file_list=[],
                backup_required=False,
                backup_list=[],
            )
        ]

        response = self.client.get(
            "/picture/list?start=1980-11-30T12:45:12Z&end=1980-12-02T13:45:12Z"
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [
                {
                    "hash": "AAAAA",
                    "backup_required": False,
                    "backup_list": [],
                    "file_list": [],
                    "info": {
                        "creation_time": "2019-11-30T12:15:05.002000Z",
                        "thumbnail": "BBBBB",
                        "orientation": "LANDSCAPE",
                    },
                }
            ],
            response.get_json(),
        )

        self.mock_app.list_pictures.assert_called_once_with(
            datetime(1980, 11, 30, 12, 45, 12, 0, timezone.utc),
            datetime(1980, 12, 2, 13, 45, 12, 0, timezone.utc),
        )

    def test_picture_count(self):
        self.mock_app.count.return_value = [
            PictureCount(
                date=datetime(1980, 11, 30, 12, 11, 5, 456, tzinfo=timezone.utc),
                count=35,
                start_date=datetime(1980, 11, 30, 11, 42, tzinfo=timezone.utc),
                end_date=datetime(1980, 12, 2, 14, 37, 25, tzinfo=timezone.utc),
            )
        ]

        response = self.client.get("/picture/count")

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [
                {
                    "count": 35,
                    "date": "1980-11-30T12:11:05.000456Z",
                    "end_date": "1980-12-02T14:37:25.000000Z",
                    "start_date": "1980-11-30T11:42:00.000000Z",
                }
            ],
            response.get_json(),
        )

    @patch("src.http.resources.datetime")
    def test_backup_plan_image(self, mock_date_time):
        mock_date_time.utcnow.return_value = FAKE_CURRENT_TIME

        mock_storage_list = [Storage(id="storage")]
        self.mock_backup_app.get_storages.return_value = mock_storage_list

        mock_picture = MagicMock(spec=Picture)
        self.mock_app.get_picture.return_value = mock_picture

        response = self.client.put("/backup/plan/AAAA")

        self.assertEqual(201, response.status_code)
        mock_picture.plan_backup.assert_called_once_with(
            storage_list=mock_storage_list, current_time=FAKE_CURRENT_TIME
        )

        self.mock_app.record_picture.assert_called_once_with(mock_picture)

    def test_backup_plan_image_not_found(self):
        self.mock_app.get_picture.return_value = None

        response = self.client.put("/backup/plan/AAAA")

        self.assertEqual(404, response.status_code)

    def test_get_backup_plan(self):
        backup = Backup(
            crawler_id="AAAA",
            storage_id="XXX",
            status=BackupStatus.PENDING,
            creation_time=FAKE_CURRENT_TIME,
            file_path="/file",
            backup_id=None
        )

        picture = Picture(
            **{
                "hash": "AAAAA",
                "backup_required": False,
                "backup_list": [backup],
                "file_list": [],
                "info": {
                    "creation_time": FAKE_CURRENT_TIME,
                    "thumbnail": "BBBBB",
                },
            }
        )
        self.mock_app.get_picture.return_value = picture

        response = self.client.get("/backup/plan/AAAA")

        self.assertEqual(200, response.status_code)
        self.assertEqual(
            [
                {
                    "crawler_id": "AAAA",
                    "storage_id": "XXX",
                    "status": "PENDING",
                    "creation_time": "1980-11-30T00:00:00.000000Z",
                    "file_path": "/file"
                }
            ],
            response.get_json(),
        )

    def test_backup(self):
        picture_dict = {
            "hash": "AAAAA",
            "backup_required": False,
            "backup_list": [],
            "file_list": [],
            "info": {
                "creation_time": FAKE_CURRENT_TIME,
                "thumbnail": "BBBBB",
            },
        }

        picture = Picture(**picture_dict)
        self.mock_app.get_picture.return_value = picture

        response = self.client.post("/backup/request/AAAA")

        expected_picture_dict = picture_dict.copy()
        expected_picture_dict["backup_required"] = True
        expected_picture = Picture(**expected_picture_dict)

        self.assertEqual(201, response.status_code)
        self.mock_app.record_picture.assert_called_once_with(expected_picture)

    def test_backup_delete(self):
        picture_dict = {
            "hash": "AAAAA",
            "backup_required": True,
            "backup_list": [],
            "file_list": [],
            "info": {
                "creation_time": FAKE_CURRENT_TIME,
                "thumbnail": "BBBBB",
            },
        }

        picture = Picture(**picture_dict)
        self.mock_app.get_picture.return_value = picture

        response = self.client.delete("/backup/request/AAAA")

        expected_picture_dict = picture_dict.copy()
        expected_picture_dict["backup_required"] = False
        expected_picture = Picture(**expected_picture_dict)

        self.assertEqual(201, response.status_code)
        self.mock_app.record_picture.assert_called_once_with(expected_picture)

    def test_crawler_get_backup_list(self):
        backup_request_dict = {
            "crawler_id": "AAA",
            "storage_id": "BBB",
            "file_path": "/file",
            "picture_hash": "acde",
            "status": "PENDING"
        }

        backup_request = BackupRequest(backup_id=None, **backup_request_dict)

        self.mock_backup_app.get_pending_backup_request.return_value = [backup_request]

        response = self.client.get("/crawler/backup/AAA")
        self.assertEqual(200, response.status_code)
        self.assertEqual([backup_request_dict], response.get_json())
        self.mock_backup_app.get_pending_backup_request.assert_called_once_with(
            crawler_id="AAA", limit=20
        )

    def test_crawler_record_file_save_complete(self):
        backup_request_dict = {
            "crawler_id": "AAA",
            "storage_id": "BBB",
            "file_path": "/file",
            "picture_hash": "acde",
            "status": "PENDING",
            "backup_id": "ABCDEF"
        }

        mock_picture = MagicMock(spec=Picture)
        self.mock_app.get_picture.return_value = mock_picture

        response = self.client.post("/crawler/backup/xxx", json=backup_request_dict)

        self.assertEqual(201, response.status_code)
        mock_picture.record_done.assert_called_once_with(
            storage_id="BBB", crawler_id="AAA", backup_id="ABCDEF"
        )
        self.mock_app.record_picture.assert_called_once_with(picture=mock_picture)

    def test_crawler_record_file_delete_completed(self):
        backup_request_dict = {
            "crawler_id": "AAA",
            "storage_id": "BBB",
            "file_path": "/file",
            "picture_hash": "acde",
            "status": "PENDING_DELETE",
        }

        mock_picture = MagicMock(spec=Picture)
        self.mock_app.get_picture.return_value = mock_picture

        response = self.client.post("/crawler/backup/xxx", json=backup_request_dict)

        self.assertEqual(201, response.status_code)
        mock_picture.record_deleted.assert_called_once_with(
            storage_id="BBB", crawler_id="AAA"
        )
        self.mock_app.record_picture.assert_called_once_with(picture=mock_picture)

    def test_crawler_record_backup_with_incorrect_status(self):
        backup_request_dict = {
            "crawler_id": "AAA",
            "storage_id": "BBB",
            "file_path": "/file",
            "picture_hash": "acde",
            "status": "DONE",
        }

        mock_picture = MagicMock(spec=Picture)
        self.mock_app.get_picture.return_value = mock_picture

        response = self.client.post("/crawler/backup/xxx", json=backup_request_dict)

        self.assertEqual(400, response.status_code)

    def test_crawler_record_file_save_error(self):
        backup_request_dict = {
            "crawler_id": "AAA",
            "storage_id": "BBB",
            "file_path": "/file",
            "picture_hash": "acde",
            "status": "PENDING",
        }

        mock_picture = MagicMock(spec=Picture)
        self.mock_app.get_picture.return_value = mock_picture

        response = self.client.delete("/crawler/backup/xxx", json=backup_request_dict)

        self.assertEqual(201, response.status_code)
        mock_picture.record_backup_error.assert_called_once_with(
            storage_id="BBB", crawler_id="AAA"
        )
        self.mock_app.record_picture.assert_called_once_with(picture=mock_picture)

    def test_crawler_record_file_save_unknown_file(self):
        backup_request_dict = {
            "crawler_id": "AAA",
            "storage_id": "BBB",
            "file_path": "/file",
            "picture_hash": "acde",
            "status": "PENDING",
        }

        self.mock_app.get_picture.return_value = None

        response = self.client.post("/crawler/backup/xxx", json=backup_request_dict)

        self.assertEqual(404, response.status_code)

    def test_crawler_get_storage_config(self):
        storage_config = StorageConfig(
            id="xxx", type=StorageType.AWS_GLACIER, config={"config": "config"}
        )

        self.mock_backup_app.get_storage_config.return_value = storage_config

        expected_answer = {
            "id": "xxx",
            "type": "AWS_GLACIER",
            "config": {"config": "config"},
        }

        response = self.client.get("/crawler/storage/xxx")
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_answer, response.get_json())
        self.mock_backup_app.get_storage_config.assert_called_once_with("xxx")
