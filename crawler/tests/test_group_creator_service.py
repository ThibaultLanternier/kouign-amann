import unittest
from datetime import datetime
from pathlib import Path

from app.entities.picture_data import PictureData
from app.entities.picture_group import PictureGroup
from app.services.group_creator import GroupCreatorService


class TestGroupCreatorService(unittest.TestCase):
    def setUp(self):
        self._picture_list = [
            PictureData(
                path=Path("root/NOT_GROUPED/hash1.jpg"),
                creation_date=datetime(2023, 10, 1),
                hash="hash1",
            ),
            PictureData(
                path=Path("root/EVENT_1/hash2.jpg"),
                creation_date=datetime(2023, 10, 2),
                hash="hash2",
            ),
            PictureData(
                path=Path("root/NOT_GROUPED/hash3.jpg"),
                creation_date=datetime(2023, 10, 4),
                hash="hash3",
            ),
            PictureData(
                path=Path("root/EVENT_2/hash4.jpg"),
                creation_date=datetime(2023, 10, 5),
                hash="hash4",
            ),
        ]

        self._picture_list_hours = [
            PictureData(
                path=Path("root/NOT_GROUPED/hash1.jpg"),
                creation_date=datetime(2023, 10, 1, 10),
                hash="hash1",
            ),
            PictureData(
                path=Path("root/EVENT_1/hash2.jpg"),
                creation_date=datetime(2023, 10, 1, 11),
                hash="hash2",
            ),
            PictureData(
                path=Path("root/NOT_GROUPED/hash3.jpg"),
                creation_date=datetime(2023, 10, 1, 13),
                hash="hash3",
            ),
            PictureData(
                path=Path("root/EVENT_2/hash4.jpg"),
                creation_date=datetime(2023, 10, 1, 14),
                hash="hash4",
            ),
        ]

        return super().setUp()

    def test_group_creator_service_from_folders_ok(self):
        grouper = GroupCreatorService()
        grouped_pictures = grouper.get_group_list_from_folders(self._picture_list)

        self.assertEqual(
            [x.get_picture_list() for x in grouped_pictures],
            [
                [self._picture_list[0], self._picture_list[2]],
                [self._picture_list[1]],
                [self._picture_list[3]],
            ],
        )

    def test_group_creator_service_1_value(self):
        grouper = GroupCreatorService(hours_btw_picture=1)
        grouped_pictures = grouper.get_group_list_from_time(
            [self._picture_list_hours[0]]
        )

        self.assertEqual(
            [[picture.get_hash() for picture in x.get_picture_list()] for x in grouped_pictures],
            [
                ["hash1"],
            ],
        )

    def test_group_creator_service_1hour_time_difference(self):
        grouper = GroupCreatorService(hours_btw_picture=1)
        grouped_pictures = grouper.get_group_list_from_time(self._picture_list_hours)

        self.assertEqual(
            [[picture.get_hash() for picture in x.get_picture_list()] for x in grouped_pictures],
            [
                ["hash1", "hash2"],
                ["hash3", "hash4"],
            ]
        )

    def test_group_creator_service_2hours_time_difference(self):
        grouper = GroupCreatorService(hours_btw_picture=2)
        grouped_pictures = grouper.get_group_list_from_time(self._picture_list_hours)

        self.assertEqual(
            [[picture.get_hash() for picture in x.get_picture_list()] for x in grouped_pictures],
            [
                ["hash1", "hash2", "hash3", "hash4"]
            ],
        )

    def test_group_creator_service_default_days_2_paths(self):
        grouper = GroupCreatorService()
        grouped_pictures = grouper.get_group_list_from_time(
            [self._picture_list[0], self._picture_list[3]]
        )

        self.assertEqual(
            [[picture.get_hash() for picture in x.get_picture_list()] for x in grouped_pictures],
            [
                ["hash1"],
                ["hash4"],
            ],
        )

    def test_group_creator_service_default_days(self):
        grouper = GroupCreatorService()
        grouped_pictures = grouper.get_group_list_from_time(self._picture_list)

        self.assertEqual(
            [[picture.get_hash() for picture in x.get_picture_list()] for x in grouped_pictures],
            [
                ["hash1", "hash2"],
                ["hash3", "hash4"]
            ],
        )

    def test_group_creator_service_2_days(self):
        grouper = GroupCreatorService(hours_btw_picture=48)
        grouped_pictures = grouper.get_group_list_from_time(self._picture_list)

        self.assertEqual(
            [[picture.get_hash() for picture in x.get_picture_list()] for x in grouped_pictures],
            [
                ["hash1", "hash2", "hash3", "hash4"],
            ],
        )
    
    def test_group_creator_service_2_days_with_group_break(self):
        grouper = GroupCreatorService(hours_btw_picture=48)
        
        # Adding a group break to the third picture
        self._picture_list[2] = PictureData(
            path=self._picture_list[2].get_path(),
            creation_date=self._picture_list[2].get_creation_date(),
            hash=self._picture_list[2].get_hash(),
            group_break=True,
        )
        
        grouped_pictures = grouper.get_group_list_from_time(self._picture_list)

        self.assertEqual(
            [[picture.get_hash() for picture in x.get_picture_list()] for x in grouped_pictures],
            [
                ["hash1", "hash2"],
                ["hash3","hash4"],
            ],
        )
    

