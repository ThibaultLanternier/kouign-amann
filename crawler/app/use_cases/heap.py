from datetime import timedelta
from functools import reduce
from pathlib import Path
from app.repositories.picture_data import PictureDataRepository
from app.services.heap_organizer import TimeDifferenceHeapOrganizer, iHeapOrganizer
from app.use_cases.backup import BackupUseCase
from app.entities.picture_heap import HeapType
from app.factories.picture_data import PictureDataFactory, iPictureDataFactory
from app.services.backup import LocalFileBackupService, iBackupService
from app.services.picture_data_caching import (
    LocalFilePictureDataCachingService,
    iPictureDataCachingService,
)
from app.tools.file import FileTools, iFileTools


class HeapUseCase(BackupUseCase):
    def __init__(
        self,
        backup_service: iBackupService,
        file_tools: iFileTools,
        picture_data_factory: iPictureDataFactory,
        picture_data_caching_service: iPictureDataCachingService,
        heap_organizer: iHeapOrganizer,
    ):
        self._heap_organizer = heap_organizer

        super().__init__(
            backup_service,
            file_tools,
            picture_data_factory,
            picture_data_caching_service,
        )

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
    backup_folder_path: Path,
    sharded_folder_path: dict[int, Path],
    hours_btw_pictures: int,
    minimun_group_size: int,
) -> HeapUseCase:
    picture_data_repo = PictureDataRepository(
        cache_file_path=Path(f"{backup_folder_path}/cache.jsonl")
    )

    picture_data_factory = PictureDataFactory()
    file_tools = FileTools()

    file_service = LocalFileBackupService(
        backup_folder_path=backup_folder_path,
        sharded_folder_path=sharded_folder_path,
        picture_data_factory=picture_data_factory,
        file_tools=file_tools,
    )
    picture_id_service = LocalFilePictureDataCachingService(
        picture_data_repo=picture_data_repo
    )

    heap_organizer_service = TimeDifferenceHeapOrganizer(
        max_time_difference=timedelta(hours=hours_btw_pictures),
        min_heap_size=minimun_group_size,
    )

    return HeapUseCase(
        backup_service=file_service,
        file_tools=file_tools,
        picture_data_factory=picture_data_factory,
        picture_data_caching_service=picture_id_service,
        heap_organizer=heap_organizer_service,
    )
