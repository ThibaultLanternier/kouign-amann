from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
import re

from app.entities.picture_data import PictureData, iPictureData
from app.entities.picture import Picture


class NotStandardFileNameException(Exception):
    pass


class iPictureDataFactory(ABC):
    @abstractmethod
    def from_standard_path(
        self, path: Path, current_timezone: timezone
    ) -> iPictureData:
        pass

    @abstractmethod
    def compute_data(self, path: Path, current_timezone: timezone) -> iPictureData:
        pass


class PictureDataFactory(iPictureDataFactory):
    def from_standard_path(
        self, path: Path, current_timezone: timezone
    ) -> iPictureData:
        pattern = re.compile(r"^([0-9]{1,10})-([a-f0-9]+).jpg$")
        m = re.match(pattern, path.name)

        if m is None:
            raise NotStandardFileNameException(f"File name {path.name} is malformed")

        creation_timestamp = int(m.group(1))
        hash_value = m.group(2)

        return PictureData(
            path=path,
            creation_date=datetime.fromtimestamp(
                creation_timestamp, tz=current_timezone
            ),
            hash=hash_value,
        )

    def compute_data(self, path: Path, current_timezone: timezone) -> iPictureData:
        picture = Picture(path=path, current_timezone=current_timezone)

        return PictureData(
            path=path,
            creation_date=picture.get_exif_creation_time(),
            hash=picture.get_hash(),
        )
