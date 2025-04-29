from abc import ABC, abstractmethod
from calendar import c
from pathlib import Path
from typing import Union
import uuid

from app.entities.picture_data import PictureData, iPictureData

class PictureIdComputeException(Exception):
    pass

class iPictureIdService(ABC):
    @abstractmethod
    def get_from_cache(self, picture_path: Path) -> Union[iPictureData|None]:
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

    def get_from_cache(self, picture_path: Path) -> Union[iPictureData|None]:
        return None

    def compute_id(self, picture_path: Path) -> iPictureData:
        return PictureData(
            path=picture_path,
            creation_date=picture_path.stat().st_ctime,
            hash=uuid.uuid4().hex
        )

    def add_to_cache(self, picture_path: Path, data: iPictureData) -> bool:
        return True