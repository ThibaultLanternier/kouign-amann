from io import BytesIO

from PIL import Image, ImageOps

DEFAULT_THUMBNAIL_SIZE = 400


def create_thumbnail(
    picture_buffer: bytes, max_size: int = DEFAULT_THUMBNAIL_SIZE
) -> bytes:
    """Return a JPEG thumbnail whose largest side is at most max_size pixels"""
    if max_size <= 0:
        raise ValueError(f"Thumbnail size must be positive, got {max_size}")

    with Image.open(BytesIO(picture_buffer)) as image:
        thumbnail = ImageOps.exif_transpose(image)
        thumbnail.thumbnail((max_size, max_size))

        if thumbnail.mode != "RGB":
            thumbnail = thumbnail.convert("RGB")

        output = BytesIO()
        thumbnail.save(output, format="JPEG", quality=85)

        return output.getvalue()
