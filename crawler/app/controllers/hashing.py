from PIL import Image

import imagehash


class Hasher:
    def __init__(self, image: Image) -> None:
        self._image = image

    async def hash(self) -> str:
        return str(imagehash.phash(self._image))
