import unittest
from datetime import date
from pathlib import Path

from app.tools.path import (FileNotFoundException, MalformedFileNameException,
                            PicturePath)


class TestPicturePath(unittest.TestCase):
    def setUp(self):
        return super().setUp()

    def test_picture_path_ok(self):
        test_path = Path(
            "tests/files/photos/2024/ANYTHING/1733616335-e7975821ce2e1a55.jpg"
        )
        picture_path = PicturePath(test_path)

        self.assertEqual(picture_path.get_year(), 2024)
        self.assertEqual(picture_path.get_day(), date(2024, 12, 8))
        self.assertEqual(
            picture_path.get_folder_path(), Path("tests/files/photos/2024/ANYTHING")
        )
        self.assertEqual(picture_path.get_hash(), "e7975821ce2e1a55")

    def test_picture_path_not_exists(self):
        test_path = Path(
            "tests/files/photos/2024/ANYTHING/x-1733616335-e7975821ce2e1a55.jpg"
        )

        def load_picture_path():
            PicturePath(test_path)

        self.assertRaises(FileNotFoundException, load_picture_path)

    def test_picture_path_malformed_name(self):
        test_path = Path(
            "tests/files/photos/2024/ANYTHING/91733616335-e7975821ce2e1a55.jpg"
        )

        def load_picture_path():
            PicturePath(test_path)

        self.assertRaises(MalformedFileNameException, load_picture_path)

    def test_picture_path_should_handle_with_timestamp_zero(self):
        test_path = Path("tests/files/photos/2024/ANYTHING/0-e7975821ce2e1a55.jpg")

        PicturePath(test_path)
