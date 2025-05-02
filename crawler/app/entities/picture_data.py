from abc import ABC, abstractmethod
from datetime import datetime
import json
from pathlib import Path


class iPictureData(ABC):
    @abstractmethod
    def get_path(self) -> Path:
        pass

    @abstractmethod
    def get_creation_date(self) -> datetime:
        pass

    @abstractmethod
    def get_hash(self) -> str:
        pass


class PictureData(iPictureData):
    def __init__(self, path: Path, creation_date: datetime, hash: str) -> None:
        self._path = path
        self._creation_date = creation_date
        self._hash = hash

    def get_path(self) -> Path:
        return self._path

    def get_creation_date(self) -> datetime:
        return self._creation_date

    def get_hash(self) -> str:
        return self._hash

    @staticmethod
    def from_json(json_data: str) -> iPictureData:
        data = json.loads(json_data)
        return PictureData(
            path=Path(data["path"]),
            creation_date=datetime.fromisoformat(data["creation_date"]),
            hash=data["hash"],
        )
    
    @staticmethod
    def to_json(data: iPictureData) -> str: 
        return json.dumps({
            "path": str(data.get_path()),
            "creation_date": data.get_creation_date().isoformat(),
            "hash": data.get_hash(),
        })