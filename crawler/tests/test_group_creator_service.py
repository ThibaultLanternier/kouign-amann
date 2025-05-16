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

    def test_group_creator_service_1_value(self):
        grouper = GroupCreatorService(hours_btw_picture=1)
        grouped_pictures = grouper.get_group_list([self._picture_list_hours[0]])

        self.assertEqual(
            [x.get_picture_list() for x in grouped_pictures],
            [
                PictureGroup([self._picture_list_hours[0]]).get_picture_list(),
            ],
        )

    def test_group_creator_service_1hour_time_difference(self):
        grouper = GroupCreatorService(hours_btw_picture=1)
        grouped_pictures = grouper.get_group_list(self._picture_list_hours)

        self.assertEqual(
            [x.get_picture_list() for x in grouped_pictures],
            [
                PictureGroup(
                    [self._picture_list_hours[0], self._picture_list_hours[1]]
                ).get_picture_list(),
                PictureGroup(
                    [
                        self._picture_list_hours[2],
                        self._picture_list_hours[3],
                    ]
                ).get_picture_list(),
            ],
        )

    def test_group_creator_service_2hours_time_difference(self):
        grouper = GroupCreatorService(hours_btw_picture=2)
        grouped_pictures = grouper.get_group_list(self._picture_list_hours)

        self.assertEqual(
            [x.get_picture_list() for x in grouped_pictures],
            [
                PictureGroup(
                    [
                        self._picture_list_hours[0],
                        self._picture_list_hours[1],
                        self._picture_list_hours[2],
                        self._picture_list_hours[3],
                    ]
                ).get_picture_list()
            ],
        )

    def test_group_creator_service_default_days_2_paths(self):
        grouper = GroupCreatorService()
        grouped_pictures = grouper.get_group_list(
            [self._picture_list[0], self._picture_list[3]]
        )

        self.assertEqual(
            [x.get_picture_list() for x in grouped_pictures],
            [
                PictureGroup([self._picture_list[0]]).get_picture_list(),
                PictureGroup([self._picture_list[3]]).get_picture_list(),
            ],
        )

    def test_group_creator_service_default_days(self):
        grouper = GroupCreatorService()
        grouped_pictures = grouper.get_group_list(self._picture_list)

        self.assertEqual(
            [x.get_picture_list() for x in grouped_pictures],
            [
                PictureGroup(
                    [self._picture_list[0], self._picture_list[1]]
                ).get_picture_list(),
                PictureGroup(
                    [self._picture_list[2], self._picture_list[3]]
                ).get_picture_list(),
            ],
        )

    def test_group_creator_service_2_days(self):
        grouper = GroupCreatorService(hours_btw_picture=48)
        grouped_pictures = grouper.get_group_list(self._picture_list)

        self.assertEqual(
            [x.get_picture_list() for x in grouped_pictures],
            [
                PictureGroup(
                    [
                        self._picture_list[0],
                        self._picture_list[1],
                        self._picture_list[2],
                        self._picture_list[3],
                    ]
                ).get_picture_list()
            ],
        )
