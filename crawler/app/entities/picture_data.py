from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
from pathlib import Path
import re

class NotStandardFileNameException(Exception):
    pass

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
        return json.dumps(
            {
                "path": str(data.get_path()),
                "creation_date": data.get_creation_date().isoformat(),
                "hash": data.get_hash(),
            }
        )
    
    @staticmethod
    def from_standard_path(standard_path: Path, current_timezone: timezone = timezone.utc) -> iPictureData:
        pattern = re.compile(r"^([0-9]{1,10})-([a-f0-9]+).jpg$")
        m = re.match(pattern, standard_path.name)

        if m is None:
            raise NotStandardFileNameException(f"File name {standard_path.name} is malformed")

        creation_timestamp = int(m.group(1))
        hash_value = m.group(2)

        return PictureData(
            path=standard_path,
            creation_date=datetime.fromtimestamp(creation_timestamp, tz=current_timezone),
            hash=hash_value,
        )
 