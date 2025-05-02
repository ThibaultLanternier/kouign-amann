import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.entities.picture import Picture

TEST_PICTURE_CAMERA = "tests/files/test-canon-eos70D-exif.jpg"
TEST_PICTURE_OLD_SCAN_2 = "tests/files/0001.jpg"


class TestPictureEntity(unittest.TestCase):
    def test_get_exif_creation_time_old_picture(self):
        picture = Picture(path=Path(TEST_PICTURE_OLD_SCAN_2))

        self.assertEqual(
            datetime(1970, 1, 1, tzinfo=timezone.utc),
            picture.get_exif_creation_time(),
        )

    def test_get_exif_creation_time_recent_picture(self):
        picture = Picture(path=Path(TEST_PICTURE_CAMERA))

        self.assertEqual(
            datetime(2019, 11, 19, 12, 46, 56, tzinfo=timezone.utc),
            picture.get_exif_creation_time(),
        )

    def test_get_hash(self):
        picture = Picture(path=Path("tests/files/test-canon-eos70D.jpg"))

        expected_hash = "c643dbe5e4d60f02"

        self.assertEqual(expected_hash, picture.get_hash())
