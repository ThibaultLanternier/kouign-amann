from abc import ABC, abstractmethod
from datetime import datetime
from math import pi
from pathlib import Path
from typing import Union
import uuid

from app.controllers.exif import ExifManager
from app.entities.picture import Picture, PictureException
from app.entities.picture_data import PictureData, iPictureData


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
    def __init__(self) -> None:
        pass

    def get_from_cache(self, picture_path: Path) -> Union[iPictureData | None]:
        return None

    def compute_id(self, picture_path: Path) -> iPictureData:
        try:
            picture = Picture(path=picture_path)
        
            return PictureData(
                path=picture_path,
                creation_date=picture.get_exif_creation_time(),
                hash=picture.get_hash(),
            )
        except PictureException as e:
            raise PictureIdComputeException(f"Failed to compute picture {picture_path}: {e}")

    def add_to_cache(self, picture_path: Path, data: iPictureData) -> bool:
        return True
