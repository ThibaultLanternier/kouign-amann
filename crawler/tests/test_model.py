import unittest
from dataclasses import asdict
from datetime import datetime, timedelta, timezone

from app.models.picture import DictFactory, PictureData


class TestPictureData(unittest.TestCase):
    def setUp(self):
        self.picture_dict = {
            "hash": "c643dbe5e4d60e0a",
            "creation_time": datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc),
            "resolution": (5472, 3648),
            "thumbnail": "THUMBNAIL",
            "picture_path": "fake/path",
        }

        self.picture_data = PictureData(**self.picture_dict)

    def test_asdict(self):
        expected = {
            "hash": "c643dbe5e4d60e0a",
            "creation_time": "2019-11-19T12:46:56.000000Z",
            "resolution": (5472, 3648),
            "thumbnail": "THUMBNAIL",
            "picture_path": "fake/path",
        }

        self.assertEqual(expected, asdict(self.picture_data, dict_factory=DictFactory))

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
        }

        self.assertEqual(expected, asdict(self.picture_data, dict_factory=DictFactory))
