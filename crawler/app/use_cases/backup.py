import logging
from progressbar import ProgressBar
from zipp import Path

from app.services.file import FileService, iFileService
from app.services.picture_id import (
    PictureIdComputeException,
    PictureIdService,
    iPictureIdService,
)


class BackupUseCase:
    def __init__(
        self, file_service: iFileService, picture_id_service: iPictureIdService
    ):
        self._file_service = file_service
        self._picture_id_service = picture_id_service

        self._logger = logging.getLogger("app.backup_use_case")

    def list_pictures(self, root_path: Path) -> list[Path]:
        self._logger.info(f"Listing pictures in {root_path}")
        picture_list = self._file_service.list_pictures(root_path=root_path)
        self._logger.info(f"Found {len(picture_list)} pictures")

        return picture_list

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
            except PictureIdComputeException as e:
                self._logger.warning(
                    f"Failed to compute picture id for {picture_path}: {e}"
                )
                return False

        self._file_service.backup(origin_path=picture_path, data=picture_data)

        return True

    def backup(
        self, picture_list_to_backup: list[Path], strict_mode: bool = False
    ) -> bool:
        self._logger.info(f"Starting backup of {len(picture_list_to_backup)} pictures")
        if strict_mode:
            self._logger.info("Strict mode is enabled, all ids will be recomputed")

        progress_bar = ProgressBar()
        progress_bar.start(max_value=len(picture_list_to_backup))
        progress_bar_count = 0

        for picture_path in picture_list_to_backup:
            self._backup_picture(picture_path=picture_path, strict_mode=strict_mode)
            progress_bar_count = progress_bar_count + 1
            progress_bar.update(progress_bar_count)

        progress_bar.finish()

        return True


def backup_use_case_factory(backup_folder_path: Path) -> BackupUseCase:
    file_service = FileService(backup_folder_path=backup_folder_path)
    picture_id_service = PictureIdService()

    return BackupUseCase(
        file_service=file_service, picture_id_service=picture_id_service
    )
