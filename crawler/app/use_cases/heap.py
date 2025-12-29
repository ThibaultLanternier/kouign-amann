from datetime import timedelta
from functools import reduce
import logging
from app.services.heap_organizer import TimeDifferenceHeapOrganizer, iHeapOrganizer
from app.entities.picture_heap import HeapType
from app.services.backup import iBackupService


class HeapUseCase:
    def __init__(
        self,
        backup_service: iBackupService,
        heap_organizer: iHeapOrganizer,
    ):
        self._backup_service = backup_service
        self._heap_organizer = heap_organizer

        self._logger = logging.getLogger("app.heap_use_case")

    def reorganize_heaps(self):
        self._logger.info("Starting picture grouping using the new heap approach")
        current_picture_heaps = self._backup_service.list_backed_up_pictures()
        self._logger.info(f"Found {len(current_picture_heaps)} picture heaps")

        not_grouped_heaps = [
            heap
            for heap in current_picture_heaps
            if heap.get_type() is HeapType.NOT_GROUPED
        ]
        self._logger.info(f"Found {len(not_grouped_heaps)} not grouped picture heaps")
        not_grouped_picture_count = reduce(
            lambda x, y: x + y,
            [len(heap.get_picture_list()) for heap in not_grouped_heaps],
            0,
        )
        self._logger.info(f"Found {not_grouped_picture_count} not grouped pictures")

        self._logger.info("Starting organizing heaps")
        organized_heaps = self._heap_organizer.reorganize_heaps(current_picture_heaps)

        self._logger.info("Moving pictures in new heaps")
        self._backup_service.update_picture_heaps(organized_heaps)


def heap_use_case_factory(
    backup_service: iBackupService,
    hours_btw_pictures: int,
    minimun_group_size: int,
) -> HeapUseCase:
    heap_organizer_service = TimeDifferenceHeapOrganizer(
        max_time_difference=timedelta(hours=hours_btw_pictures),
        min_heap_size=minimun_group_size,
    )

    return HeapUseCase(
        backup_service=backup_service,
        heap_organizer=heap_organizer_service,
    )
