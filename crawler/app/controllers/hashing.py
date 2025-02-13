from PIL.Image import Image

import imagehash


class HasherException(Exception):
    pass


class Hasher:
    def __init__(self, image: Image) -> None:
        self._image = image

    async def hash(self) -> str:
        try:
            return str(imagehash.phash(self._image))
        except Exception:
            raise HasherException()
