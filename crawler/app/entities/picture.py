from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

import imagehash
import piexif

class PictureException(Exception):
    pass

class ExifImpossibleToLoadException(PictureException):
    pass

class ExifImageImpossibleToOpen(PictureException):
    pass

class ExifMalformedDateTime(PictureException):
    pass

class HasherException(PictureException):
    pass

class iPicture(ABC):
    @abstractmethod
    def get_exif_creation_time(self) -> datetime:
        pass
    
    @abstractmethod
    def get_hash(self) -> str:
        pass

DEFAULT_DATETIME = datetime(1970, 1, 1, tzinfo=timezone.utc)

class Picture(iPicture):
    def __init__(self, path: Path, current_timezone: timezone = timezone.utc) -> None:
        self._current_timezone = current_timezone
        self._path = path

        try:
            self._image = Image.open(self._path)
        except Exception:
            raise ExifImageImpossibleToOpen(self._path)
    
    def _get_exif_dict(self) -> dict:
        if not hasattr(self, "_exif_dict"):
            try:
                if "exif" in self._image.info:
                    self._exif_dict = piexif.load(self._image.info["exif"])
                else:
                    self._exif_dict = piexif.load(str(self._path))
            except Exception:
                raise ExifImpossibleToLoadException(str(self._path))

        return self._exif_dict

    def _extract_date_time(
        self, raw_date_time: str, current_timezone: timezone
    ) -> datetime:
        try:
            raw_date_and_time = raw_date_time.split(" ")
            raw_date_elements = raw_date_and_time[0].split(":")

            raw_time_elements = raw_date_and_time[1].split(":")

            return datetime(
                int(raw_date_elements[0]),
                int(raw_date_elements[1]),
                int(raw_date_elements[2]),
                int(raw_time_elements[0]),
                int(raw_time_elements[1]),
                int(raw_time_elements[2]),
                0,
                current_timezone,
            )
        except Exception:
            raise ExifMalformedDateTime(self._path)

    def get_exif_creation_time(self) -> datetime:
        try:
            exif_dict = self._get_exif_dict()
            original_date_time = exif_dict["Exif"][
                piexif.ExifIFD.DateTimeOriginal
            ].decode("UTF-8")

            return self._extract_date_time(
                raw_date_time=original_date_time,
                current_timezone=self._current_timezone,
            )
        except KeyError:
            return DEFAULT_DATETIME
    
    def get_hash(self) -> str:
        try:
            return str(imagehash.phash(self._image))
        except Exception:
            raise HasherException(self._path)