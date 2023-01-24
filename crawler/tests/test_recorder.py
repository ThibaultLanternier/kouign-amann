import asyncio
import logging
import os
import secrets
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Awaitable
from unittest.mock import MagicMock, Mock, call, patch

from aiohttp import ClientResponse, ClientSession
from requests import Response

from app.controllers.recorder import (AsyncRecorder, CrawlHistoryStore,
                                      PictureRESTRecorder)
from app.models.picture import (PictureData, PictureFile, PictureInfo,
                                PictureOrientation)

TEST_TIME = datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc)


class TestAsyncRecorder(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.mock_session = MagicMock(spec=ClientSession)

        mock_ctor = Mock()
        mock_ctor.return_value = self.mock_session

        self.async_recorder = AsyncRecorder(
            base_url="http://url", client_session_ctor=mock_ctor
        )

        self.response = MagicMock(spec=ClientResponse)
        self.response.status = 200
        self.async_response: Awaitable[ClientResponse] = asyncio.Future()
        self.async_response.set_result(self.response)

    async def test_async_check_picture_exists(self):
        case_list = [(200, True), (403, False)]
        for status_code, expected_result in case_list:
            with self.subTest():
                self.response.status = status_code
                self.mock_session.get.return_value = self.async_response

                self.assertEqual(
                    expected_result,
                    await self.async_recorder.check_picture_exists("XXX"),
                )
                self.mock_session.get.assert_called_with(
                    "http://url/picture/exists/XXX"
                )

    async def test_async_record_info(self):
        test_picture_info = PictureInfo(
            creation_time=TEST_TIME,
            thumbnail="a2d6",
            orientation=PictureOrientation.PORTRAIT,
        )

        self.response.status = 201
        self.mock_session.post.return_value = self.async_response

        await self.async_recorder.record_info(info=test_picture_info, hash="XXXX")

        self.mock_session.post.assert_called_once_with(
            "http://url/picture/XXXX",
            json={
                "creation_time": "2019-11-19T12:46:56.000000Z",
                "thumbnail": "a2d6",
                "orientation": "PORTRAIT",
            },
        )

    async def test_async_record_file(self):
        test_picture_file = PictureFile(
            crawler_id="ABC",
            resolution=(234, 23),
            picture_path="/path",
            last_seen=TEST_TIME,
        )

        self.response.status = 201
        self.mock_session.put.return_value = self.async_response

        await self.async_recorder.record_file(file=test_picture_file, hash="XXXX")

        self.mock_session.put.assert_called_once_with(
            "http://url/picture/file/XXXX",
            json={
                "crawler_id": "ABC",
                "resolution": (234, 23),
                "picture_path": "/path",
                "last_seen": "2019-11-19T12:46:56.000000Z",
            },
        )


class TestPictureRESTRecorder(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

        self.picture_dict = {
            "hash": "c643dbe5e4d60e0a",
            "creation_time": datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc),
            "resolution": (5472, 3648),
            "thumbnail": "THUMBNAIL",
            "picture_path": Path("fake/path"),
            "orientation": PictureOrientation.LANDSCAPE,
        }

        self.picture_data = PictureData(**self.picture_dict)

        picture_dict_no_thumbnail = self.picture_dict.copy()
        picture_dict_no_thumbnail["thumbnail"] = None
        self.picture_data_no_thumbnail = PictureData(**picture_dict_no_thumbnail)

        self.expected_payload = {
            "hash": "c643dbe5e4d60e0a",
            "creation_time": "2019-11-19T12:46:56.000000Z",
            "resolution": (5472, 3648),
            "thumbnail": "THUMBNAIL",
            "picture_path": str(Path("fake/path")),
            "crawl_time": "2019-11-19T12:46:56.000000Z",
            "crawler_id": "xxx",
        }

        self.expected_info_payload = {
            "creation_time": "2019-11-19T12:46:56.000000Z",
            "thumbnail": "THUMBNAIL",
            "orientation": "LANDSCAPE",
        }

        self.expected_file_payload = {
            "resolution": (5472, 3648),
            "picture_path": str(Path("fake/path")),
            "last_seen": "2019-11-19T12:46:56.000000Z",
            "crawler_id": "xxx",
        }

        self.mock_response = MagicMock(name="mock_response", spec=Response)

    @patch("requests.post")
    @patch("requests.put")
    def test_record_OK_with_thumbnail(self, mock_put, mock_post):
        self.mock_response.status_code = 201

        mock_post.return_value = self.mock_response
        mock_put.return_value = self.mock_response

        result = PictureRESTRecorder("BASE_URL").record(
            picture_data=self.picture_data,
            crawl_time=datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc),
            crawler_id="xxx",
        )

        self.assertTrue(result)

        info_call = call(
            "BASE_URL/picture/c643dbe5e4d60e0a", json=self.expected_info_payload
        )
        mock_post.assert_has_calls([info_call])

        file_call = call(
            "BASE_URL/picture/file/c643dbe5e4d60e0a", json=self.expected_file_payload
        )
        mock_put.assert_has_calls([file_call])

    @patch("requests.put")
    def test_record_OK_no_thumbnail(self, mock_put):
        self.mock_response.status_code = 201

        mock_put.return_value = self.mock_response

        result = PictureRESTRecorder("BASE_URL").record(
            picture_data=self.picture_data_no_thumbnail,
            crawl_time=datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc),
            crawler_id="xxx",
        )

        self.assertTrue(result)

        file_call = call(
            "BASE_URL/picture/file/c643dbe5e4d60e0a", json=self.expected_file_payload
        )

        mock_put.assert_has_calls([file_call])

    @patch("requests.put")
    def test_record_no_thumbnail_Not_OK(self, mock_put):
        self.mock_response.status_code = 500

        mock_put.return_value = self.mock_response

        result = PictureRESTRecorder("BASE_URL").record(
            picture_data=self.picture_data_no_thumbnail,
            crawl_time=datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc),
            crawler_id="xxx",
        )

        self.assertFalse(result)

    @patch("requests.post")
    def test_record_thumbnail_Not_OK(self, mock_post):
        self.mock_response.status_code = 500

        mock_post.return_value = self.mock_response

        result = PictureRESTRecorder("BASE_URL").record(
            picture_data=self.picture_data,
            crawl_time=datetime(2019, 11, 19, 12, 46, 56, 0, timezone.utc),
            crawler_id="xxx",
        )

        self.assertFalse(result)


