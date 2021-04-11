from dataclasses import dataclass
from typing import Tuple, Any, Union
from datetime import datetime
from app.tools.date import DateTimeConverter


class DictFactory(dict):
    def __init__(self, data):
        super().__init__(self._format_value(key=x[0], value=x[1]) for x in data)

    def _format_value(self, key: str, value: Any) -> Tuple[str, Any]:
        if isinstance(value, datetime):
            value = DateTimeConverter().to_string(value)

        return (key, value)


@dataclass
class PictureInfo:
    creation_time: datetime
    thumbnail: str


@dataclass
class PictureFile:
    crawler_id: str
    resolution: Tuple[int, int]
    picture_path: str
    last_seen: datetime


@dataclass
class PictureData:
    hash: str
    creation_time: datetime
    resolution: Tuple[int, int]
    picture_path: str
    thumbnail: Union[str, None]

    def get_picture_info(self) -> PictureInfo:
        if self.thumbnail is None:
            raise Exception("Missing thumbnail")

        return PictureInfo(creation_time=self.creation_time, thumbnail=self.thumbnail)

    def get_picture_file(self, current_time: datetime, crawler_id: str) -> PictureFile:
        return PictureFile(
            crawler_id=crawler_id,
            resolution=self.resolution,
            picture_path=self.picture_path,
            last_seen=current_time,
        )
