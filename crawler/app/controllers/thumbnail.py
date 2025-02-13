import io
import base64

from PIL import ImageOps
from PIL.Image import Image

from app.models.picture import PictureOrientation

DEFAULT_THUMBNAIL_SIZE = 800


class ThumbnailImage:
    def __init__(
        self, image: Image, thumbnail_size: int = DEFAULT_THUMBNAIL_SIZE
    ) -> None:
        self._image = image
        self._thumbnail_size = (thumbnail_size, thumbnail_size)

    async def _get_thumbnail(self) -> Image:
        if not hasattr(self, "thumbnail"):
            self._thumbnail = ImageOps.exif_transpose(self._image)
            if self._thumbnail is None:
                raise Exception("Thumbnail is not definded")

            self._thumbnail.thumbnail(self._thumbnail_size)

        if self._thumbnail is None:
            raise Exception("Thumbnail is not definded")

        return self._thumbnail

    async def get_base64_thumbnail(self) -> str:
        thumbnail = await self._get_thumbnail()

        with io.BytesIO() as thumbnail_output:
            thumbnail.save(thumbnail_output, format="JPEG")
            return base64.b64encode(thumbnail_output.getvalue()).decode("UTF-8")

    async def get_orientation(self) -> PictureOrientation:
        thumbnail = await self._get_thumbnail()
        size = thumbnail.size

        if size[0] > size[1]:
            return PictureOrientation.LANDSCAPE
        else:
            return PictureOrientation.PORTRAIT
