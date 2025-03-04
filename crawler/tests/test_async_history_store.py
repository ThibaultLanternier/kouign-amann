import asyncio
import secrets
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiofiles
from aiofiles import os as async_os

from app.controllers.async_history_store import AsyncCrawlHistoryStore

TEST_TIME = datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc)


class TestAsyncCrawlHistoryStore(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.file_name_list = [
            Path(f"tests/files/local_recorder/{secrets.token_hex(8)}.txt"),
            Path(f"tests/files/local_recorder/{secrets.token_hex(8)}.txt"),
            Path(f"tests/files/local_recorder/{secrets.token_hex(8)}.txt"),
        ]

        for file_name in self.file_name_list:
            async with aiofiles.open(str(file_name), "w+") as f:
                await f.write("Fichier de test")

        self.recorder = AsyncCrawlHistoryStore(
            file_directory=Path("tests/files/local_recorder/")
        )

    async def test_async_add_get_file(self):
        await asyncio.gather(
            self.recorder.add_file(path=self.file_name_list[0]),
            self.recorder.add_file(path=self.file_name_list[1]),
            self.recorder.add_file(path=self.file_name_list[1]),
            self.recorder.add_file(path=self.file_name_list[2]),
        )

        crawl_history = self.recorder.get_crawl_history()

        file_list = set(crawl_history.keys())

        self.assertEqual(set(self.file_name_list), file_list)

        current_time = datetime.now()

        for value in crawl_history.values():
            delta = current_time - value.last_modified
            self.assertLess(delta, timedelta(seconds=1))

    def test_get_crawl_history_first_time(self):
        empty_result = self.recorder.get_crawl_history()

        self.assertEqual({}, empty_result)

    async def asyncTearDown(self) -> None:
        for file_name in self.file_name_list:
            await async_os.remove(file_name)

        await self.recorder.reset()
