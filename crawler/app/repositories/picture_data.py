from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from json import JSONDecodeError
import json
import logging
from pathlib import Path
from typing import Union


@dataclass
class RecordedPictureData:
    path: Path
    hash: str
    creation_date: datetime


class iPictureDataRepository(ABC):
    @abstractmethod
    def get(self, path: Path) -> Union[RecordedPictureData, None]:
        pass

    @abstractmethod
    def record(self, data: RecordedPictureData) -> bool:
        pass


class PictureDataRepository(iPictureDataRepository):
    def _get_data_from_json_line(self, line: str) -> RecordedPictureData:
        data = json.loads(line)

        return RecordedPictureData(
            path=Path(data["path"]),
            creation_date=datetime.fromisoformat(data["creation_date"]),
            hash=data["hash"],
        )

    def _convert_to_json_line(self, data: RecordedPictureData) -> str:
        return json.dumps(
            {
                "path": str(data.path),
                "creation_date": data.creation_date.isoformat(),
                "hash": data.hash,
            }
        )

    def _get_data_from_file(self) -> list[RecordedPictureData]:
        output = []

        try:
            with open(self._cache_file_path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    try:
                        output.append(self._get_data_from_json_line(line.strip()))
                    except JSONDecodeError as e:
                        self._logger.error(
                            f"Error decoding line in cache file: {line.strip()} - {e}"
                        )
        except FileNotFoundError:
            self._logger.warning(
                f"Cache file {self._cache_file_path} not found. Creating a new one."
            )
            pass

        self._logger.info(f"Loaded {len(output)} PictureData from cache file")

        return output

    def _index_data(self, data: RecordedPictureData) -> None:
        self._data[data.path] = data

    def _write_data_to_file(self, data: RecordedPictureData) -> None:
        with open(self._cache_file_path, "a+") as file:
            file.write(self._convert_to_json_line(data) + "\n")

    def __init__(self, cache_file_path: Path) -> None:
        self._cache_file_path = cache_file_path
        self._data: dict[Path, RecordedPictureData] = {}

        self._logger = logging.getLogger("app.picture_data_repository")
        self._logger.info(
            f"Init PictureDataRepository Cache file path is: {self._cache_file_path}"
        )

        picture_data_list = self._get_data_from_file()

        for picture_data in picture_data_list:
            self._index_data(data=picture_data)

    def get(self, path: Path) -> Union[RecordedPictureData, None]:
        if path in self._data:
            self._logger.debug(f"Found {path} PictureData in cache")
            return self._data[path]
        else:
            self._logger.debug(f"{path} not found in PictureData cache")
            return None

    def record(self, data: RecordedPictureData) -> bool:
        self._index_data(data=data)
        self._write_data_to_file(data=data)

        return True
