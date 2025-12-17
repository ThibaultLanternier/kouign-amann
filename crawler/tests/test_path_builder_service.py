import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from app.entities.picture_data import PictureData
from app.entities.picture_heap import iPictureHeap
from app.services.path_builder import LocalFilePathBuilderService


class TestLocalFileBackupPathBuilderService(unittest.TestCase):
    def setUp(self):
        self._path_builder = LocalFilePathBuilderService(
            root_folder=Path("/backup"),
            sharded_folders_path={
                2023: Path("/other-backup"),
                2024: Path("/other-backup"),
            },
        )

        self._picture_data = PictureData(
            path=Path("/USELESS"),
            creation_date=datetime(2021, 5, 17, 10, 30),
            hash="abcdef123456",
            group_break=False,
            is_selected=False,
        )

        return super().setUp()

    def test_build_path_no_heap(self):
        self.assertEqual(
            self._path_builder.build_path(data=self._picture_data),
            Path("/backup/2021/NOT_GROUPED/1621240200-abcdef123456.jpg"),
        )

    def test_build_path_with_heap_no_description(self):
        # Créer un mock de iPictureHeap sans description
        mock_heap = MagicMock(spec=iPictureHeap)
        mock_heap.get_start_date.return_value = datetime(2020, 8, 15, 14, 0)
        mock_heap.get_description.return_value = None

        self.assertEqual(
            self._path_builder.build_path(data=self._picture_data, heap=mock_heap),
            Path(
                "/backup/2020/2020-08-15 <EVENT DESCRIPTION 1597492800.0>/1621240200-abcdef123456.jpg"  # NOQA E501
            ),
        )

    def test_build_path_with_heap_with_description(self):
        # Créer un mock de iPictureHeap sans description
        mock_heap = MagicMock(spec=iPictureHeap)
        mock_heap.get_start_date.return_value = datetime(2020, 8, 15, 14, 0)
        mock_heap.get_description.return_value = "Super Party"

        self.assertEqual(
            self._path_builder.build_path(data=self._picture_data, heap=mock_heap),
            Path("/backup/2020/2020-08-15 Super Party/1621240200-abcdef123456.jpg"),
        )

    def test_build_path_with_heap_with_description_selected(self):
        # Créer un mock de iPictureHeap sans description
        mock_heap = MagicMock(spec=iPictureHeap)
        mock_heap.get_start_date.return_value = datetime(2020, 8, 15, 14, 0)
        mock_heap.get_description.return_value = "Super Party"

        picture_data = PictureData(
            path=Path("/USELESS"),
            creation_date=datetime(2021, 5, 17, 10, 30),
            hash="abcdef123456",
            group_break=False,
            is_selected=True,
        )

        self.assertEqual(
            self._path_builder.build_path(data=picture_data, heap=mock_heap),
            Path("/backup/2020/2020-08-15 Super Party/0-1621240200-abcdef123456.jpg"),
        )

    def test_build_path_with_heap_with_description_group_break(self):
        # Créer un mock de iPictureHeap sans description
        mock_heap = MagicMock(spec=iPictureHeap)
        mock_heap.get_start_date.return_value = datetime(2020, 8, 15, 14, 0)
        mock_heap.get_description.return_value = "Super Party"

        picture_data = PictureData(
            path=Path("/USELESS"),
            creation_date=datetime(2021, 5, 17, 10, 30),
            hash="abcdef123456",
            group_break=True,
            is_selected=False,
        )

        self.assertEqual(
            self._path_builder.build_path(data=picture_data, heap=mock_heap),
            Path("/backup/2020/2020-08-15 Super Party/1621240200-abcdef123456-x.jpg"),
        )

    def test_build_path_with_heap_with_description_sharding(self):
        # Créer un mock de iPictureHeap sans description
        mock_heap = MagicMock(spec=iPictureHeap)
        mock_heap.get_start_date.return_value = datetime(2023, 8, 15, 14, 0)
        mock_heap.get_description.return_value = "Super Party"

        self.assertEqual(
            self._path_builder.build_path(data=self._picture_data, heap=mock_heap),
            Path(
                "/other-backup/2023/2023-08-15 Super Party/1621240200-abcdef123456.jpg"
            ),
        )
