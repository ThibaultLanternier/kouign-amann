from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import Union

from app.entities.picture_data import iPictureData, PictureData


class iPictureDataRepository(ABC):
    @abstractmethod
    def get(self, path: Path) -> Union[iPictureData, None]:
        pass

    @abstractmethod
    def record(self, data: iPictureData) -> bool:
        pass

    @abstractmethod
    def get_parents_folder_list(self, picture_hash: str) -> list[str]:
        pass


class PictureDataRepository(iPictureDataRepository):
    def _get_data_from_file(self) -> list[iPictureData]:
        output = []

        try:
            with open(self._cache_file_path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    output.append(PictureData.from_json(line.strip()))
        except FileNotFoundError:
            self._logger.warning(
                f"Cache file {self._cache_file_path} not found. Creating a new one."
            )
            pass

        return output

    def _index_data(self, data: iPictureData) -> None:
        self._data[data.get_path()] = data

        picture_hash = data.get_hash()

        if picture_hash not in self._folder_data:
            self._folder_data[picture_hash] = []

        self._folder_data[picture_hash].append(data.get_path())

    def _write_data_to_file(self, data: iPictureData) -> None:
        with open(self._cache_file_path, "a+") as file:
            file.write(PictureData.to_json(data) + "\n")

    def __init__(self, cache_file_path: Path) -> None:
        self._cache_file_path = cache_file_path
        self._data: dict[Path, iPictureData] = {}
        self._folder_data: dict[str, list[Path]] = {}

        self._logger = logging.getLogger("app.picture_data_repository")
        self._logger.info(
            f"Init PictureDataRepository Cache file path is: {self._cache_file_path}"
        )

        picture_data_list = self._get_data_from_file()

        for picture_data in picture_data_list:
            self._index_data(data=picture_data)

    def get(self, path: Path) -> Union[iPictureData, None]:
        if path in self._data:
            self._logger.debug(f"Found {path} PictureData in cache")
            return self._data[path]
        else:
            self._logger.debug(f"{path} not found in PictureData cache")
            return None

    def record(self, data: iPictureData) -> bool:
        self._index_data(data=data)
        self._write_data_to_file(data=data)

        return True

    def get_parents_folder_list(self, picture_hash: str) -> list[str]:
        if picture_hash in self._folder_data:
            folders = [
                str(path.parent.name) for path in self._folder_data[picture_hash]
            ]
            unique_folders = list(set(folders))

            return unique_folders
        else:
            return []
