from datetime import date
from pathlib import Path
import unittest

from click import group

from app.tools.picture_grouper import PictureGrouper
from tests.fake import FakePicturePath


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
