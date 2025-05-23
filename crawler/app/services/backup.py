from abc import ABC, abstractmethod
from datetime import timezone
import logging
import os
from pathlib import Path

from app.entities.picture_data import iPictureData
from app.factories.picture_data import iPictureDataFactory, NotStandardFileNameException

class iBackupService(ABC):
    @abstractmethod
    def backup(self, origin_path: Path, data: iPictureData) -> bool:
        """Backup to the backup folder returns True if new file is created"""
        pass

    @abstractmethod
    def hash_exists(self, picture_hash: str) -> bool:
        """Find file by hash"""
        pass


class LocalFileBackupService(iBackupService):
    def _create_hash_set(self, path_list: list[Path]) -> set[str]:
        output = set()

        for file in path_list:
            try:
                picture_data = self._picture_data_factory.from_standard_path(file, current_timezone=timezone.utc)
                output.add(picture_data.get_hash())
            except NotStandardFileNameException:
                self._logger.warning(
                    f"File {file} is not in the standard format, skipping hash recovery"
                )

        return output

    def __init__(
            self, 
            backup_folder_path: Path, 
            picture_data_factory: iPictureDataFactory, 
            file_tools: iFileTools
        ) -> None:
        self._backup_folder_path = backup_folder_path
        self._picture_data_factory = picture_data_factory
        self._file_tools = file_tools

        self._logger = logging.getLogger("app.file_service")
        self._logger.info(
            f"Init FileService Backup folder path is: {self._backup_folder_path}"
        )

        self._hash_set = self._create_hash_set(
            self._file_tools.list_pictures(root_path=self._backup_folder_path)
        )

    def __get_folder_path(self, data: iPictureData) -> Path:
        return (
            self._backup_folder_path
            / Path(f"{data.get_creation_date().year}")
            / Path("NOT_GROUPED")
        )

    def __get_file_path(self, data: iPictureData) -> Path:
        return self.__get_folder_path(data) / Path(
            f"{int(data.get_creation_date().timestamp())}-{data.get_hash()}.jpg"
        )

    def __file_already_exists(self, picture_hash: str) -> bool:
        return picture_hash in self._hash_set

    def backup(self, origin_path: Path, data: iPictureData) -> bool:
        if self.__file_already_exists(data.get_hash()):
            self._logger.debug(f"File {origin_path} already backed up, SKIPPING")
            return False

        with open(origin_path, "rb") as picture_file:
            new_file_path = self.__get_file_path(data=data)
            self._logger.debug(f"Backing up {origin_path} to {new_file_path}")
            os.makedirs(new_file_path.parent, exist_ok=True)
            with open(new_file_path, "wb+") as new_picture_file:
                new_picture_file.write(picture_file.read())
                os.utime(
                    new_file_path,
                    (
                        data.get_creation_date().timestamp(),
                        data.get_creation_date().timestamp(),
                    ),
                )

        self._hash_set.add(data.get_hash())
        return True

    def hash_exists(self, picture_hash: str) -> bool:
        return self.__file_already_exists(picture_hash)
