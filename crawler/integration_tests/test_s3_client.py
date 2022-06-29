import unittest
import os
import uuid

from typing import List
from app.storage.basic import S3Client, S3Content

TEST_PICTURE = "tests/files/test.txt"
TEST_BUCKET = "picture.backup.test"

class TestS3Client(unittest.TestCase):
    def setUp(self) -> None:
        self.assertIsNotNone(os.getenv("TEST_AWS_KEY"))
        self.assertIsNotNone(os.getenv("TEST_AWS_SECRET"))

        self._client = S3Client(
            aws_key = os.getenv("TEST_AWS_KEY"),
            aws_secret = os.getenv("TEST_AWS_SECRET")
        )

    def _get_key_list(self, list_content_response: List[S3Content]) -> List[str]:
        return list(map(lambda x: x.get("Key"), list_content_response))

    def test_upload_wrong_bucket(self):
        file_id = str(uuid.uuid4())

        self.assertFalse(self._client.upload_file(TEST_PICTURE, TEST_BUCKET+"-xxx", file_id))

    def test_record_delete_list(self):
        file_id = str(uuid.uuid4())

        self.assertTrue(self._client.upload_file(TEST_PICTURE, TEST_BUCKET, file_id))

        list_object_response = self._client.list_objects(TEST_BUCKET, file_id)
        key_list = self._get_key_list(list_object_response)

        self.assertIn(file_id, key_list)

        self._client.delete_object(TEST_BUCKET, file_id)

        list_object_response = self._client.list_objects(TEST_BUCKET, file_id)
        key_list = self._get_key_list(list_object_response)

        self.assertNotIn(file_id, key_list)


