import unittest
from datetime import date
from pathlib import Path

from app.tools.path_manager import PicturePathManager
from tests.fake import FakePicturePath

class TestPicturePathManager(unittest.TestCase):
    _path_manager: PicturePathManager

    def setUp(self):
        picture_path_1 = FakePicturePath(
            folder_path=Path("day/2024-12-08"), day=date(2024, 12, 8), hash="xxx"
        )

        self._path_manager = PicturePathManager(
            [picture_path_1], root_folder=Path("root_folder")
        )

        return super().setUp()

    def test_picture_path_manager_return_new_folder_if_not_exists(self):
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 6)),
            Path("root_folder/2024/2024-12-06 <EVENT_DESCRIPTION>"),
        )

    def test_picture_path_manager_return_existing_if_day_exists(self):
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 8)),
            Path("day/2024-12-08"),
        )

    def test_picture_path_manager_return_existing_if_next_day_exists(self):
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 7)),
            Path("day/2024-12-08"),
        )

    def test_picture_path_manager_return_existing_if_previous_day_exists(self):
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 9)),
            Path("day/2024-12-08"),
        )

    @unittest.skip("Not implemented yet")
    def test_picture_path_manager_should_regroup(self):
        self.assertEqual(
            self._path_manager._by_day, {date(2024, 12, 8): Path("day/2024-12-08")}
        )

        self._path_manager.add_picture_path(
            FakePicturePath(
                folder_path=Path("day/2024-12-10"), day=date(2024, 12, 10), hash="yyy"
            )
        )

        self.assertEqual(
            self._path_manager._by_day,
            {
                date(2024, 12, 8): Path("day/2024-12-08"),
                date(2024, 12, 10): Path("day/2024-12-10"),
            },
        )

        self._path_manager.add_picture_path(
            FakePicturePath(
                folder_path=Path("day/2024-12-09"), day=date(2024, 12, 9), hash="yyy"
            )
        )

        self.assertEqual(
            self._path_manager._by_day,
            {
                date(2024, 12, 8): Path("day/2024-12-08"),
                date(2024, 12, 9): Path("day/2024-12-08"),
                date(2024, 12, 10): Path("day/2024-12-08"),
            },
        )

    def test_picture_path_manager_should_link_adjacent_days(self):
        self._path_manager.add_picture_path(
            FakePicturePath(
                folder_path=Path("day/2024-12-10"), day=date(2024, 12, 10), hash="yyy"
            )
        )
        # One folder for December 8th and one for december 10th
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 7)),
            Path("day/2024-12-08"),
        )
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 8)),
            Path("day/2024-12-08"),
        )
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 9)),
            Path("day/2024-12-08"),
        )
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 10)),
            Path("day/2024-12-10"),
        )
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 11)),
            Path("day/2024-12-10"),
        )

        # Adding December 9th to bridge the gap
        self._path_manager.add_picture_path(
            FakePicturePath(
                folder_path=Path("day/2024-12-09"), day=date(2024, 12, 9), hash="zzz"
            )
        )

        # Continuous serie for December 8th, 9th and 10th
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 8)),
            Path("day/2024-12-08"),
        )
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 9)),
            Path("day/2024-12-08"),
        )
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 10)),
            Path("day/2024-12-08"),
        )
        self.assertEqual(
            self._path_manager.get_folder_path(date(2024, 12, 11)),
            Path("day/2024-12-08"),
        )
