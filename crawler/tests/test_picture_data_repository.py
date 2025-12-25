import unittest
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.repositories.picture_data import (JSONRecordedPictureDataRepository,
                                           RecordedPictureData)


class TestPictureDataRepository(unittest.TestCase):
    def test_get_record(self):
        file_path = Path(f"tests/files/repository/repo_{uuid4().hex}.jsonl")

        repository = JSONRecordedPictureDataRepository(cache_file_path=file_path)

        recorded_picture_data = RecordedPictureData(
            path=file_path,
            creation_date=datetime(2023, 10, 1, 12, 0, 0),
            hash="1234567890abcdef",
        )

        repository.record(data=recorded_picture_data)

        new_repository = JSONRecordedPictureDataRepository(cache_file_path=file_path)

        self.assertEqual(
            new_repository.get(path=recorded_picture_data.path).hash,
            recorded_picture_data.hash,
        )
