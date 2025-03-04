import datetime
import unittest
import uuid
from pathlib import Path

from app.controllers.async_file_recorder import AsyncFileRecorder
from app.models.picture import PictureFile, PictureInfo, PictureOrientation


class TestAsyncFileRecorder(unittest.IsolatedAsyncioTestCase):
    async def test_async_record_file(self):
        test_file_recorder = AsyncFileRecorder(Path("tests/files/photos/"))

        picture_info = PictureInfo(
            creation_time=datetime.datetime(2024, 11, 30, 11, 45),
            thumbnail="xxx",
            orientation=PictureOrientation.LANDSCAPE,
        )

        picture_file = PictureFile(
            crawler_id="xx",
            resolution=[1920, 1080],
            picture_path=Path("tests/files/test-canon-eos70D.jpg"),
            last_seen=datetime.datetime.now(),
        )

        fake_hash = uuid.uuid4().hex

        self.assertFalse(await test_file_recorder.check_picture_exists(fake_hash))

        self.assertTrue(await test_file_recorder.record_info(picture_info, fake_hash))
        self.assertTrue(await test_file_recorder.record_file(picture_file, fake_hash))
        
        self.assertTrue(await test_file_recorder.check_picture_exists(fake_hash))
    
    async def test_async_record_file_check_exists(self):
        test_file_recorder = AsyncFileRecorder(Path("tests/files/photos/"))

        self.assertTrue(await test_file_recorder.check_picture_exists('e7975821ce2e1a55'))
    
    async def test_async_record_file_check_exists_other(self):
        test_file_recorder = AsyncFileRecorder(Path("tests/files/photos/"))

        self.assertTrue(await test_file_recorder.check_picture_exists('1ad0318cff38424c9d0351837f03e473'))
    
