import dataclasses
import secrets
import unittest
from datetime import datetime, timedelta, timezone
from app.models.picture import PictureOrientation

from imagehash import ImageHash
from PIL import Image

from app.controllers.picture import (PictureAnalyzer, PictureAnalyzerFactory,
                                     perception_hashing_function)
from app.tools.debug import record_thumbnail_to_html


class TestPerceptionHashingFunction(unittest.TestCase):
    def __get_image_hash(self, image_path: str) -> ImageHash:
        with Image.open(image_path) as image:
            return perception_hashing_function(image)

    def test_perception_hashing_function(self):
        self.assertEqual(
            "c643dbe5e4d60f02",
            str(self.__get_image_hash("tests/files/test-canon-eos70D.jpg")),
        )

    def test_perception_hashing_function_compare(self):
        difference = self.__get_image_hash(
            "tests/files/test-canon-eos70D.jpg"
        ) - self.__get_image_hash("tests/files/IMG_7095-300px.JPG")

        self.assertLess(difference, 3)

    def test_perception_hashing_function_compare_different(self):
        difference = self.__get_image_hash(
            "tests/files/test-canon-eos70D.jpg"
        ) - self.__get_image_hash("tests/files/test_image.JPG")

        self.assertGreater(difference, 30)


CANON_EOS_70D_THUMBNAIL = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAADAAUDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCW+sbTUPKkvbaK5cAgGZQ+BnHGenTtRRRWFVtTZ0UkuRH/2Q==" # noqa: E501
VERTICAL_IMAGE_THUMBNAIL = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAKAAcDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDGh1G30fQ7W8vNhFwCY4UbMjnPX0A6/pRXn92Sd3J4VQPbpRXYsRNKyMPZRep//9k=" # noqa: E501
HORIZONTAL_IMAGE_THUMBNAIL = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAHAAoDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDSvLy51O1ktm1AzQW8wXURdF2IiI58sjoevSuGbwJ4clcyRXWreWx3JxH0PTrRRU124zaRdBJ002f/2Q=="  # noqa: E501

VERTICAL_IMAGE_NAME = "tests/files/test_image.JPG"
HORIZONTAL_IMAGE_NAME = "tests/files/IMG_7095-300px.JPG"

