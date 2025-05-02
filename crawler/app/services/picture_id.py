from abc import ABC, abstractmethod
import logging
from pathlib import Path
from typing import Union

from app.controllers.exif import ExifManager
from app.entities.picture import Picture, PictureException
from app.entities.picture_data import PictureData, iPictureData
from app.repositories.picture_data import iPictureDataRepository


class PictureIdComputeException(Exception):
    pass


class iPictureIdService(ABC):
    @abstractmethod
    def get_from_cache(self, picture_path: Path) -> Union[iPictureData | None]:
        pass

    @abstractmethod
    def compute_id(self, picture_path: Path) -> iPictureData:
        pass

    @abstractmethod
    def add_to_cache(self, picture_path: Path, data: iPictureData) -> bool:
        pass


class PictureIdService(iPictureIdService):
    def __init__(self, picture_data_repo: iPictureDataRepository) -> None:
        self._picture_data_repo = picture_data_repo
        self._logger = logging.getLogger("app.picture_id_service")

    def get_from_cache(self, picture_path: Path) -> Union[iPictureData | None]:
        return self._picture_data_repo.get(picture_path)

    def compute_id(self, picture_path: Path) -> iPictureData:
        self._logger.debug(f"Computing picture data for {picture_path}")
        try:
            picture = Picture(path=picture_path)
        
            return PictureData(
                path=picture_path,
                creation_date=picture.get_exif_creation_time(),
                hash=picture.get_hash(),
            )
        except PictureException as e:
            self._logger.warning(f"Failed to compute picture data {picture_path}: {e}")
            raise PictureIdComputeException(f"Failed to compute picture {picture_path}: {e}")

    def add_to_cache(self, data: iPictureData) -> bool:
        return self._picture_data_repo.record(data)
