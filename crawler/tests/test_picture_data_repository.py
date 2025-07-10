import unittest
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.entities.picture_data import PictureData
from app.repositories.picture_data import PictureDataRepository


class TestPictureDataRepository(unittest.TestCase):
    def test_get_parents_folder_list(self):
        file_path = Path(f"tests/files/repository/repo_{uuid4().hex}.jsonl")
        repository = PictureDataRepository(cache_file_path=file_path)

        # Create picture data in different folders
        folder1 = "tests/files/repository/folder1"
        folder2 = "tests/files/repository/folder2"

        picture_data1 = PictureData(
            path=Path(f"{folder1}/test1.jpg"),
            creation_date=datetime(2023, 10, 1, 12, 0, 0),
            hash="same-hash",
        )

        picture_data2 = PictureData(
            path=Path(f"{folder1}/test2.jpg"),
            creation_date=datetime(2023, 10, 2, 12, 0, 0),
            hash="same-hash",
        )

        picture_data3 = PictureData(
            path=Path(f"{folder2}/test3.jpg"),
            creation_date=datetime(2023, 10, 3, 12, 0, 0),
            hash="same-hash",
        )

        # Record the picture data
        repository.record(data=picture_data1)
        repository.record(data=picture_data2)
        repository.record(data=picture_data3)

        # Get parent folder list
        folders = repository.get_parents_folder_list(picture_hash="same-hash")

        # Verify folders
        self.assertEqual(set(folders), set(["folder1", "folder2"]))

    def test_get_record(self):
        file_path = Path(f"tests/files/repository/repo_{uuid4().hex}.jsonl")

        repository = PictureDataRepository(cache_file_path=file_path)

        picture_data = PictureData(
            path=Path("tests/files/repository/test.jpg"),
            creation_date=datetime(2023, 10, 1, 12, 0, 0),
            hash="1234567890abcdef",
        )

        self.assertIsNone(repository.get(picture_data.get_path()))

        repository.record(data=picture_data)

        self.assertEqual(repository.get(picture_data.get_path()), picture_data)

        new_repository = PictureDataRepository(cache_file_path=file_path)

        self.assertEqual(
            new_repository.get(picture_data.get_path()).get_hash(),
            picture_data.get_hash(),
        )
