from abc import ABC
import logging
from progressbar import ProgressBar
from pathlib import Path
from app.services.file import FileService, FileTools, iFileService
from app.services.picture_id import (
    PictureIdComputeException,
    PictureIdService,
    iPictureIdService,
)
from app.repositories.picture_data import PictureDataRepository


class baseUseCase(ABC):
    def __init__(self, file_service: iFileService):
        self._file_service = file_service
        self._logger = logging.getLogger("app.use_case")

    def list_pictures(self, root_path: Path) -> list[Path]:
        self._logger.info(f"Listing pictures in {root_path}")
        picture_list = FileTools.list_pictures(root_path=root_path)
        self._logger.info(f"Found {len(picture_list)} pictures")

        return picture_list


class BackupUseCase(baseUseCase):
    def __init__(
        self, file_service: iFileService, picture_id_service: iPictureIdService
    ):
        super().__init__(file_service=file_service)
        self._picture_id_service = picture_id_service

    def _backup_picture(self, picture_path: Path, strict_mode: bool) -> bool:
        picture_data = None

        if not strict_mode:
            picture_data = self._picture_id_service.get_from_cache(
                picture_path=picture_path
            )

        if picture_data is None:
            try:
                picture_data = self._picture_id_service.compute_id(
                    picture_path=picture_path
                )
                self._picture_id_service.add_to_cache(data=picture_data)
            except PictureIdComputeException as e:
                self._logger.warning(
                    f"Failed to compute picture id for {picture_path}: {e}"
                )
                return False

        return self._file_service.backup(origin_path=picture_path, data=picture_data)

    def backup(
        self, picture_list_to_backup: list[Path], strict_mode: bool = False
    ) -> bool:
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

        return True


def backup_use_case_factory(backup_folder_path: Path) -> BackupUseCase:
    picture_data_repo = PictureDataRepository(
        cache_file_path=Path(f"{backup_folder_path}/cache.jsonl")
    )
    file_service = FileService(backup_folder_path=backup_folder_path)
    picture_id_service = PictureIdService(picture_data_repo=picture_data_repo)

    return BackupUseCase(
        file_service=file_service, picture_id_service=picture_id_service
    )
