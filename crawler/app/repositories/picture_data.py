from abc import ABC, abstractmethod
import logging
from math import e
from pathlib import Path
from typing import Union

from app.entities.picture import Picture
from app.entities.picture_data import iPictureData, PictureData


class iPictureDataRepository(ABC):
    @abstractmethod
    def get(self, path: Path) -> iPictureData:
        pass

    @abstractmethod
    def record(self, data: iPictureData) -> bool:
        pass

class PictureDataRepository(ABC):
    def _get_data_from_file(self) -> list[iPictureData]:
        output = []

        try:
            with open(self._cache_file_path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    output.append(PictureData.from_json(line.strip()))
        except FileNotFoundError:
            self._logger.warning(f"Cache file {self._cache_file_path} not found. Creating a new one.")
            pass

        return output
    
    def _index_data(self, data: iPictureData) -> None:
        self._data[data.get_path()] = data

    def _write_data_to_file(self, data: iPictureData) -> None:
        with open(self._cache_file_path, "a+") as file:
            file.write(PictureData.to_json(data) + "\n")

    def __init__(self, cache_file_path: Path) -> None:
        self._cache_file_path = cache_file_path
        self._data: dict[Path, iPictureData] = {}

        self._logger = logging.getLogger("app.picture_data_repository")
        self._logger.info(f"Init PictureDataRepository Cache file path is: {self._cache_file_path}")
        
        picture_data_list = self._get_data_from_file()

        for picture_data in picture_data_list:
            self._index_data(data=picture_data)

    def get(self, path: Path) -> Union[iPictureData, None]:
        if path in self._data:
            return self._data[path]
        else:
            return None
    
    def record(self, data: iPictureData) -> bool:
        self._index_data(data=data)
        self._write_data_to_file(data=data)
        
        return True