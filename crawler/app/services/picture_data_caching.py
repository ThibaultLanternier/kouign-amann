from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import Union

from app.entities.picture_data import PictureData, iPictureData
from app.repositories.picture_data import RecordedPictureData, iPictureDataRepository


class PictureIdComputeException(Exception):
    pass


class iPictureDataCachingService(ABC):
    @abstractmethod
    def get_from_cache(self, picture_path: Path) -> Union[iPictureData | None]:
        pass

    @abstractmethod
    def add_to_cache(self, data: iPictureData, picture_path: Path) -> bool:
        pass


class LocalFilePictureDataCachingService(iPictureDataCachingService):
    def __init__(self, picture_data_repo: iPictureDataRepository) -> None:
        self._picture_data_repo = picture_data_repo
        self._logger = logging.getLogger("app.picture_id_service")

    def _from_picture_data(self, path: Path, data: iPictureData) -> RecordedPictureData:
        return RecordedPictureData(
            path=path,
            hash=data.get_hash(),
            creation_date=data.get_creation_date(),
        )

    def _to_picture_data(self, data: RecordedPictureData) -> iPictureData:
        return PictureData(
            creation_date=data.creation_date,
            hash=data.hash,
        )

    def get_from_cache(self, picture_path: Path) -> Union[iPictureData | None]:
        data = self._picture_data_repo.get(picture_path)

        if data is not None:
            return self._to_picture_data(data=data)
        else:
            return None

    def add_to_cache(self, data: iPictureData, picture_path: Path) -> bool:
        recorded_data = self._from_picture_data(path=picture_path, data=data)

        return self._picture_data_repo.record(data=recorded_data)
