from datetime import timezone
from pathlib import Path

from progressbar import ProgressBar

from app.factories.picture_data import PictureDataFactory, iPictureDataFactory
from app.tools.file import FileTools, iFileTools
from app.use_cases.backup import baseUseCase


class CheckUseCase(baseUseCase):
    def __init__(
        self, file_tools: iFileTools, picture_data_factory: iPictureDataFactory
    ):
        super().__init__(
            file_tools=file_tools, picture_data_factory=picture_data_factory
        )

    def check_pictures(
        self,
        backup_list: list[Path],
        picture_list: list[Path],
        current_timezone=timezone.utc,
    ) -> int:
        hash_set = set()

        self._logger.info(f"Indexing {len(backup_list)} already backuped up pictures")
        for backup_path in backup_list:
            try:
                picture_data = self._picture_data_factory.from_standard_path(
                    path=backup_path, current_timezone=current_timezone
                )
                hash_set.add(picture_data.get_hash())
            except Exception as e:
                self._logger.debug(f"Error processing {backup_path}: {e}")

        self._logger.info(f"Found {len(hash_set)} unique hashes in backup list")

        self._logger.info(f"Checking {len(picture_list)} pictures against backup list")

        not_in_backup_count = 0

        progress_bar = ProgressBar()
        progress_bar.start(max_value=len(picture_list))
        progress_bar_count = 0

        for picture_path in picture_list:
            try:
                picture_data = self._picture_data_factory.compute_data(
                    path=picture_path, current_timezone=current_timezone
                )
                if picture_data.get_hash() not in hash_set:
                    self._logger.info(f"Picture {picture_path} has not been backed up")
                    not_in_backup_count += 1
            except Exception as e:
                self._logger.debug(f"Error processing {picture_path}: {e}")

            progress_bar_count = progress_bar_count + 1
            progress_bar.update(progress_bar_count)

        return not_in_backup_count
        if not_in_backup_count > 0:
            self._logger.error(
                f"{not_in_backup_count} pictures have not been backed up"
            )
        else:
            self._logger.info("All pictures have been backed up")


def check_use_case_factory() -> CheckUseCase:
    picture_data_factory = PictureDataFactory()
    file_tools = FileTools()

    return CheckUseCase(
        file_tools=file_tools, picture_data_factory=picture_data_factory
    )
