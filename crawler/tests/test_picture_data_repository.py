from datetime import date, datetime
from math import pi
from pathlib import Path
import re
import unittest
from uuid import uuid4

from app.entities.picture_data import PictureData
from app.repositories.picture_data import PictureDataRepository


class TestPictureDataRepository(unittest.TestCase):
    def test_get_record(self):
        file_path = Path(f"tests/files/repository/repo_{uuid4().hex}.jsonl")

        repository = PictureDataRepository(cache_file_path=file_path)

        picture_data = PictureData(
            path=Path("tests/files/repository/test.jpg"),
            creation_date= datetime(2023, 10, 1, 12, 0, 0),
            hash="1234567890abcdef",
        )

        self.assertIsNone(repository.get(picture_data.get_path()))

        repository.record(data= picture_data)

        self.assertEqual(repository.get(picture_data.get_path()), picture_data)

        new_repository = PictureDataRepository(cache_file_path=file_path)

        self.assertEqual(new_repository.get(picture_data.get_path()).get_hash(), picture_data.get_hash())