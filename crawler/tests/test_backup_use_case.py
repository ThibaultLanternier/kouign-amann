import unittest
from pathlib import Path
from unittest.mock import MagicMock

from app.entities.picture_data import iPictureData
from app.services.file import iFileService
from app.services.picture_id import (PictureIdComputeException,
                                     iPictureIdService)
from app.use_cases.backup import BackupUseCase

PICTURE_PATH = Path("path1")
PICTURE_DATA = MagicMock(name="fake_picture_data", spec=iPictureData)
PICTURE_DATA_2 = MagicMock(name="fake_picture_data_2", spec=iPictureData)


class TestBackupUseCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self._mock_file_service = MagicMock(name="mock_file_service", spec=iFileService)
        self._mock_picture_id_service = MagicMock(
            name="mock_picture_id_service", spec=iPictureIdService
        )

        self._mock_file_service.backup.return_value = True

        self._backup_use_case = BackupUseCase(
            file_service=self._mock_file_service,
            picture_id_service=self._mock_picture_id_service,
        )

    def test_backup_strict_mode_OK(self):
        self._mock_picture_id_service.get_from_cache.return_value = PICTURE_DATA_2
        self._mock_picture_id_service.compute_id.return_value = PICTURE_DATA

        result = self._backup_use_case.backup(
            picture_list_to_backup=[PICTURE_PATH], strict_mode=True
        )

        self.assertEqual(1, result)

        # When strict mode is True, cache should not be used
        self._mock_picture_id_service.get_from_cache.assert_not_called()
        self._mock_file_service.backup.assert_called_once_with(
            origin_path=PICTURE_PATH, data=PICTURE_DATA
        )

    def test_backup_not_strict_file_not_cached_OK(self):
        self._mock_picture_id_service.get_from_cache.return_value = None
        self._mock_picture_id_service.compute_id.return_value = PICTURE_DATA

        result = self._backup_use_case.backup(
            picture_list_to_backup=[PICTURE_PATH], strict_mode=False
        )

        self.assertEqual(1, result)

        self._mock_picture_id_service.get_from_cache.assert_called_once_with(
            picture_path=PICTURE_PATH
        )
        self._mock_picture_id_service.add_to_cache.assert_called_once_with(
            data=PICTURE_DATA
        )

        self._mock_file_service.backup.assert_called_once_with(
            origin_path=PICTURE_PATH, data=PICTURE_DATA
        )

    def test_backup_not_strict_file_cached_OK(self):
        self._mock_picture_id_service.get_from_cache.return_value = PICTURE_DATA

        result = self._backup_use_case.backup(
            picture_list_to_backup=[PICTURE_PATH], strict_mode=False
        )

        self.assertEqual(1, result)

        self._mock_picture_id_service.get_from_cache.assert_called_once_with(
            picture_path=PICTURE_PATH
        )
        self._mock_picture_id_service.compute_id.assert_not_called()
        self._mock_picture_id_service.add_to_cache.assert_not_called()

        self._mock_file_service.backup.assert_called_once_with(
            origin_path=PICTURE_PATH, data=PICTURE_DATA
        )

    def test_backup_not_strict_file_cached_file_already_exists_OK(self):
        self._mock_picture_id_service.get_from_cache.return_value = PICTURE_DATA
        self._mock_file_service.backup.return_value = False

        result = self._backup_use_case.backup(
            picture_list_to_backup=[PICTURE_PATH], strict_mode=False
        )

        self.assertEqual(0, result)

    def test_backup_not_strict_file_impossible_to_compute_cached_OK(self):
        self._mock_picture_id_service.get_from_cache.return_value = None

        def raise_picture_id_compute_exception(picture_path: Path) -> iPictureData:
            raise PictureIdComputeException("test")

        self._mock_picture_id_service.compute_id.side_effect = (
            raise_picture_id_compute_exception
        )

        result = self._backup_use_case.backup(
            picture_list_to_backup=[PICTURE_PATH], strict_mode=False
        )

        self.assertEqual(0, result)
