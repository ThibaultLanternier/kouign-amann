from datetime import date
from pathlib import Path
import unittest

from click import group

from app.tools.picture_grouper import PictureGroup, PictureGrouper
from tests.fake import FakePicturePath

class TestPictureGroup(unittest.TestCase):
    def setUp(self):
        self._picture_group_not_grouped = PictureGroup([
            FakePicturePath(folder_path=Path("root/NOT_GROUPED"), day=date(2023, 10, 1), hash="hash1"),
            FakePicturePath(folder_path=Path("root/NOT_GROUPED"), day=date(2023, 10, 3), hash="hash2")
        ])

        self._picture_group_partly_grouped = PictureGroup([
            FakePicturePath(folder_path=Path("root/NOT_GROUPED"), day=date(2023, 10, 1), hash="hash1"),
            FakePicturePath(folder_path=Path("root/EVENT-XXX"), day=date(2023, 10, 3), hash="hash2"),
            FakePicturePath(folder_path=Path("root/EVENT-YYY"), day=date(2023, 10, 5), hash="hash3"),
            FakePicturePath(folder_path=Path("root/EVENT-YYY"), day=date(2023, 10, 7), hash="hash4")
        ])
    
    def test_get_folder_path_no_picture_already_grouped(self):
        self.assertEqual(self._picture_group_not_grouped.get_folder_path(), Path("root/2023-10-01 <EVENT_DESCRIPTION>"))

    def test_get_folder_path_picture_already_grouped_in_multiple_folder(self):
        self.assertEqual(self._picture_group_partly_grouped.get_folder_path(), Path("root/EVENT-YYY"))

    def test_list_pictures_to_move(self):
        self.assertEqual(self._picture_group_partly_grouped.list_pictures_to_move(), [
            (Path("root/NOT_GROUPED/hash1.jpg"), Path("root/EVENT-YYY/hash1.jpg")),
            (Path("root/EVENT-XXX/hash2.jpg"), Path("root/EVENT-YYY/hash2.jpg"))
        ])

    def test_list_pictures_to_move_new_folder(self):
        self.assertEqual(self._picture_group_not_grouped.list_pictures_to_move(), [
            (Path("root/NOT_GROUPED/hash1.jpg"), Path("root/2023-10-01 <EVENT_DESCRIPTION>/hash1.jpg")),
            (Path("root/NOT_GROUPED/hash2.jpg"), Path("root/2023-10-01 <EVENT_DESCRIPTION>/hash2.jpg"))
        ])

class TestPictureGrouper(unittest.TestCase):
    def setUp(self):
        self._picture_paths = [
            FakePicturePath(folder_path=Path("root/NOT_GROUPED"), day=date(2023, 10, 1), hash="hash1"),
            FakePicturePath(folder_path=Path("root/EVENT_1"), day=date(2023, 10, 2), hash="hash2"),
            FakePicturePath(folder_path=Path("root/NOT_GROUPED"), day=date(2023, 10, 4), hash="hash3"),
            FakePicturePath(folder_path=Path("root/EVENT_2"), day=date(2023, 10, 5), hash="hash4"),
        ]
        
        return super().setUp()
    
    def test_picture_grouper_default_days_2_paths(self):
        grouper = PictureGrouper([self._picture_paths[0], self._picture_paths[3]])
        grouped_pictures = grouper.group_pictures()

        self.assertEqual(grouped_pictures, [
            [self._picture_paths[0]],
            [self._picture_paths[3]],
        ])
    
    def test_picture_grouper_default_days(self):
        grouper = PictureGrouper(self._picture_paths)
        grouped_pictures = grouper.group_pictures()

        self.assertEqual(grouped_pictures, [
            [self._picture_paths[0], self._picture_paths[1]],
            [self._picture_paths[2], self._picture_paths[3]],
        ])

    def test_picture_grouper_2_days(self):
        grouper = PictureGrouper(self._picture_paths)
        grouped_pictures = grouper.group_pictures(max_days=2)

        self.assertEqual(grouped_pictures, [
            [
                self._picture_paths[0], 
                self._picture_paths[1],
                self._picture_paths[2], 
                self._picture_paths[3]
            ]
        ])
