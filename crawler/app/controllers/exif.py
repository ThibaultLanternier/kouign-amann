from PIL import Image
from PIL.Image import Image as ImageType
from pathlib import Path
from datetime import datetime, timezone
from typing import Union, Dict, Tuple
from abc import ABC, abstractmethod

from app.tools.hash import HashExtractor

import piexif


class ExifException(Exception):
    pass


class ExifImageImpossibleToOpen(ExifException):
    pass


class ExifImpossibleToLoadException(ExifException):
    pass


class ExifFailedRecordingHashInExif(ExifException):
    pass


class AbstractExifManager(ABC):
    @abstractmethod
    async def record_hash_in_exif(self, hash: str) -> ImageType:
        pass

    @abstractmethod
    def get_image(self) -> ImageType:
        pass

    @abstractmethod
    async def get_hash(self) -> Union[str, None]:
        pass

    @abstractmethod
    async def get_creation_time(self) -> datetime:
        pass

    @abstractmethod
    async def get_resolution(self) -> Tuple[int, int]:
        pass


DEFAULT_DATETIME = datetime(1970, 1, 1, tzinfo=timezone.utc)


class ExifManager(AbstractExifManager):
    def __init__(self, path: Path, current_timezone: timezone = timezone.utc) -> None:
        self._path = path
        self._current_timezone = current_timezone
        try:
            self._image = Image.open(self._path)
        except Exception:
            raise ExifImageImpossibleToOpen(self._path)

    async def _get_exif_dict(self) -> Dict:
        if not hasattr(self, "_exif_dict"):
            try:
                if "exif" in self._image.info:
                    self._exif_dict = piexif.load(self._image.info["exif"])
                else:
                    self._exif_dict = piexif.load(str(self._path))
            except Exception:
                raise ExifImpossibleToLoadException(str(self._path))

        return self._exif_dict

    def __del__(self):
        if hasattr(self, "_image"):
            self._image.close()

    def get_image(self) -> ImageType:
        return self._image

    async def _add_hash_to_exif(self, hash: str) -> bytes:
        try:
            await self._get_exif_dict()

            hash_string = f"phash:{hash}"

            self._exif_dict["0th"][piexif.ImageIFD.ImageID] = hash_string.encode(
                "ASCII"
            )

            return piexif.dump(self._exif_dict)
        except Exception:
            raise ExifFailedRecordingHashInExif(self._path)

    def _extract_date_time(
        self, raw_date_time: str, current_timezone: timezone
    ) -> datetime:
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

    async def record_hash_in_exif(self, hash: str) -> ImageType:
        exif_bytes = await self._add_hash_to_exif(hash=hash)

        self._image.save(self._path, "jpeg", exif=exif_bytes)

        return self._image

    async def get_hash(self) -> Union[str, None]:
        await self._get_exif_dict()

        try:
            hash = self._exif_dict["0th"][piexif.ImageIFD.ImageID].decode("ASCII")
            return HashExtractor().extract(hash)
        except Exception:
            return None

    async def get_creation_time(self) -> datetime:
        try:
            exif_dict = await self._get_exif_dict()
            original_date_time = exif_dict["Exif"][
                piexif.ExifIFD.DateTimeOriginal
            ].decode("UTF-8")

            return self._extract_date_time(
                raw_date_time=original_date_time,
                current_timezone=self._current_timezone,
            )
        except KeyError:
            return DEFAULT_DATETIME

    async def get_resolution(self) -> Tuple[int, int]:
        try:
            exif_dict = await self._get_exif_dict()

            return (
                exif_dict["Exif"][piexif.ExifIFD.PixelXDimension],
                exif_dict["Exif"][piexif.ExifIFD.PixelYDimension],
            )
        except KeyError:
            return (-1, -1)
