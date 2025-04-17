import datetime
import unittest
import uuid
from pathlib import Path

from app.controllers.async_file_recorder import AsyncFileRecorder


class TestAsyncFileRecorder(unittest.IsolatedAsyncioTestCase):
    async def test_async_record_file(self):
        test_file_recorder = AsyncFileRecorder(Path("tests/files/photos/"))

        picture_path = Path("tests/files/test-canon-eos70D.jpg")
        fake_hash = uuid.uuid4().hex
        creation_time = datetime.datetime(2024, 11, 30, 11, 45)

        self.assertFalse(await test_file_recorder.check_picture_exists(fake_hash))

        self.assertTrue(await test_file_recorder.record_file(
            hash=fake_hash, 
            picture_path=picture_path, 
            creation_time=creation_time
        ))
        self.assertTrue(await test_file_recorder.check_picture_exists(fake_hash))

    async def test_async_record_file_check_exists(self):
        test_file_recorder = AsyncFileRecorder(Path("tests/files/photos/"))

        self.assertTrue(
            await test_file_recorder.check_picture_exists("e7975821ce2e1a55")
        )

    async def test_async_record_file_check_exists_other(self):
        test_file_recorder = AsyncFileRecorder(Path("tests/files/photos/"))

        self.assertTrue(
            await test_file_recorder.check_picture_exists(
                "1ad0318cff38424c9d0351837f03e473"
            )
        )
