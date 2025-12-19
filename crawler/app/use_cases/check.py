from datetime import timezone
import logging
from pathlib import Path

from progressbar import ProgressBar

from app.factories.picture_data import PictureDataFactory, iPictureDataFactory
from app.services.backup import iBackupService


class CheckUseCase:
    def __init__(
        self, backup_service: iBackupService, picture_data_factory: iPictureDataFactory
    ):
        self._backup_service = backup_service
        self._picture_data_factory = picture_data_factory

        self._logger = logging.getLogger("app.check_use_case")

    def check_single_picture(
        self,
        picture_path: Path,
        current_timezone=timezone.utc,
    ) -> bool:
        try:
            picture_data = self._picture_data_factory.compute_data(
                path=picture_path, current_timezone=current_timezone
            )
            picture_hash = picture_data.get_hash()

            if not self._backup_service.hash_exists(picture_hash=picture_hash):
                self._logger.info(f"Picture {picture_path} has not been backed up")
                return False
            else:
                return True
        except Exception as e:
            self._logger.debug(f"Error processing {picture_path}: {e}")
            return False

    def check_pictures(
        self,
        picture_list_to_check: list[Path],
        current_timezone=timezone.utc,
    ) -> int:
        self._logger.info(
            f"Checking {len(picture_list_to_check)} pictures against backup list"
        )

        not_in_backup_count = 0

        progress_bar = ProgressBar()
        progress_bar.start(max_value=len(picture_list_to_check))
        progress_bar_count = 0

        for picture_path in picture_list_to_check:
            picture_check = self.check_single_picture(
                picture_path=picture_path, current_timezone=current_timezone
            )

            if not picture_check:
                not_in_backup_count += 1

            progress_bar_count = progress_bar_count + 1
            progress_bar.update(progress_bar_count)

        return not_in_backup_count


def check_use_case_factory(backup_service: iBackupService) -> CheckUseCase:
    picture_data_factory = PictureDataFactory()

    return CheckUseCase(
        backup_service=backup_service, picture_data_factory=picture_data_factory
    )
