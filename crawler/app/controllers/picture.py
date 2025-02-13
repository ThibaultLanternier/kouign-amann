import base64
import io
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Tuple
from pathlib import Path

import imagehash
import piexif
from imagehash import ImageHash
from PIL import Image, ImageOps, UnidentifiedImageError
from PIL.Image import Image as ImageType

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
    def _get_recorded_hash(self) -> str:
        pass

    @abstractmethod
    def get_metric(self) -> MetricRecorder:
        pass

    @abstractmethod
    def get_hash(self) -> str:
        pass


DEFAULT_DATETIME = datetime(1970, 1, 1, tzinfo=timezone.utc)

DEFAULT_THUMBNAIL_SIZE = 800


class CorruptedPictureFileError(Exception):
    pass


class PictureAnalyzer(AbstractPictureAnalyzer):
    def __init__(
        self,
        picture_path: Path,
        hashing_function,
        thumbnail_size: int = DEFAULT_THUMBNAIL_SIZE,
        current_timezone: timezone = timezone.utc,
    ):
        self._logger = logging.getLogger("app.picture")

        self._recorder = MetricRecorder(measurement_name="picture_analyze")

        self._picture_path = picture_path
        self._thumbnail_size = thumbnail_size, thumbnail_size
        self._current_timezone = current_timezone

        try:
            self._PILImage = Image.open(self._picture_path)
        except UnidentifiedImageError:
            raise CorruptedPictureFileError(
                f"File {self._picture_path} is not a correct image file"
            )

        self._recorder.add_step("open_picture")

        self._image_hash = self._get_recorded_hash()

        if self._image_hash is None:
            self._recorder.add_tag("hash_origin", "compute")
            self._image_hash = str(hashing_function(self._PILImage))
            self._record_hash_in_exif(self._image_hash)
            self._recorder.add_step("hash_generation")
        else:
            self._recorder.add_tag("hash_origin", "retrieve")
            self._recorder.add_step("hash_retrieval")

        self._recorder.set_hash(self._image_hash)

        self._logger.debug(
            "Opening picture %s hash:%s, thumbnail size %s, timezone %s",
            self._picture_path,
            self._image_hash,
            thumbnail_size,
            current_timezone,
        )

        self._creation_time = self._get_creation_time()
        self._recorder.add_step("retrieve_creation_date")

        self.resolution = self._get_resolution()
        self._recorder.add_step("retrieve_resolution")

        self._thumbnail = None

    def __del__(self):
        if hasattr(self, "PILImage"):
            self._PILImage.close()

    def _record_hash_in_exif(self, picture_hash):
        try:
            if "exif" in self._PILImage.info:
                exif_dict = piexif.load(self._PILImage.info["exif"])
            else:
                exif_dict = piexif.load(str(self._picture_path))

            exif_dict["0th"][piexif.ImageIFD.ImageID] = f"phash:{picture_hash}"

            exif_bytes = piexif.dump(exif_dict)

            self._PILImage.save(self._picture_path, "jpeg", exif=exif_bytes)

        except Exception:
            return None

    def _get_recorded_hash(self):
        try:
            exif_dict = piexif.load(self._PILImage.info["exif"])
            hash = exif_dict["0th"][piexif.ImageIFD.ImageID].decode("ASCII")

            return HashExtractor().extract(hash)

        except Exception:
            return None

    def _get_creation_time(self):
        try:
            exif_dict = piexif.load(self._PILImage.info["exif"], key_is_name=True)
            original_date_time = exif_dict["Exif"]["DateTimeOriginal"].decode("UTF-8")
            return self._extract_date_time(
                raw_date_time=original_date_time,
                current_timezone=self._current_timezone,
            )

        except Exception:
            return DEFAULT_DATETIME

    def _get_resolution(self) -> Tuple[int, int]:
        try:
            exif_dict = piexif.load(self._PILImage.info["exif"], key_is_name=True)

            return (
                exif_dict["Exif"]["PixelXDimension"],
                exif_dict["Exif"]["PixelYDimension"],
            )

        except Exception:
            return (-1, -1)

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

    def _get_thumbnail(self) -> ImageType:
        """
        Returns a JPEG thumbnail of the image
        """
        if self._thumbnail is None:
            pivoted_image: ImageType | None = ImageOps.exif_transpose(self._PILImage)
            if pivoted_image is None:
                raise Exception("pivoted_image is not definded")

            pivoted_image.thumbnail(self._thumbnail_size)

            self._thumbnail = pivoted_image

        if self._thumbnail is None:
            raise Exception("Thumbnail is not definded")

        return self._thumbnail

    def _get_orientaton(self) -> PictureOrientation:
        size = self._get_thumbnail().size

        if size[0] > size[1]:
            return PictureOrientation.LANDSCAPE
        else:
            return PictureOrientation.PORTRAIT

    def _get_base64_thumbnail(self) -> str:
        """
        Returns a JPEG thumbnail encoded as Base64 UTF-8 string
        """
        thumbnail = self._get_thumbnail()

        with io.BytesIO() as thumbnail_output:
            thumbnail.save(thumbnail_output, format="JPEG")
            self._recorder.add_step("generate_thumbnail")
            return base64.b64encode(thumbnail_output.getvalue()).decode("UTF-8")

    def get_data(self, create_thumbnail=True) -> PictureData:
        output = {
            "hash": self._image_hash,
            "creation_time": self._creation_time,
            "resolution": self.resolution,
            "picture_path": self._picture_path,
            "thumbnail": None,
            "orientation": None,
        }

        if create_thumbnail:
            output["thumbnail"] = self._get_base64_thumbnail()
            output["orientation"] = self._get_orientaton()

        return PictureData(**output)

    def get_metric(self) -> MetricRecorder:
        return self._recorder

    def get_hash(self) -> str:
        return self._image_hash


class PictureAnalyzerFactory:
    def perception_hash(
        self, picture_path: Path, thumbnail_size: int = DEFAULT_THUMBNAIL_SIZE
    ) -> AbstractPictureAnalyzer:
        return PictureAnalyzer(
            picture_path, perception_hashing_function, thumbnail_size
        )