class TestLocalPathStore(unittest.TestCase):
    def setUp(self) -> None:
        self.file_name_list = [
            Path(f"tests/files/local_recorder/{secrets.token_hex(8)}.txt"),
            Path(f"tests/files/local_recorder/{secrets.token_hex(8)}.txt"),
            Path(f"tests/files/local_recorder/{secrets.token_hex(8)}.txt"),
        ]

        for file_name in self.file_name_list:
            with open(str(file_name), "w+") as f:
                f.write("Fichier de test")

        self.recorder = CrawlHistoryStore(
            file_directory=Path("tests/files/local_recorder/")
        )

    def tearDown(self) -> None:
        for file_name in self.file_name_list:
            os.remove(file_name)

        self.recorder.reset()

    def test_add_get_file(self):
        self.recorder.add_file(path=self.file_name_list[0], worker_id=1)
        self.recorder.add_file(path=self.file_name_list[1], worker_id=1)
        self.recorder.add_file(path=self.file_name_list[1], worker_id=2)
        self.recorder.add_file(path=self.file_name_list[2], worker_id=2)

        file_list = set(self.recorder.get_crawl_history().keys())

        self.assertEqual(set(self.file_name_list), file_list)

        current_time = datetime.now()

        for value in self.recorder.get_crawl_history().values():
            delta = current_time - value.last_modified
            self.assertLess(delta, timedelta(seconds=1))
