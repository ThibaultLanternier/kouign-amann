import hashlib
import unittest
from datetime import datetime
from pathlib import Path

from app.entities.picture_data import PictureData
from app.entities.picture_heap import HeapType
from app.factories.picture_heap import PictureHeapFactory


class TestPictureHeapFactory(unittest.TestCase):
    def setUp(self):
        self._picture_list = [
            PictureData(
                creation_date=datetime(2023, 1, 1, 12, 0),
                hash="hash1",
            )
        ]

        self._path_to_id = lambda path: "fixed_id"

        return super().setUp()

    def test_from_folder_path_other(self):
        parent_folder = Path("/path/to/2025 OTHER")

        picture_heap = PictureHeapFactory().from_folder_path(
            folder_path=parent_folder,
            picture_list=self._picture_list,
            path_to_id=self._path_to_id,
        )

        self.assertEqual(picture_heap.get_picture_list(), self._picture_list)
        self.assertEqual(picture_heap.get_type(), HeapType.OTHER)
        self.assertEqual(picture_heap.get_id(), "fixed_id")

    def test_from_folder_path_not_grouped(self):
        parent_folder = Path("/path/to/NOT_GROUPED")

        picture_heap = PictureHeapFactory().from_folder_path(
            folder_path=parent_folder,
            picture_list=self._picture_list,
            path_to_id=self._path_to_id,
        )

        self.assertEqual(picture_heap.get_picture_list(), self._picture_list)
        self.assertEqual(picture_heap.get_type(), HeapType.NOT_GROUPED)

    def test_from_folder_path_grouped(self):
        parent_folder = Path("/path/to/2025-12-25 Christmas Party")

        picture_heap = PictureHeapFactory().from_folder_path(
            folder_path=parent_folder,
            picture_list=self._picture_list,
            path_to_id=self._path_to_id,
        )

        self.assertEqual(picture_heap.get_picture_list(), self._picture_list)
        self.assertEqual(picture_heap.get_type(), HeapType.GROUPED)
        self.assertEqual(picture_heap.get_description(), "Christmas Party")

    def test_from_folder_path_grouped_no_description(self):
        parent_folder = Path("/path/to/2025-12-25 <EVENT DESCRIPTION>")

        picture_heap = PictureHeapFactory().from_folder_path(
            folder_path=parent_folder,
            picture_list=self._picture_list,
            path_to_id=self._path_to_id,
        )

        self.assertEqual(picture_heap.get_picture_list(), self._picture_list)
        self.assertEqual(picture_heap.get_type(), HeapType.GROUPED)
        self.assertEqual(picture_heap.get_description(), None)

    def test_from_folder_path_grouped_no_description_with_increment(self):
        parent_folder = Path("/path/to/2025-12-25 <EVENT DESCRIPTION 125>")

        picture_heap = PictureHeapFactory().from_folder_path(
            folder_path=parent_folder,
            picture_list=self._picture_list,
            path_to_id=self._path_to_id,
        )

        self.assertEqual(picture_heap.get_picture_list(), self._picture_list)
        self.assertEqual(picture_heap.get_type(), HeapType.GROUPED)
        self.assertEqual(picture_heap.get_description(), None)

    def test_from_folder_path_with_heap_id(self):
        parent_folder = Path("/path/to/2025 OTHER")

        picture_heap = PictureHeapFactory().from_folder_path(
            folder_path=parent_folder,
            picture_list=self._picture_list,
            path_to_id=self._path_to_id,
        )

        self.assertEqual(picture_heap.get_id(), "fixed_id")

    def test_from_folder_path_without_heap_id_generates_one(self):
        parent_folder = Path("/path/to/2025 OTHER")
        parent_folder_2 = Path("/path/to/2025 OTHER 2")

        self._path_to_id = lambda path: hashlib.sha256(
            str(path).encode("utf-8")
        ).hexdigest()[:16]

        first_heap = PictureHeapFactory().from_folder_path(
            folder_path=parent_folder,
            picture_list=self._picture_list,
            path_to_id=self._path_to_id,
        )
        second_heap = PictureHeapFactory().from_folder_path(
            folder_path=parent_folder_2,
            picture_list=self._picture_list,
            path_to_id=self._path_to_id,
        )

        self.assertIsInstance(first_heap.get_id(), str)
        self.assertNotEqual(first_heap.get_id(), second_heap.get_id())
