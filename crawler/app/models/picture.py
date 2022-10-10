from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Union, Optional
from datetime import datetime


class PictureOrientation(Enum):
    PORTRAIT = 0
    LANDSCAPE = 1


@dataclass
class PictureInfo:
    creation_time: datetime
    thumbnail: str
    orientation: Optional[PictureOrientation]


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
    orientation: Union[PictureOrientation, None]

    def get_picture_info(self) -> PictureInfo:
        if self.thumbnail is None:
            raise Exception("Missing thumbnail")

        return PictureInfo(
            creation_time=self.creation_time,
            thumbnail=self.thumbnail,
            orientation=self.orientation,
        )

    def get_picture_file(
        self, current_time: datetime, crawler_id: str
    ) -> PictureFile:  # noqa: E501
        return PictureFile(
            crawler_id=crawler_id,
            resolution=self.resolution,
            picture_path=self.picture_path,
            last_seen=current_time,
        )