class TestPicture(unittest.TestCase):
    def test_factory(self):
        test_picture = PictureAnalyzerFactory().perception_hash(
            "tests/files/test-canon-eos70D.jpg"
        )
        self.assertIsInstance(test_picture, PictureAnalyzer)

    def test_get_base64_thumbnail(self):
        test_picture = PictureAnalyzer(
            "tests/files/test-canon-eos70D.jpg", perception_hashing_function, 5
        )
        base64_thumbnail = test_picture.get_base64_thumbnail()

        self.assertEqual(CANON_EOS_70D_THUMBNAIL, base64_thumbnail)

    def test_get_base64_original_image_unchanged(self):
        test_picture = PictureAnalyzer(
            VERTICAL_IMAGE_NAME, perception_hashing_function, 10
        )

        start_size = test_picture.PILImage.size
        test_picture.get_base64_thumbnail()

        self.assertEqual(start_size, test_picture.PILImage.size)

    def test_get_orientation_vertical(self):
        test_picture = PictureAnalyzer(
            VERTICAL_IMAGE_NAME, perception_hashing_function
        )

        self.assertEqual(PictureOrientation.PORTRAIT, test_picture.get_orientaton())

    def test_get_orientation_horizontal(self):
        test_picture = PictureAnalyzer(
            HORIZONTAL_IMAGE_NAME, perception_hashing_function
        )

        self.assertEqual(PictureOrientation.LANDSCAPE, test_picture.get_orientaton())

    def test_get_base64_thumbnail_vertical(self):
        test_picture = PictureAnalyzer(
            VERTICAL_IMAGE_NAME, perception_hashing_function, 10
        )

        test_picture.get_orientaton()
        base64_thumbnail = test_picture.get_base64_thumbnail()

        self.maxDiff = None
        self.assertEqual(VERTICAL_IMAGE_THUMBNAIL, base64_thumbnail)

    def test_get_base64_thumbnail_horizontal(self):
        test_picture = PictureAnalyzer(
            HORIZONTAL_IMAGE_NAME, perception_hashing_function, 10
        )

        test_picture.get_orientaton()
        base64_thumbnail = test_picture.get_base64_thumbnail()

        self.maxDiff = None
        self.assertEqual(HORIZONTAL_IMAGE_THUMBNAIL, base64_thumbnail)


    def test_get_data(self):
        test_picture = PictureAnalyzer(
            "tests/files/test-canon-eos70D.jpg", perception_hashing_function, 5
        )

        expected_dict = {
            "hash": "c643dbe5e4d60e0a",
            "creation_time": datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc),
            "resolution": (5472, 3648),
            "thumbnail": CANON_EOS_70D_THUMBNAIL,
            "picture_path": "tests/files/test-canon-eos70D.jpg",
            "orientation": PictureOrientation.LANDSCAPE
        }
        actual_data = test_picture.get_data()

        self.assertEqual(expected_dict, dataclasses.asdict(actual_data))

    def test_get_data_missing_date(self):
        test_picture = PictureAnalyzer(
            "tests/files/0025.jpg", perception_hashing_function, 5
        )

        expected_dict = {
            "hash": "dc5a230bcb89ddc8",
            "creation_time": datetime(1970, 1, 1, tzinfo=timezone.utc),
            "resolution": (-1, -1),
            "picture_path": "tests/files/0025.jpg",
            "orientation": PictureOrientation.LANDSCAPE
        }
        actual_dict = dataclasses.asdict(test_picture.get_data())
        actual_dict.pop("thumbnail")

        self.assertEqual(expected_dict, actual_dict)

    def test_get_data_no_thumbnail(self):
        test_picture = PictureAnalyzer(
            "tests/files/test-canon-eos70D.jpg", perception_hashing_function, 5
        )

        expected_dict = {
            "hash": "c643dbe5e4d60e0a",
            "creation_time": datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc),
            "resolution": (5472, 3648),
            "picture_path": "tests/files/test-canon-eos70D.jpg",
            "thumbnail": None,
            "orientation": None
        }
        actual_dict = test_picture.get_data(create_thumbnail=False)

        self.assertEqual(expected_dict, dataclasses.asdict(actual_dict))

    def test_perception_hash_resized(self):
        """
        Checks if an image has the same hash as its thumbnail
        """
        test_picture = PictureAnalyzer(
            "tests/files/test-canon-eos70D.jpg", perception_hashing_function, 600
        )
        test_picture_small = PictureAnalyzer(
            "tests/files/test-canon-eos70D-small.jpg", perception_hashing_function, 600
        )

        self.assertEqual(test_picture.image_hash, test_picture_small.image_hash)

    def test_perception_hash_black_white(self):
        """
        Checks if an image has the same hash as its thumbnail
        """
        test_picture = PictureAnalyzer(
            "tests/files/test-canon-eos70D.jpg", perception_hashing_function, 600
        )
        test_picture_small = PictureAnalyzer(
            "tests/files/test-canon-eos70D-bw.jpg", perception_hashing_function, 600
        )

        self.assertEqual(test_picture.image_hash, test_picture_small.image_hash)

    def test_resolution(self):
        test_picture = PictureAnalyzer(
            "tests/files/test-canon-eos70D.jpg",
            perception_hashing_function,
            600,
            timezone(timedelta(0, 3600)),
        )
        expected = (5472, 3648)

        self.assertEqual(expected, test_picture.resolution)

    def test_time_extraction(self):
        test_picture = PictureAnalyzer(
            "tests/files/test-canon-eos70D.jpg",
            perception_hashing_function,
            600,
            timezone(timedelta(0, 3600)),
        )
        expected = datetime(2019, 11, 19, 11, 46, 56, 0, timezone.utc)

        self.assertEqual(expected, test_picture.creation_time)

    def test_time_extraction_missing_exif(self):
        test_picture = PictureAnalyzer(
            "tests/files/picture-no-exif.jpg",
            perception_hashing_function,
            600,
            timezone(timedelta(0, 3600)),
        )

        self.assertEqual(
            datetime(1970, 1, 1, tzinfo=timezone.utc), test_picture.creation_time
        )
        self.assertEqual((-1, -1), test_picture.resolution)
