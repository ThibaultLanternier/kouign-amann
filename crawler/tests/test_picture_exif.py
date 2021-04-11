import os
import secrets
import shutil
import unittest

from app.controllers.picture import PictureAnalyzerFactory

TEST_PICTURE = "tests/files/test-canon-eos70D-exif.jpg"


class TestPictureExif(unittest.TestCase):
    def setUp(self):
        uniq_id = secrets.token_hex(8)
        self.test_file_copy = f"tests/files/{uniq_id}.jpg"
        shutil.copyfile(TEST_PICTURE, self.test_file_copy)

    def tearDown(self):
        os.remove(self.test_file_copy)

    def test_record_hash_in_exif(self):
        test_hash = secrets.token_hex(8)

        test_picture = PictureAnalyzerFactory().perception_hash(self.test_file_copy)
        test_picture.record_hash_in_exif(test_hash)

        new_test_picture = PictureAnalyzerFactory().perception_hash(self.test_file_copy)

        self.assertEqual(test_hash, new_test_picture.get_recorded_hash())
