import unittest
from unittest.mock import MagicMock

from app.entities.picture_heap import iPictureHeap
from app.services.backup import iBackupService
from app.services.heap_organizer import iHeapOrganizer
from app.use_cases.heap import HeapUseCase, heap_use_case_factory


class TestHeapUseCase(unittest.TestCase):
    def setUp(self):
        mock_picture_heap_1 = MagicMock(name="mock_picture_heap_1", spec=iPictureHeap)
        mock_picture_heap_2 = MagicMock(name="mock_picture_heap_2", spec=iPictureHeap)
        mock_picture_heap_3 = MagicMock(name="mock_picture_heap_3", spec=iPictureHeap)

        self._mock_backup_service = MagicMock(spec=iBackupService)

        self._mock_backup_service.list_backed_up_pictures.return_value = [
            mock_picture_heap_1,
            mock_picture_heap_2,
        ]

        self._heap_organizer_service = MagicMock(spec=iHeapOrganizer)
        self._heap_organizer_service.reorganize_heaps.return_value = [
            mock_picture_heap_3
        ]

        pass  # Setup code for HeapUseCase tests would go here

    def test_reorganize_heaps(self):
        heap_use_case = HeapUseCase(
            backup_service=self._mock_backup_service,
            heap_organizer=self._heap_organizer_service,
        )

        heap_use_case.reorganize_heaps()

        self._mock_backup_service.list_backed_up_pictures.assert_called_once()
        self._heap_organizer_service.reorganize_heaps.assert_called_once_with(
            self._mock_backup_service.list_backed_up_pictures.return_value
        )
        self._mock_backup_service.update_picture_heaps.assert_called_once_with(
            self._heap_organizer_service.reorganize_heaps.return_value
        )

    def test_heap_use_case_factory(self):
        heap_use_case = heap_use_case_factory(
            backup_service=self._mock_backup_service,
            hours_btw_pictures=5,
            minimun_group_size=3,
        )

        self.assertIsInstance(heap_use_case, HeapUseCase)
