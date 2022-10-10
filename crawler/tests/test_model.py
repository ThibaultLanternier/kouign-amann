import unittest
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone

from app.models.backup import BackupRequest, BackupStatus
from app.models.picture import PictureData, PictureOrientation
from app.models.shared import DictFactory


class TestBackupRequest(unittest.TestCase):
    def setUp(self):
        self.backup_request_dict = {
            "crawler_id": "AAA",
            "storage_id": "BBB",
            "file_path": "/file",
            "picture_hash": "acde",
            "status": "PENDING",
            "backup_id": None,
        }

    def test_construct_enum_conversion(self):
        backup_request_class = BackupRequest(**self.backup_request_dict)

        self.assertEqual(BackupStatus.PENDING, backup_request_class.status)

    def test_construct_enum_error(self):
        self.backup_request_dict["status"] = "NIMPORTEQUOI"

        with self.assertRaises(ValueError):
            BackupRequest(**self.backup_request_dict)

    def test_construct_with_actual_enum(self):
        self.backup_request_dict["status"] = BackupStatus.PENDING

        backup_request_class = BackupRequest(**self.backup_request_dict)

        self.assertEqual(BackupStatus.PENDING, backup_request_class.status)


class TestPictureData(unittest.TestCase):
    def setUp(self):
        self.picture_dict = {
            "hash": "c643dbe5e4d60e0a",
            "creation_time": datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc),
            "resolution": (5472, 3648),
            "thumbnail": "THUMBNAIL",
            "picture_path": "fake/path",
            "orientation": PictureOrientation.LANDSCAPE,
        }

        self.picture_data = PictureData(**self.picture_dict)

    def test_asdict(self):
        expected = {
            "hash": "c643dbe5e4d60e0a",
            "creation_time": "2019-11-19T12:46:56.000000Z",
            "resolution": (5472, 3648),
            "thumbnail": "THUMBNAIL",
            "picture_path": "fake/path",
            "orientation": "LANDSCAPE",
        }

        result = asdict(self.picture_data, dict_factory=DictFactory)

        self.assertEqual(expected, result)

    def test_asdict_timezone(self):
        self.picture_data.creation_time = datetime(
            2019, 11, 19, 12, 46, 56, 0, timezone(timedelta(seconds=3600))
        )

        expected = {
            "hash": "c643dbe5e4d60e0a",
            "creation_time": "2019-11-19T11:46:56.000000Z",
            "resolution": (5472, 3648),
            "thumbnail": "THUMBNAIL",
            "picture_path": "fake/path",
            "orientation": "LANDSCAPE",
        }

        result = asdict(self.picture_data, dict_factory=DictFactory)

        self.assertEqual(expected, result)


@dataclass
class TestClass:
    value_1: str
    value_2: str


class TestDictFactory(unittest.TestCase):
    def test_none_field(self):
        test_object = TestClass(value_1="A", value_2=None)

        self.assertEqual(
            {"value_1": "A"}, asdict(test_object, dict_factory=DictFactory)
        )
