import unittest
from pathlib import Path

from PIL import Image

from app.controllers.hashing import Hasher


class TestHasher(unittest.IsolatedAsyncioTestCase):
    async def test_hasher_open(self):
        image = Image.open(Path("tests/files/test-canon-eos70D.jpg"))

        hash = await Hasher(image=image).hash()

        self.assertEqual("c643dbe5e4d60f02", hash)
