import unittest
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from app.entities.picture_data import PictureData
from app.entities.picture_heap import HeapType, PictureHeap, iPictureHeap
from app.factories.picture_data import PictureDataFactory
from app.services.backup import LocalFileBackupService
from app.tools.file import FileTools, iFileTools


class TestLocalFileBackupService(unittest.TestCase):
    def test_backup(self):
        file_service = LocalFileBackupService(
            backup_folder_path=Path("tests/files/local_recorder"),
            sharded_folder_path={},
            picture_data_factory=PictureDataFactory(),
            file_tools=FileTools(),
        )

        picture_path = Path("tests/files/test-canon-eos70D.jpg")

        picture_data = PictureData(
            hash=uuid.uuid4().hex,
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

    def test_backup_with_year_sharding(self):
        file_service = LocalFileBackupService(
            backup_folder_path=Path("tests/files/local_recorder"),
            sharded_folder_path={2024: Path("tests/files/local_recorder_sharded")},
            picture_data_factory=PictureDataFactory(),
            file_tools=FileTools(),
        )

        picture_path = Path("tests/files/test-canon-eos70D.jpg")

        picture_data = PictureData(
            hash=uuid.uuid4().hex,
            creation_date=datetime(2024, 11, 30, 11, 45),
        )

        self.assertTrue(
            file_service.backup(picture_path, picture_data),
            "First recording should work",
        )

        sharded_folder = Path("tests/files/local_recorder_sharded/2024/NOT_GROUPED")
        timestamp = int(picture_data.get_creation_date().timestamp())

        file_name = Path(f"{timestamp}-{picture_data.get_hash()}.jpg")
        expected_backup_path = sharded_folder / file_name

        with open(expected_backup_path, "rb") as f:
            self.assertEqual(f.read(), picture_path.read_bytes())

    def test_hash_exists(self):
        file_service = LocalFileBackupService(
            backup_folder_path=Path("tests/files/local_recorder_2"),
            sharded_folder_path={},
            picture_data_factory=PictureDataFactory(),
            file_tools=FileTools(),
        )

        test_hash = "2eacfe02c923466cb98163c0b65c739e"

        self.assertTrue(file_service.hash_exists(test_hash))
        self.assertFalse(file_service.hash_exists("XXXXX"))

    def test_find_by_hash(self):
        file_service = LocalFileBackupService(
            backup_folder_path=Path("tests/files/local_recorder_2"),
            sharded_folder_path={},
            picture_data_factory=PictureDataFactory(),
            file_tools=FileTools(),
        )

        test_hash = "3eacfe02c923466cb98163c0b65c739e"

        self.assertEqual(
            file_service.find_by_hash(test_hash),
            Path(
                "tests/files/local_recorder_2/2024/NOT_GROUPED/1732963500-3eacfe02c923466cb98163c0b65c739e.jpg"  # noqa: E501
            ),
        )
        self.assertIsNone(file_service.find_by_hash("XXXXX"))

    def test_list_backed_up_pictures(self):
        backup_service = LocalFileBackupService(
            backup_folder_path=Path("tests/files/local_recorder_2"),
            sharded_folder_path={},
            picture_data_factory=PictureDataFactory(),
            file_tools=FileTools(),
        )

        picture_heap_list: list[iPictureHeap] = backup_service.list_backed_up_pictures()

        self.assertEqual(
            set([picture_heap.get_type() for picture_heap in picture_heap_list]),
            set([HeapType.OTHER, HeapType.GROUPED, HeapType.NOT_GROUPED]),
        )

    def test_update_picture_heaps(self):
        mock_file_tools = MagicMock(spec=iFileTools)

        origin_path = Path("BACKUP/2024/NOT_GROUPED/1732963500-5eacfe02.jpg")

        mock_file_tools.list_pictures.return_value = [
            Path("BACKUP/2024/NOT_GROUPED/1732963500-5eacfe02.jpg")
        ]

        backup_service = LocalFileBackupService(
            backup_folder_path=Path("FAKE"),
            sharded_folder_path={},
            picture_data_factory=PictureDataFactory(),
            file_tools=mock_file_tools,
        )

        picture_data = PictureData(
            creation_date=datetime(1980, 11, 30, 12),
            hash="5eacfe02",
            group_break=True,
            is_selected=True,
        )

        picture_heap = PictureHeap(
            heap_type=HeapType.GROUPED,
            picture_list=[picture_data],
            description="ANNIVERSAIRE THIBAULT",
        )

        backup_service.update_picture_heaps(picture_heap_list=[picture_heap])

        mock_file_tools.move_file.assert_called_once_with(
            origin_path,
            Path(
                "FAKE/1980/1980-11-30 ANNIVERSAIRE THIBAULT/0-344430000-5eacfe02-x.jpg"
            ),
        )
