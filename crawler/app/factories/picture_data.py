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
        pattern = re.compile(r"^(0-)?([0-9]{1,10})-([a-f0-9]+)(-x)?\.jpg$")
        m = re.match(pattern, path.name)

        if m is None:
            raise NotStandardFileNameException(f"File name {path.name} is malformed")

        is_selected = m.group(1) == "0-"
        creation_timestamp = int(m.group(2))
        hash_value = m.group(3)
        group_break = m.group(4) == "-x"

        return PictureData(
            path=path,
            creation_date=datetime.fromtimestamp(
                creation_timestamp, tz=current_timezone
            ),
            hash=hash_value,
            group_break=group_break,
            is_selected=is_selected,
        )

    def compute_data(self, path: Path, current_timezone: timezone) -> iPictureData:
        picture = Picture(path=path, current_timezone=current_timezone)

        return PictureData(
            path=path,
            creation_date=picture.get_exif_creation_time(),
            hash=picture.get_hash(),
        )
