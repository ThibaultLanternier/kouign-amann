import logging
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from requests import Response

from app.controllers.recorder import PictureRESTRecorder
from app.models.picture import PictureData, PictureOrientation


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
