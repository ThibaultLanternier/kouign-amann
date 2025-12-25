from abc import ABC
from datetime import timezone
import logging
from progressbar import ProgressBar
from pathlib import Path
from app.services.backup import (
    iBackupService,
    local_file_backup_service_factory,
)
from app.services.picture_data_caching import (
    LocalFilePictureDataCachingService,
    iPictureDataCachingService,
)
from app.repositories.picture_data import JSONRecordedPictureDataRepository
from app.entities.picture import PictureException
from app.factories.picture_data import PictureDataFactory, iPictureDataFactory
from app.tools.file import iFileTools
from app.entities.picture_data import iPictureData


class baseUseCase(ABC):
    def __init__(
        self, file_tools: iFileTools, picture_data_factory: iPictureDataFactory
    ):
        self._file_tools = file_tools
        self._picture_data_factory = picture_data_factory
        self._logger = logging.getLogger("app.use_case")

    def list_pictures(
        self, root_path: Path, folder_name_to_exclude: list[str] = []
    ) -> list[Path]:
        self._logger.info(f"Listing pictures in {root_path}")
        picture_list = self._file_tools.list_pictures(
            root_path_list=[root_path], folder_name_to_exclude=folder_name_to_exclude
        )
        self._logger.info(f"Found {len(picture_list)} pictures")

        return picture_list


class BackupUseCase:
    def __init__(
        self,
        backup_service: iBackupService,
        picture_data_factory: iPictureDataFactory,
        picture_data_caching_service: iPictureDataCachingService,
    ):
        self._picture_data_factory = picture_data_factory
        self._logger = logging.getLogger("app.backup_use_case")

        self._backup_service = backup_service
        self._picture_data_caching_service = picture_data_caching_service

    def backup_single_picture(
        self, picture_path: Path, strict_mode: bool
    ) -> tuple[bool, iPictureData | None]:
        picture_data = None

        if not strict_mode:
            picture_data = self._picture_data_caching_service.get_from_cache(
                picture_path=picture_path
            )

        if picture_data is None:
            try:
                self._logger.debug(f"Computing picture data for {picture_path}")
                picture_data = self._picture_data_factory.compute_data(
                    path=picture_path, current_timezone=timezone.utc
                )
                self._picture_data_caching_service.add_to_cache(
                    data=picture_data, picture_path=picture_path
                )
            except PictureException as e:
                self._logger.warning(
                    f"Failed to compute picture id for {picture_path}: {e}"
                )
                return False, None

        return (
            self._backup_service.backup(origin_path=picture_path, data=picture_data),
            picture_data,
        )

    def backup(
        self, picture_list_to_backup: list[Path], strict_mode: bool = False
    ) -> int:
        self._logger.info(f"Starting backup of {len(picture_list_to_backup)} pictures")
        if strict_mode:
            self._logger.info("Strict mode is enabled, all ids will be recomputed")

        progress_bar = ProgressBar()
        progress_bar.start(max_value=len(picture_list_to_backup))
        progress_bar_count = 0

        new_picture_count = 0

        for picture_path in picture_list_to_backup:
            result, data = self.backup_single_picture(
                picture_path=picture_path, strict_mode=strict_mode
            )

            if result and data is not None:
                self._logger.debug(f"Picture {data.get_hash()} backed up successfully")
                new_picture_count = new_picture_count + 1

            progress_bar_count = progress_bar_count + 1
            progress_bar.update(progress_bar_count)

        progress_bar.finish()

        self._logger.info(
            f"Backup completed, {new_picture_count} new pictures backed up"
        )

        return new_picture_count

    def locate_picture_by_hash(self, picture_hash: str) -> Path | None:
        self._logger.info(f"Locating picture with hash {picture_hash}")
        return self._backup_service.find_by_hash(picture_hash=picture_hash)


def backup_use_case_factory(
    backup_folder_path: Path, sharded_folder_path: dict[int, Path]
) -> BackupUseCase:
    backup_service = local_file_backup_service_factory(
        backup_folder_path=backup_folder_path,
        sharded_folder_path=sharded_folder_path,
    )

    picture_data_repo = JSONRecordedPictureDataRepository(
        cache_file_path=Path(f"{backup_folder_path}/cache.jsonl")
    )

    picture_id_service = LocalFilePictureDataCachingService(
        picture_data_repo=picture_data_repo
    )

    picture_data_factory = PictureDataFactory()

    return BackupUseCase(
        backup_service=backup_service,
        picture_data_factory=picture_data_factory,
        picture_data_caching_service=picture_id_service,
    )
