from datetime import datetime, timezone
from pathlib import Path
import unittest

from app.factories.picture_data import (NotStandardFileNameException,
                                        PictureDataFactory)


class TestPictureDataFactory(unittest.TestCase):
    def test_from_standard_path_OK(self):
        test_path = Path(
            "tests/files/photos/2024/ANYTHING/1733616335-e7975821ce2e1a55.jpg"
        )
        picture_data = PictureDataFactory().from_standard_path(path=test_path, current_timezone=timezone.utc)

        self.assertEqual(
            picture_data.get_creation_date(),
            datetime(2024, 12, 8, 0, 5, 35, tzinfo=timezone.utc),
        )
        self.assertEqual(picture_data.get_path(), test_path)
        self.assertEqual(picture_data.get_hash(), "e7975821ce2e1a55")
        self.assertFalse(picture_data.is_group_break())

    def test_from_standard_path_with_group_break(self):
        test_path_with_group_break = Path(
            "tests/files/photos/2024/ANYTHING/1609459200-abcdef1234567890-x.jpg"
        )
        picture_data = PictureDataFactory().from_standard_path(path=test_path_with_group_break, current_timezone=timezone.utc)

        self.assertEqual(
            picture_data.get_creation_date(),
            datetime(2021, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(picture_data.get_path(), test_path_with_group_break)
        self.assertEqual(picture_data.get_hash(), "abcdef1234567890")
        self.assertTrue(picture_data.is_group_break())

    def test_from_standard_path_incorrect_path_throws(self):
        test_path = Path("tests/files/photos/2024/ANYTHING/testXXX.jpg")

        def create_from_standard_path():
            PictureDataFactory().from_standard_path(path=test_path, current_timezone=timezone.utc)

        self.assertRaises(NotStandardFileNameException, create_from_standard_path)
