import unittest
from datetime import timezone
from pathlib import Path
from unittest.mock import MagicMock

from app.factories.picture_data import iPictureDataFactory
from app.services.backup import iBackupService
from app.use_cases.check import CheckUseCase, check_use_case_factory


class TestCheckUseCase(unittest.TestCase):
    def setUp(self):
        self.mock_picture_data_factory = MagicMock(spec=iPictureDataFactory)

        def mock_compute_data(path, current_timezone=timezone.utc):
            if path == Path("a.jpg"):
                return MagicMock(get_hash=lambda: "hash1")
            else:
                return MagicMock(get_hash=lambda: "hash3")

        self.mock_picture_data_factory.compute_data.side_effect = mock_compute_data

        self._mock_backup_service = MagicMock(spec=iBackupService)

        def mock_hash_exists(picture_hash):
            return picture_hash == "hash1"

        self._mock_backup_service.hash_exists.side_effect = mock_hash_exists

        self.use_case = CheckUseCase(
            backup_service=self._mock_backup_service,
            picture_data_factory=self.mock_picture_data_factory,
        )

    def test_check_pictures_1_picture_not_backuped_up(self):
        picture_list = [Path("a.jpg"), Path("b.jpg")]

        self.assertEqual(
            1, self.use_case.check_pictures(picture_list_to_check=picture_list)
        )

    def test_check_pictures_all_pictures_backuped_up(self):
        picture_list = [Path("a.jpg")]

        self.assertEqual(
            0, self.use_case.check_pictures(picture_list_to_check=picture_list)
        )

    def test_check_use_case_factory(self):
        use_case = check_use_case_factory(backup_service=self._mock_backup_service)

        self.assertIsInstance(use_case, CheckUseCase)
