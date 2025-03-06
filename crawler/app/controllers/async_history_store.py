from abc import ABC, abstractmethod
import logging
import os
import aiofiles

from datetime import datetime
from typing import List, Tuple, Dict
from aiofiles import os as async_os

from app.models.file import LocalFile

from pathlib import Path


class iAsyncCrawlHistoryStore(ABC):
    @abstractmethod
    def get_crawl_history(self) -> Dict[Path, LocalFile]:
        pass

    @abstractmethod
    async def add_file(self, path: Path):
        pass

    @abstractmethod
    async def reset(self):
        pass


class AsyncCrawlHistoryStore(iAsyncCrawlHistoryStore):
    def __init__(self, file_directory: Path = Path("")) -> None:
        self._directory_path = file_directory
        self._file_name = "localstore-async.csv"

        self._logger = logging.getLogger("app.historystore")
        self._logger.info(f"Using {self._get_storage_file_path()} as storage file")

    def _get_storage_file_path(self) -> Path:
        return self._directory_path / self._file_name

    def _get_raw_data_list(self) -> List[Tuple[str, str]]:
        output = []

        try:
            with open(self._get_storage_file_path(), "r") as file:
                lines = file.readlines()
                for line in lines:
                    line_elements = line.split("\n")[0].split(";")
                    output.append((line_elements[0], line_elements[1]))
        except FileNotFoundError:
            self._logger.warning(f'No history file found at {self._get_storage_file_path()}')
            pass

        return output

    def get_crawl_history(self) -> Dict[Path, LocalFile]:
        output: Dict[Path, LocalFile] = {}

        raw_data_list = self._get_raw_data_list()

        for data in raw_data_list:
            path = Path(data[0])
            last_modified = datetime.fromisoformat(data[1])

            local_file = LocalFile(path=path, last_modified=last_modified)

            if path not in output.keys():
                output[path] = local_file
            else:
                if output[path].last_modified < local_file.last_modified:
                    output[path] = local_file

        return output

    async def add_file(self, path: Path):
        last_modified_ts = os.path.getmtime(path)
        last_modified = datetime.fromtimestamp(last_modified_ts)

        async with aiofiles.open(self._get_storage_file_path(), "a+") as f:
            await f.write(str(path) + ";" + last_modified.isoformat() + "\n")

    async def reset(self):
        try:
            await async_os.remove(self._get_storage_file_path())
        except FileNotFoundError:
            pass
