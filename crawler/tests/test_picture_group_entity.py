import unittest
from datetime import datetime
from pathlib import Path

from app.entities.picture_data import PictureData
from app.entities.picture_group import PictureGroup


class TestPictureGroup(unittest.TestCase):

    def setUp(self):
        self._picture_group_not_grouped: PictureGroup = PictureGroup(
            [
                PictureData(
                    path=Path("root/NOT_GROUPED/hash1.jpg"),
                    creation_date=datetime(2023, 10, 1, 15, 45, 12),
                    hash="hash1",
                ),
                PictureData(
                    path=Path("root/NOT_GROUPED/hash2.jpg"),
                    creation_date=datetime(2023, 10, 3),
                    hash="hash2",
                ),
            ]
        )

        self._picture_group_partly_grouped = PictureGroup(
            [
                PictureData(
                    path=Path("root/NOT_GROUPED/hash1.jpg"),
                    creation_date=datetime(2023, 10, 1),
                    hash="hash1",
                ),
                PictureData(
                    path=Path("root/EVENT-XXX/hash2.jpg"),
                    creation_date=datetime(2023, 10, 3),
                    hash="hash2",
                ),
                PictureData(
                    path=Path("root/EVENT-YYY/hash3.jpg"),
                    creation_date=datetime(2023, 10, 5),
                    hash="hash3",
                ),
                PictureData(
                    path=Path("root/EVENT-YYY/hash4.jpg"),
                    creation_date=datetime(2023, 10, 7),
                    hash="hash4",
                ),
            ]
        )

    def test_get_folder_path_no_picture_already_grouped(self):
        self.assertEqual(
            self._picture_group_not_grouped.get_folder_path(),
            Path("root/2023-10-01 <EVENT_DESCRIPTION>"),
        )

    def test_get_folder_path_picture_already_grouped_in_multiple_folder(self):
        self.assertEqual(
            self._picture_group_partly_grouped.get_folder_path(), Path("root/EVENT-YYY")
        )

    def test_list_pictures_to_move(self):
        pictures_to_move = self._picture_group_partly_grouped.list_pictures_to_move()

        self.assertEqual(
            pictures_to_move,
            [
                (Path("root/NOT_GROUPED/hash1.jpg"), Path("root/EVENT-YYY/hash1.jpg")),
                (Path("root/EVENT-XXX/hash2.jpg"), Path("root/EVENT-YYY/hash2.jpg")),
            ],
        )

    def test_list_pictures_to_move_new_folder(self):
        pictures_to_move = self._picture_group_not_grouped.list_pictures_to_move()

        expected_list = [
            (
                Path("root/NOT_GROUPED/hash1.jpg"),
                Path("root/2023-10-01 <EVENT_DESCRIPTION>/hash1.jpg"),
            ),
            (
                Path("root/NOT_GROUPED/hash2.jpg"),
                Path("root/2023-10-01 <EVENT_DESCRIPTION>/hash2.jpg"),
            ),
        ]

        self.assertEqual(
            pictures_to_move,
            expected_list,
        )
