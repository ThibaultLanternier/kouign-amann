import base64
import io
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

import imagehash
import piexif
from imagehash import ImageHash
from PIL import Image

from app.tools.hash import HashExtractor
from app.models.picture import PictureData


def perception_hashing_function(image_file) -> ImageHash:
    return imagehash.phash(image_file)


def average_hashing_function(image_file) -> ImageHash:
    return imagehash.average_hash(image_file)


class AbstractPictureAnalyzer(ABC):
    @abstractmethod
    def get_data(self, create_thumbnail=True) -> PictureData:
        pass

    @abstractmethod
    def get_recorded_hash(self):
        pass


DEFAULT_DATETIME = datetime(1970, 1, 1, tzinfo=timezone.utc)


class PictureAnalyzer(AbstractPictureAnalyzer):
    def __init__(
        self,
        picture_path: str,
        hashing_function,
        thumbnail_size: int = 300,
        current_timezone: timezone = timezone.utc,
    ):
        self.logger = logging.getLogger("app.picture")

        self.__reference_time = datetime.now()
        self.step_list: List[Tuple[str, timedelta]] = []

        self.picture_path = picture_path
        self.thumbnail_size = thumbnail_size, thumbnail_size
        self.current_timezone = current_timezone

        self.PILImage = Image.open(self.picture_path)
        self.__record_step_duration("open_picture")

        self.image_hash = self.get_recorded_hash()

        if self.image_hash is None:
            self.image_hash = str(hashing_function(self.PILImage))
            self.record_hash_in_exif(self.image_hash)

            self.__record_step_duration("compute_hash")
        else:
            self.__record_step_duration("retrieve_hash_from_exif")

        self.logger.debug(
            "Opening picture %s hash:%s, thumbnail size %s, timezone %s",
            self.picture_path,
            self.image_hash,
            thumbnail_size,
            current_timezone,
        )

        self.creation_time = self.__get_creation_time()
        self.__record_step_duration("retrieve_creation_date")

        self.resolution = self.__get_resolution()
        self.__record_step_duration("retrieve_resolution")

    def __del__(self):
        self.PILImage.close()

    def __record_step_duration(self, step_name: str):
        new_reference_time = datetime.now()

        self.step_list.append((step_name, new_reference_time - self.__reference_time))
        self.__reference_time = new_reference_time

    def record_hash_in_exif(self, picture_hash):
        try:
            exif_dict = piexif.load(self.PILImage.info["exif"])
            exif_dict["0th"][piexif.ImageIFD.ImageID] = f"phash:{picture_hash}"

            exif_bytes = piexif.dump(exif_dict)

            self.PILImage.save(self.picture_path, "jpeg", exif=exif_bytes)

        except Exception:
            return None

    def get_recorded_hash(self):
        try:
            exif_dict = piexif.load(self.PILImage.info["exif"])
            raw_hash = exif_dict["0th"][piexif.ImageIFD.ImageID].decode("ASCII")

            return HashExtractor().extract(raw_hash)

        except Exception:
            return None

    def __get_creation_time(self):
        try:
            exif_dict = piexif.load(self.PILImage.info["exif"], key_is_name=True)
            raw_original_date_time = exif_dict["Exif"]["DateTimeOriginal"].decode(
                "UTF-8"
            )
            return self.__extract_date_time(
                raw_date_time=raw_original_date_time,
                current_timezone=self.current_timezone,
            )

        except Exception:
            return DEFAULT_DATETIME

    def __get_resolution(self) -> Tuple[int, int]:
        try:
            exif_dict = piexif.load(self.PILImage.info["exif"], key_is_name=True)

            return (
                exif_dict["Exif"]["PixelXDimension"],
                exif_dict["Exif"]["PixelYDimension"],
            )

        except Exception:
            return (-1, -1)

    def __extract_date_time(
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

    def record_thumbnail(self, file_name):
        self.PILImage.thumbnail(self.thumbnail_size)
        self.PILImage.save(file_name)

    def get_base64_thumbnail(self):
        """
        Returns a JPEG thumbnail encoded as Base64 UTF-8 string
        """
        self.__reference_time = datetime.now()

        self.PILImage.thumbnail(self.thumbnail_size)

        with io.BytesIO() as thumbnail_output:
            self.PILImage.save(thumbnail_output, format="JPEG")
            self.__record_step_duration("generate_thumbnail")
            return base64.b64encode(thumbnail_output.getvalue()).decode("UTF-8")

    def get_data(self, create_thumbnail=True) -> PictureData:
        output = {
            "hash": self.image_hash,
            "creation_time": self.creation_time,
            "resolution": self.resolution,
            "picture_path": self.picture_path,
            "thumbnail": None,
        }

        if create_thumbnail:
            output["thumbnail"] = self.get_base64_thumbnail()

        return PictureData(**output)


class PictureAnalyzerFactory:
    def perception_hash(
        self, picture_path: str, thumbnail_size: int = 300
    ) -> AbstractPictureAnalyzer:
        return PictureAnalyzer(
            picture_path, perception_hashing_function, thumbnail_size
        )
