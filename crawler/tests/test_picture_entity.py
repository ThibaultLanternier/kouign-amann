import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.entities.picture import (HasherException, MalformedImageFileException,
                                  Picture)
from app.entities.picture_data import PictureData

TEST_PICTURE_CAMERA = "tests/files/test-canon-eos70D-exif.jpg"
TEST_PICTURE_OLD_SCAN_2 = "tests/files/0001.jpg"

DEFAULT_CREATION_TIME = datetime(1970, 1, 1, tzinfo=timezone.utc)


class TestPictureEntity(unittest.TestCase):
    def test_get_exif_creation_time_old_picture(self):
        picture = Picture(path=Path(TEST_PICTURE_OLD_SCAN_2))

        self.assertEqual(
            DEFAULT_CREATION_TIME,
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

    def test_get_exif_malformed_throws_exception(self):
        def create_picture():
            Picture(path=Path("tests/files/not_a_jpeg.jpg"))

        self.assertRaises(MalformedImageFileException, create_picture)

    def test_get_hash_broken_jpeg_throws_exception(self):
        def create_picture():
            picture = Picture(path=Path("tests/files/broken_jpg_image.jpg"))
            picture.get_hash()

        self.assertRaises(HasherException, create_picture)

    def test_get_exif_creation_time_no_exif(self):
        # Note: It seems difficult to creat pictures without any EXIF data ?
        picture = Picture(path=Path("tests/files/foto_no_exif.jpg"))

        self.assertEqual(DEFAULT_CREATION_TIME, picture.get_exif_creation_time())
