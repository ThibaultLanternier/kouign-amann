import base64
import io
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

import imagehash
import piexif
from imagehash import ImageHash
from PIL import Image, ImageOps

from app.tools.hash import HashExtractor
from app.models.picture import PictureData, PictureOrientation
from app.tools.metrics import MetricRecorder


def perception_hashing_function(image_file) -> ImageHash:
    return imagehash.phash(image_file)


def average_hashing_function(image_file) -> ImageHash:
    return imagehash.average_hash(image_file)


class AbstractPictureAnalyzer(ABC):
    @abstractmethod
    def get_data(self, create_thumbnail=True) -> PictureData:
        pass

    @abstractmethod
    def get_recorded_hash(self) -> str:
        pass

    @abstractmethod
    def get_metric(self) -> MetricRecorder:
        pass


DEFAULT_DATETIME = datetime(1970, 1, 1, tzinfo=timezone.utc)

DEFAULT_THUMBNAIL_SIZE = 800


class PictureAnalyzer(AbstractPictureAnalyzer):
    def __init__(
        self,
        picture_path: str,
        hashing_function,
        thumbnail_size: int = DEFAULT_THUMBNAIL_SIZE,
        current_timezone: timezone = timezone.utc,
    ):
        self.logger = logging.getLogger("app.picture")

        self.__recorder = MetricRecorder(measurement_name="picture_analyze")
        self.step_list: List[Tuple[str, timedelta]] = []

        self.picture_path = picture_path
        self.thumbnail_size = thumbnail_size, thumbnail_size
        self.current_timezone = current_timezone

        self.PILImage = Image.open(self.picture_path)
        self.__recorder.add_step("open_picture")

        self.image_hash = self.get_recorded_hash()

        if self.image_hash is None:
            self.__recorder.add_tag("hash_origin", "compute")
            self.image_hash = str(hashing_function(self.PILImage))
            self.record_hash_in_exif(self.image_hash)
        else:
            self.__recorder.add_tag("hash_origin", "retrieve")

        self.__recorder.set_hash(self.image_hash)
        self.__recorder.add_step("hash_generation")

        self.logger.debug(
            "Opening picture %s hash:%s, thumbnail size %s, timezone %s",
            self.picture_path,
            self.image_hash,
            thumbnail_size,
            current_timezone,
        )

        self.creation_time = self.__get_creation_time()
        self.__recorder.add_step("retrieve_creation_date")

        self.resolution = self.__get_resolution()
        self.__recorder.add_step("retrieve_resolution")

        self.__thumbnail = None

    def __del__(self):
        if hasattr(self, "PILImage"):
            self.PILImage.close()

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
            hash = exif_dict["0th"][piexif.ImageIFD.ImageID].decode("ASCII")

            return HashExtractor().extract(hash)

        except Exception:
            return None

    def __get_creation_time(self):
        try:
            exif_dict = piexif.load(self.PILImage.info["exif"], key_is_name=True)
            original_date_time = exif_dict["Exif"]["DateTimeOriginal"].decode("UTF-8")
            return self.__extract_date_time(
                raw_date_time=original_date_time,
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

    def __get_thumbnail(self) -> Image:
        """
        Returns a JPEG thumbnail of the image
        """
        if self.__thumbnail is None:
            pivoted_image = ImageOps.exif_transpose(self.PILImage)
            pivoted_image.thumbnail(self.thumbnail_size)

            self.__thumbnail = pivoted_image

        return self.__thumbnail

    def get_orientaton(self) -> PictureOrientation:
        size = self.__get_thumbnail().size

        if size[0] > size[1]:
            return PictureOrientation.LANDSCAPE
        else:
            return PictureOrientation.PORTRAIT

    def get_base64_thumbnail(self) -> str:
        """
        Returns a JPEG thumbnail encoded as Base64 UTF-8 string
        """
        thumbnail = self.__get_thumbnail()

        with io.BytesIO() as thumbnail_output:
            thumbnail.save(thumbnail_output, format="JPEG")
            self.__recorder.add_step("generate_thumbnail")
            return base64.b64encode(thumbnail_output.getvalue()).decode("UTF-8")

    def get_data(self, create_thumbnail=True) -> PictureData:
        output = {
            "hash": self.image_hash,
            "creation_time": self.creation_time,
            "resolution": self.resolution,
            "picture_path": self.picture_path,
            "thumbnail": None,
            "orientation": None,
        }

        if create_thumbnail:
            output["thumbnail"] = self.get_base64_thumbnail()
            output["orientation"] = self.get_orientaton()

        return PictureData(**output)

    def get_metric(self) -> MetricRecorder:
        return self.__recorder


class PictureAnalyzerFactory:
    def perception_hash(
        self, picture_path: str, thumbnail_size: int = DEFAULT_THUMBNAIL_SIZE
    ) -> AbstractPictureAnalyzer:
        return PictureAnalyzer(
            picture_path, perception_hashing_function, thumbnail_size
        )
