from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import Union

from app.entities.picture_data import iPictureData
from app.repositories.picture_data import iPictureDataRepository


class PictureIdComputeException(Exception):
    pass


class iPictureDataCachingService(ABC):
    @abstractmethod
    def get_from_cache(self, picture_path: Path) -> Union[iPictureData | None]:
        pass

    @abstractmethod
    def add_to_cache(self, data: iPictureData) -> bool:
        pass


class LocalFilePictureDataCachingService(iPictureDataCachingService):
    def __init__(self, picture_data_repo: iPictureDataRepository) -> None:
        self._picture_data_repo = picture_data_repo
        self._logger = logging.getLogger("app.picture_id_service")

    def get_from_cache(self, picture_path: Path) -> Union[iPictureData | None]:
        return self._picture_data_repo.get(picture_path)

    def add_to_cache(self, data: iPictureData) -> bool:
        return self._picture_data_repo.record(data)
