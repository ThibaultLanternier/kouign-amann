import os
import secrets
import shutil
import unittest
from datetime import datetime, timezone
from pathlib import Path

from app.controllers.exif import ExifManager

TEST_PICTURE_CAMERA = "tests/files/test-canon-eos70D-exif.jpg"
TEST_PICTURE_OLD_SCAN = "tests/files/0025.jpg"
TEST_PICTURE_FUJI_CAMERA = "tests/files/DSCF1057.JPG"
TEST_PICTURE_OLD_SCAN_2 = "tests/files/0001.jpg"


class TestExifManager(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def _copy_file(cls, file_name: str) -> str:
        uniq_id = secrets.token_hex(8)
        file_name_copy = f"tests/files/exif-{uniq_id}.jpg"
        shutil.copyfile(file_name, file_name_copy)

        return file_name_copy

    @classmethod
    def setUpClass(cls):
        cls.test_file_old_scan = cls._copy_file(TEST_PICTURE_OLD_SCAN_2)

    @classmethod
    def tearDownClass(cls):
        pass
        os.remove(cls.test_file_old_scan)

    async def test_get_exif_dict_camera(self):
        exif_dict = await ExifManager(path=Path(TEST_PICTURE_CAMERA))._get_exif_dict()

        self.assertIsInstance(exif_dict, dict)

    async def test_get_exif_dict_old_scan(self):
        exif_dict = await ExifManager(path=Path(TEST_PICTURE_OLD_SCAN))._get_exif_dict()

        self.assertIsInstance(exif_dict, dict)

    async def test_get_exif_dict_fuji_camera(self):
        exif_dict = await ExifManager(
            path=Path(TEST_PICTURE_FUJI_CAMERA)
        )._get_exif_dict()

        self.assertIsInstance(exif_dict, dict)

    async def test_get_exif_dict_old_scan_2(self):
        exif_dict = await ExifManager(
            path=Path(TEST_PICTURE_FUJI_CAMERA)
        )._get_exif_dict()

        self.assertIsInstance(exif_dict, dict)

    async def test_record_hash_in_exif(self):
        HASH = "c643dbe5e4d60f02"

        exif_manager = ExifManager(path=Path(self.__class__.test_file_old_scan))

        self.assertIsNone(await exif_manager.get_hash())

        await exif_manager.record_hash_in_exif(HASH)
        self.assertEqual(HASH, await exif_manager.get_hash())

        new_exif_manager = ExifManager(path=Path(self.__class__.test_file_old_scan))
        self.assertEqual(HASH, await new_exif_manager.get_hash())

    async def test_get_creation_time_old_picture(self):
        exif_manager = ExifManager(path=Path(TEST_PICTURE_OLD_SCAN_2))

        self.assertEqual(
            datetime(1970, 1, 1, tzinfo=timezone.utc),
            await exif_manager.get_creation_time(),
        )

    async def test_get_creation_time_recent_picture(self):
        exif_manager = ExifManager(path=Path(TEST_PICTURE_CAMERA))

        self.assertEqual(
            datetime(2019, 11, 19, 12, 46, 56, tzinfo=timezone.utc),
            await exif_manager.get_creation_time(),
        )

    async def test_get_creation_resolution_old_picture(self):
        exif_manager = ExifManager(path=Path(TEST_PICTURE_OLD_SCAN_2))

        self.assertEqual((-1, -1), await exif_manager.get_resolution())

    async def test_get_creation_resolution_recent_picture(self):
        exif_manager = ExifManager(path=Path(TEST_PICTURE_CAMERA))

        self.assertEqual((5472, 3648), await exif_manager.get_resolution())
