import asyncio
import unittest
from datetime import datetime, timezone
from typing import Awaitable
from unittest.mock import MagicMock, Mock

from aiohttp import ClientResponse, ClientSession

from app.controllers.async_recorder import AsyncRecorder
from app.models.picture import PictureFile, PictureInfo, PictureOrientation

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
