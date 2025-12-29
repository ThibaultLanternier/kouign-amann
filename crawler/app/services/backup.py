from abc import ABC, abstractmethod
from datetime import timezone
import logging
import os
from pathlib import Path

from app.entities.picture_data import iPictureData
from app.factories.picture_data import (
    PictureDataFactory,
    iPictureDataFactory,
    NotStandardFileNameException,
)
from app.tools.file import FileTools, iFileTools
from app.entities.picture_heap import iPictureHeap
from app.services.path_builder import LocalFilePathBuilderService
from app.factories.picture_heap import PictureHeapFactory


class iBackupService(ABC):
    @abstractmethod
    def backup(self, origin_path: Path, data: iPictureData) -> bool:
        """Backup to the backup folder returns True if new file is created"""
        pass

    @abstractmethod
    def update_picture_heaps(self, picture_heap_list: list[iPictureHeap]) -> bool:
        """Group pictures in their respective folders"""
        pass

    @abstractmethod
    def list_backed_up_pictures(self) -> list[iPictureHeap]:
        """List all pictures in the backup folder organized by heaps"""
        pass

    @abstractmethod
    def hash_exists(self, picture_hash: str) -> bool:
        """Find file by hash"""
        pass

    @abstractmethod
    def find_by_hash(self, picture_hash: str) -> bytes | None:
        """Locate picture by its hash value and return binary data"""
        pass

    @abstractmethod
    def get_picture_data_factory(self) -> iPictureDataFactory:
        """Get the picture data factory used by the service"""
        pass


class LocalFileBackupService(iBackupService):
    def _create_hash_set(self, path_list: list[Path]) -> dict[str, Path]:
        output = {}

        for file in path_list:
            try:
                picture_data = self._picture_data_factory.from_standard_path(
                    file, current_timezone=timezone.utc
                )
                output[picture_data.get_hash()] = file
            except NotStandardFileNameException:
                self._logger.warning(
                    f"File {file} is not in the standard format, skipping hash recovery"
                )

        return output

    def __init__(
        self,
        backup_folder_path: Path,
        sharded_folder_path: dict[int, Path],
        picture_data_factory: iPictureDataFactory,
        file_tools: iFileTools,
    ) -> None:
        self._backup_folder_path = backup_folder_path
        self._sharded_folder_path = sharded_folder_path

        self._path_builder = LocalFilePathBuilderService(
            root_folder=backup_folder_path, sharded_folders_path=sharded_folder_path
        )

        self._picture_data_factory = picture_data_factory
        self._file_tools = file_tools

        self._logger = logging.getLogger("app.file_service")
        self._logger.info(
            f"Init FileService Backup folder path is: {self._backup_folder_path}"
        )

        for year, path in sharded_folder_path.items():
            self._logger.info(f"Pictures for year {year} will be recorde in {path}")

        sharded_path_list = list(sharded_folder_path.values())

        self._hash_set = self._create_hash_set(
            self._file_tools.list_pictures(
                root_path_list=[self._backup_folder_path, *sharded_path_list],
                folder_name_to_exclude=[],
            )
        )

    def __picture_already_exists(self, picture_hash: str) -> bool:
        return picture_hash in self._hash_set.keys()

    def backup(self, origin_path: Path, data: iPictureData) -> bool:
        if self.__picture_already_exists(data.get_hash()):
            self._logger.debug(f"File {origin_path} already backed up, SKIPPING")
            return False

        with open(origin_path, "rb") as picture_file:
            new_file_path = self._path_builder.build_path(data=data)

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
            self._hash_set[data.get_hash()] = new_file_path

        return True

    def hash_exists(self, picture_hash: str) -> bool:
        return self.__picture_already_exists(picture_hash)

    def find_by_hash(self, picture_hash: str) -> bytes | None:
        if picture_hash in self._hash_set:
            file_path = self._hash_set[picture_hash]
            self._logger.debug(f"Found file for hash {picture_hash}: {file_path}")
            try:
                with open(file_path, "rb") as picture_file:
                    return picture_file.read()
            except FileNotFoundError:
                self._logger.warning(f"File not found for hash {picture_hash}: {file_path}")
                return None
            except Exception as e:
                self._logger.error(f"Error reading file for hash {picture_hash}: {e}")
                return None
        else:
            return None

    def update_picture_heaps(self, picture_heap_list: list[iPictureHeap]) -> bool:
        for heap in picture_heap_list:
            for picture in heap.get_picture_list():
                new_path = self._path_builder.build_path(data=picture, heap=heap)

                current_path = self.find_by_hash(picture_hash=picture.get_hash())

                if current_path is not None:
                    if str(current_path) != str(new_path):
                        self._logger.debug(
                            f"Moving {picture.get_hash()} {current_path} -> {new_path}"
                        )
                        self._file_tools.move_file(current_path, new_path)
                else:
                    self._logger.warning(f"Picture {picture.get_hash()} not found")

        return True

    def list_backed_up_pictures(self) -> list[iPictureHeap]:
        heap_list: dict[Path, list[iPictureData]] = {}

        for path in self._hash_set.values():
            parent_folder = path.parent

            if parent_folder not in heap_list:
                heap_list[parent_folder] = []

            try:
                picture_data = self._picture_data_factory.from_standard_path(
                    path, current_timezone=timezone.utc
                )
                heap_list[parent_folder].append(picture_data)

            except NotStandardFileNameException:
                self._logger.warning(
                    f"File {path} is not in the standard format, skipping"
                )
                continue

        output: list[iPictureHeap] = []

        for folder_path, picture_data_list in heap_list.items():
            picture_heap = PictureHeapFactory().from_folder_path(
                folder_path=folder_path, picture_list=picture_data_list
            )

            output.append(picture_heap)

        return output

    def get_picture_data_factory(self) -> iPictureDataFactory:
        return self._picture_data_factory


def local_file_backup_service_factory(
    backup_folder_path: Path,
    sharded_folder_path: dict[int, Path],
) -> iBackupService:
    picture_data_factory = PictureDataFactory()
    file_tools = FileTools()

    backup_service = LocalFileBackupService(
        backup_folder_path=backup_folder_path,
        sharded_folder_path=sharded_folder_path,
        picture_data_factory=picture_data_factory,
        file_tools=file_tools,
    )

    return backup_service
