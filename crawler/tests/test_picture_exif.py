import os
import secrets
import shutil
import unittest

from app.controllers.picture import (AbstractPictureAnalyzer,
                                     PictureAnalyzerFactory)

TEST_PICTURE_CAMERA = "tests/files/test-canon-eos70D-exif.jpg"
TEST_PICTURE_OLD_SCAN = "tests/files/0025.jpg"
TEST_PICTURE_FUJI_CAMERA = "tests/files/DSCF1057.JPG"


class TestPictureExif(unittest.TestCase):
    @classmethod
    def _copy_file(cls, file_name: str) -> str:
        uniq_id = secrets.token_hex(8)
        file_name_copy = f"tests/files/{uniq_id}.jpg"
        shutil.copyfile(file_name, file_name_copy)

        return file_name_copy

    @classmethod
    def setUpClass(cls):
        cls.test_file_camera = cls._copy_file(TEST_PICTURE_CAMERA)
        cls.test_file_old_scan = cls._copy_file(TEST_PICTURE_OLD_SCAN)
        cls.test_file_fuji_camera = cls._copy_file(TEST_PICTURE_FUJI_CAMERA)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_file_camera)
        os.remove(cls.test_file_old_scan)
        os.remove(cls.test_file_fuji_camera)

    def _record_hash_in_picture(
        self, hash: str, picture_file: str
    ) -> AbstractPictureAnalyzer:
        picture = PictureAnalyzerFactory().perception_hash(picture_file)
        picture.record_hash_in_exif(hash)

        new_picture = PictureAnalyzerFactory().perception_hash(picture_file)
        return new_picture

    def test_record_hash_in_exif_camera_picture(self):
        test_hash = secrets.token_hex(8)
        picture_with_hash = self._record_hash_in_picture(
            test_hash, self.__class__.test_file_camera
        )

        self.assertEqual(test_hash, picture_with_hash.get_recorded_hash())

    def test_record_hash_in_exif_scan_picture(self):
        test_hash = secrets.token_hex(8)
        picture_with_hash = self._record_hash_in_picture(
            test_hash, self.__class__.test_file_old_scan
        )

        self.assertEqual(test_hash, picture_with_hash.get_recorded_hash())

    def test_record_hash_in_exif_fuji_picture(self):
        test_hash = secrets.token_hex(8)
        picture_with_hash = self._record_hash_in_picture(
            test_hash, self.__class__.test_file_fuji_camera
        )

        self.assertEqual(test_hash, picture_with_hash.get_recorded_hash())
