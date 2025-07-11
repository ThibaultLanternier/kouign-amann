import unittest
import uuid
from datetime import datetime
from pathlib import Path

from app.entities.picture_data import PictureData
from app.factories.picture_data import PictureDataFactory
from app.services.backup import LocalFileBackupService
from app.tools.file import FileTools


class TestLocalFileBackupService(unittest.TestCase):
    def test_backup(self):
        file_service = LocalFileBackupService(
            backup_folder_path=Path("tests/files/local_recorder"),
            picture_data_factory=PictureDataFactory(),
            file_tools=FileTools(),
        )

        picture_path = Path("tests/files/test-canon-eos70D.jpg")

        picture_data = PictureData(
            hash=uuid.uuid4().hex,
            path=picture_path,
            creation_date=datetime(2024, 11, 30, 11, 45),
        )

        self.assertTrue(
            file_service.backup(picture_path, picture_data),
            "First recording should work",
        )
        # It should return False if the file already exists
        self.assertFalse(
            file_service.backup(picture_path, picture_data),
            "Second recording should not work",
        )

        folder = Path("tests/files/local_recorder/2024/NOT_GROUPED")
        timestamp = int(picture_data.get_creation_date().timestamp())

        file_name = Path(f"{timestamp}-{picture_data.get_hash()}.jpg")
        expected_backup_path = folder / file_name

        with open(expected_backup_path, "rb") as f:
            self.assertEqual(f.read(), picture_path.read_bytes())

    def test_hash_exists(self):
        file_service = LocalFileBackupService(
            backup_folder_path=Path("tests/files/local_recorder_2"),
            picture_data_factory=PictureDataFactory(),
            file_tools=FileTools(),
        )

        test_hash = "2eacfe02c923466cb98163c0b65c739e"

        self.assertTrue(file_service.hash_exists(test_hash))
        self.assertFalse(file_service.hash_exists("XXXXX"))
