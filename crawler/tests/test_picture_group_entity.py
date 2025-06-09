import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from app.entities.picture_data import PictureData, iPictureData
from app.entities.picture_group import (NotUniqueFolderException, PictureGroup,
                                        PictureGroupException)
from app.repositories.picture_data import iPictureDataRepository


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

        self._picture_group_list: list[iPictureData] = [
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

        self._picture_group_list_2: list[iPictureData] = [
            PictureData(
                path=Path("root/NOT_GROUPED/hash1.jpg"),
                creation_date=datetime(2023, 10, 1),
                hash="hash1",
            ),
            PictureData(
                path=Path("root/2013-02-03 <EVENT_DESCRIPTION>/hash2.jpg"),
                creation_date=datetime(2023, 10, 3),
                hash="hash2",
            ),
            PictureData(
                path=Path("root/EVENT-YYY/hash3.jpg"),
                creation_date=datetime(2023, 10, 5),
                hash="hash3",
            ),
            PictureData(
                path=Path("root/2013-02-03 <EVENT_DESCRIPTION>/hash4.jpg"),
                creation_date=datetime(2023, 10, 7),
                hash="hash4",
            ),
        ]

        self._picture_group_partly_grouped = PictureGroup(self._picture_group_list)

        self._mock_picture_data_repository = MagicMock(spec=iPictureDataRepository)

    def test_is_editable_not_grouped_should_return_false(self):
        picture_group = PictureGroup([self._picture_group_list_2[0]])

        self.assertFalse(picture_group.is_editable())

    def test_is_editable_already_renamed_should_return_false(self):
        picture_group = PictureGroup([self._picture_group_list_2[2]])

        self.assertFalse(picture_group.is_editable())

    def test_is_editable_generic_name_should_return_true(self):
        picture_group = PictureGroup([self._picture_group_list_2[1]])

        self.assertTrue(picture_group.is_editable())

    def test_is_editable_not_single_folder_should_raise(self):
        picture_group = PictureGroup(
            [
                self._picture_group_list_2[1],
                self._picture_group_list_2[2],
            ]
        )

        self.assertRaises(NotUniqueFolderException, picture_group.is_editable)

    def test_get_new_folder_name_should_return_most_repeated_name(self):
        picture_group = PictureGroup(
            [
                self._picture_group_list_2[1],
                self._picture_group_list_2[3],
            ]
        )

        self._mock_picture_data_repository.get_parents_folder_list.return_value = [
            "2024-03 Vacances Ski les Arcs",
            "2024-03 Vacances Ski les Arcs",
            "Saint Malo Weekend",
        ]

        expected_folder_name = Path(
            "root/2023-10-03 Saint Malo Weekend<OR>Vacances Ski les Arcs"
        )
        self.assertEqual(
            picture_group.get_new_folder_name(self._mock_picture_data_repository),
            expected_folder_name,
        )

    def test_get_new_folder_name_should_return_same_name_if_folder_list_empty(self):
        picture_group = PictureGroup(
            [
                self._picture_group_list_2[1],
                self._picture_group_list_2[3],
            ]
        )

        self._mock_picture_data_repository.get_parents_folder_list.return_value = []

        expected_folder_name = Path("root/2013-02-03 <EVENT_DESCRIPTION>")
        self.assertEqual(
            picture_group.get_new_folder_name(self._mock_picture_data_repository),
            expected_folder_name,
        )

    def test_get_new_folder_name_should_return_same_name_if_only_camera_folder(self):
        picture_group = PictureGroup(
            [
                self._picture_group_list_2[1],
                self._picture_group_list_2[3],
            ]
        )

        self._mock_picture_data_repository.get_parents_folder_list.return_value = [
            "mon truc avec CANON",
            "FUJI RAW",
            "XXX APPLE RAW",
        ]

        expected_folder_name = Path("root/2013-02-03 <EVENT_DESCRIPTION>")
        self.assertEqual(
            picture_group.get_new_folder_name(self._mock_picture_data_repository),
            expected_folder_name,
        )

    def test_get_new_folder_name_not_editable_should_raise(self):
        picture_group = PictureGroup([self._picture_group_list_2[2]])

        def get_new_folder_name():
            picture_group.get_new_folder_name(self._mock_picture_data_repository)

        self.assertRaises(PictureGroupException, get_new_folder_name)

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
