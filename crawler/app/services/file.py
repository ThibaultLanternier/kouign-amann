from abc import ABC, abstractmethod
import logging
import os
from pathlib import Path

from app.entities.picture_data import iPictureData


class iFileService(ABC):
    @abstractmethod
    def backup(self, origin_path: Path, data: iPictureData) -> bool:
        """Backup to the backup folder returns True if new file is created"""
        pass

    @abstractmethod
    def move(self, origin_path: Path, target_path: Path) -> bool:
        pass

    @abstractmethod
    def list_pictures(self, root_path: Path) -> list[Path]:
        pass


class FileService(iFileService):
    def __init__(self, backup_folder_path: Path) -> None:
        self._backup_folder_path = backup_folder_path

        self._logger = logging.getLogger("app.file_service")
        self._logger.info(
            f"Init FileService Backup folder path is: {self._backup_folder_path}"
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

    def __file_already_exists(self, file_path: Path) -> bool:
        return file_path.exists()

    def backup(self, origin_path: Path, data: iPictureData) -> bool:
        new_file_path = self.__get_file_path(data)

        if self.__file_already_exists(new_file_path):
            self._logger.debug(
                f"File {origin_path} already backed up to {new_file_path}, SKIPPING"
            )
            return False

        with open(origin_path, "rb") as picture_file:
            # new_file_path = self.__get_file_path(data=data)
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

        return True

    def move(self, origin_path: Path, target_path: Path) -> bool:
        if not target_path.parent.exists():
            target_path.parent.mkdir(parents=True)
            
        origin_path.rename(target_path)

    def list_pictures(self, root_path: Path) -> list[Path]:
        small_case_jpg = [x for x in root_path.glob("**/*.jpg")]
        capital_case_jpg = [x for x in root_path.glob("**/*.JPG")]

        return [*small_case_jpg, *capital_case_jpg]
