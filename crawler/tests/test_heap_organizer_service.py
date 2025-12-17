import unittest
from datetime import datetime, timedelta
from pathlib import Path

from app.entities.picture_data import PictureData
from app.entities.picture_heap import HeapType, PictureHeap, iPictureHeap
from app.services.heap_organizer import TimeDifferenceHeapOrganizer


class TestTimeDifferenceHeapOrganizer(unittest.TestCase):
    def setUp(self):
        self._organizer = TimeDifferenceHeapOrganizer(
            max_time_difference=timedelta(hours=2),
            min_heap_size=2,
        )

        # First Heap
        self._picture_1 = PictureData(
            path=Path("root/USELESS"),
            creation_date=datetime(2023, 10, 1, 10),
            hash="hash1",
        )
        self._picture_1_1 = PictureData(
            path=Path("root/USELESS"),
            creation_date=datetime(2023, 10, 1, 10, 10),
            hash="hash1_1",
        )
        self._picture_2 = PictureData(
            path=Path("root/USELESS"),
            creation_date=datetime(2023, 10, 1, 12, 10),
            hash="hash2",
        )

        # Second Heap Too small (less than 2) should go in OTHER
        self._picture_3 = PictureData(
            path=Path("root/USELESS"),
            creation_date=datetime(2023, 10, 1, 15),
            hash="hash3",
        )

        return super().setUp()

    def assertHashAreCorrect(
        self, heap_list: list[iPictureHeap], expected_hashes: list[list[str]]
    ):
        self.assertEqual(len(heap_list), len(expected_hashes))

        for i, heap in enumerate(heap_list):
            picture_hashes = [picture.get_hash() for picture in heap.get_picture_list()]
            self.assertEqual(picture_hashes, expected_hashes[i])

    def assertHeapTypesAreCorrect(
        self, heap_list: list[iPictureHeap], expected_types: list[HeapType]
    ):
        heap_types = [heap.get_type() for heap in heap_list]
        self.assertEqual(heap_types, expected_types)

    def assertDescriptionsAreCorrect(
        self, heap_list: list[iPictureHeap], expected_descriptions: list[str]
    ):
        descriptions = [heap.get_description() for heap in heap_list]
        self.assertEqual(descriptions, expected_descriptions)

    def test_time_difference_heap_organizer_not_grouped(self):
        not_grouped_heap = PictureHeap(
            heap_type=HeapType.NOT_GROUPED,
            picture_list=[
                self._picture_1,
                self._picture_1_1,
                self._picture_2,
                self._picture_3,
            ],
            description=None,
        )

        organized_heaps = self._organizer.reorganize_heaps([not_grouped_heap])

        self.assertHashAreCorrect(
            organized_heaps,
            expected_hashes=[
                ["hash1", "hash1_1", "hash2"],
                ["hash3"],
            ],
        )

        self.assertHeapTypesAreCorrect(
            organized_heaps, [HeapType.GROUPED, HeapType.OTHER]
        )

        self.assertDescriptionsAreCorrect(organized_heaps, [None, None])

    def test_time_difference_heap_organizer_already_grouped(self):
        grouped_heap_1 = PictureHeap(
            heap_type=HeapType.GROUPED,
            picture_list=[self._picture_1, self._picture_1_1],
            description="MAJORITY GROUP",
        )

        grouped_heap_2 = PictureHeap(
            heap_type=HeapType.GROUPED,
            picture_list=[
                self._picture_2,
                self._picture_3,
            ],
            description="MINORITY GROUP",
        )

        organized_heaps = self._organizer.reorganize_heaps(
            [grouped_heap_1, grouped_heap_2]
        )

        self.assertHashAreCorrect(
            organized_heaps,
            expected_hashes=[
                ["hash1", "hash1_1", "hash2"],
                ["hash3"],
            ],
        )

        self.assertHeapTypesAreCorrect(
            organized_heaps, [HeapType.GROUPED, HeapType.OTHER]
        )

        self.assertDescriptionsAreCorrect(organized_heaps, ["MAJORITY GROUP", None])

    def test_time_difference_heap_organizer_with_group_break(self):
        picture_1_2_break = PictureData(
            path=Path("root/USELESS"),
            creation_date=datetime(2023, 10, 1, 11, 10),
            hash="hash1_2_break",
            group_break=True,
        )

        not_grouped_heap = PictureHeap(
            heap_type=HeapType.GROUPED,
            picture_list=[
                self._picture_1,
                self._picture_1_1,
                picture_1_2_break,
                self._picture_2,
                self._picture_3,
            ],
            description="FULL GROUP",
        )

        organized_heaps = self._organizer.reorganize_heaps([not_grouped_heap])

        self.assertHashAreCorrect(
            organized_heaps,
            expected_hashes=[
                ["hash1", "hash1_1"],
                ["hash1_2_break", "hash2"],
                ["hash3"],
            ],
        )

        self.assertHeapTypesAreCorrect(
            organized_heaps, [HeapType.GROUPED, HeapType.GROUPED, HeapType.OTHER]
        )

        self.assertDescriptionsAreCorrect(
            organized_heaps, ["FULL GROUP", "FULL GROUP", None]
        )
