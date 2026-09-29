import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from app.tools.thumbnail import create_thumbnail

TEST_PICTURE = Path("tests/files/test-canon-eos70D.jpg")


class TestCreateThumbnail(unittest.TestCase):
    def test_create_thumbnail_OK(self):
        thumbnail = create_thumbnail(TEST_PICTURE.read_bytes(), max_size=200)

        with Image.open(BytesIO(thumbnail)) as image:
            self.assertEqual("JPEG", image.format)
            self.assertEqual(200, max(image.size))

    def test_create_thumbnail_keeps_small_picture_size(self):
        with Image.open(TEST_PICTURE) as original:
            original_size = original.size

        thumbnail = create_thumbnail(TEST_PICTURE.read_bytes(), max_size=100000)

        with Image.open(BytesIO(thumbnail)) as image:
            self.assertEqual(original_size, image.size)

    def test_create_thumbnail_invalid_size(self):
        with self.assertRaises(ValueError):
            create_thumbnail(TEST_PICTURE.read_bytes(), max_size=0)
