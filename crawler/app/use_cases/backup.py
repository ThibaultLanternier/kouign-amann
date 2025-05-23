from abc import ABC
from datetime import timezone
import logging
from isort import file
from progressbar import ProgressBar
from pathlib import Path
from app.services.file import LocalFileBackupService, FileTools, iBackupService, iFileTools
from app.services.picture_id import (
    PictureIdComputeException,
    LocalFilePictureDataCachingService,
    iPictureDataCachingService,
)
from app.repositories.picture_data import PictureDataRepository
from app.entities.picture import PictureException
from app.factories.picture_data import PictureDataFactory, iPictureDataFactory


class baseUseCase(ABC):
    def __init__(
            self, 
            file_service: iBackupService,
            file_tools: iFileTools
        ):
        self._file_service = file_service
        self._file_tools = file_tools
        self._logger = logging.getLogger("app.use_case")

    def list_pictures(self, root_path: Path) -> list[Path]:
        self._logger.info(f"Listing pictures in {root_path}")
        picture_list = self._file_tools.list_pictures(root_path=root_path)
        self._logger.info(f"Found {len(picture_list)} pictures")

        return picture_list


class BackupUseCase(baseUseCase):
    def __init__(
        self, 
        file_service: iBackupService,
        file_tools: iFileTools, 
        picture_id_service: iPictureDataCachingService,
        picture_data_factory: iPictureDataFactory
    ):
        super().__init__(file_service=file_service, file_tools=file_tools)

        self._picture_id_service = picture_id_service
        self._picture_data_factory = picture_data_factory

    def _backup_picture(self, picture_path: Path, strict_mode: bool) -> bool:
        picture_data = None

        if not strict_mode:
            picture_data = self._picture_id_service.get_from_cache(
                picture_path=picture_path
            )

        if picture_data is None:
            try:
                self._logger.debug(f"Computing picture data for {picture_path}")
                picture_data = self._picture_data_factory.compute_data(path=picture_path, current_timezone=timezone.utc)
                self._picture_id_service.add_to_cache(data=picture_data)
            except PictureException as e:
                self._logger.warning(
                    f"Failed to compute picture id for {picture_path}: {e}"
                )
                return False

        return self._file_service.backup(origin_path=picture_path, data=picture_data)

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
            if self._backup_picture(picture_path=picture_path, strict_mode=strict_mode):
                new_picture_count = new_picture_count + 1

            progress_bar_count = progress_bar_count + 1
            progress_bar.update(progress_bar_count)

        progress_bar.finish()

        self._logger.info(
            f"Backup completed, {new_picture_count} new pictures backed up"
        )

        return new_picture_count


def backup_use_case_factory(backup_folder_path: Path) -> BackupUseCase:
    picture_data_repo = PictureDataRepository(
        cache_file_path=Path(f"{backup_folder_path}/cache.jsonl")
    )
    
    picture_data_factory = PictureDataFactory()
    file_tools = FileTools()

    file_service = LocalFileBackupService(
        backup_folder_path=backup_folder_path, 
        picture_data_factory=picture_data_factory,
        file_tools=file_tools,
    )
    picture_id_service = LocalFilePictureDataCachingService(picture_data_repo=picture_data_repo)


    return BackupUseCase(
        file_service=file_service,
        file_tools=file_tools,
        picture_data_factory=picture_data_factory,
        picture_id_service=picture_id_service
    )
