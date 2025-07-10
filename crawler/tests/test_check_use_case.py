import unittest
from datetime import timezone
from pathlib import Path
from unittest.mock import MagicMock

from app.factories.picture_data import iPictureDataFactory
from app.use_cases.check import CheckUseCase


class TestCheckUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_file_tools = MagicMock()
        self.mock_picture_data_factory = MagicMock(spec=iPictureDataFactory)

        def mock_from_standard_path(path, current_timezone=timezone.utc):
            if path == Path("backup_a.jpg"):
                return MagicMock(get_hash=lambda: "hash1")
            else:
                return MagicMock(get_hash=lambda: "hash2")

        self.mock_picture_data_factory.from_standard_path.side_effect = (
            mock_from_standard_path
        )

        def mock_compute_data(path, current_timezone=timezone.utc):
            if path == Path("a.jpg"):
                return MagicMock(get_hash=lambda: "hash1")
            else:
                return MagicMock(get_hash=lambda: "hash3")

        self.mock_picture_data_factory.compute_data.side_effect = mock_compute_data

        self.use_case = CheckUseCase(
            file_tools=self.mock_file_tools,
            picture_data_factory=self.mock_picture_data_factory,
        )

    def test_check_pictures_1_picture_not_backuped_up(self):
        backup_list = [Path("backup_a.jpg")]
        picture_list = [Path("a.jpg"), Path("b.jpg")]

        self.assertEqual(1, self.use_case.check_pictures(backup_list, picture_list))

    def test_check_pictures_all_pictures_backuped_up(self):
        backup_list = [Path("backup_a.jpg")]
        picture_list = [Path("a.jpg")]

        self.assertEqual(0, self.use_case.check_pictures(backup_list, picture_list))
