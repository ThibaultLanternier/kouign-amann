from datetime import timezone
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from isort import file

from app.entities.picture_data import iPictureData
from app.services.backup import iBackupService, iFileTools
from app.services.picture_data_caching import (PictureIdComputeException,
                                     iPictureDataCachingService)
from app.use_cases.backup import BackupUseCase, backup_use_case_factory
from app.entities.picture import HasherException
from app.factories.picture_data import iPictureDataFactory

PICTURE_PATH = Path("path1")
PICTURE_DATA = MagicMock(name="fake_picture_data", spec=iPictureData)
PICTURE_DATA_2 = MagicMock(name="fake_picture_data_2", spec=iPictureData)

class TestBackupUseCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self._mock_file_service = MagicMock(name="mock_file_service", spec=iBackupService)
        self._mock_picture_id_service = MagicMock(
            name="mock_picture_id_service", spec=iPictureDataCachingService
        )
        self._mock_picture_data_factory = MagicMock(name="mock_picture_data_factory", spec=iPictureDataFactory)

        self._mock_file_tools = MagicMock(name="mock_file_tools", spec=iFileTools)

        self._mock_file_service.backup.return_value = True

        self._backup_use_case = BackupUseCase(
            backup_service=self._mock_file_service,
            file_tools=self._mock_file_tools,
            picture_data_caching_service=self._mock_picture_id_service,
            picture_data_factory=self._mock_picture_data_factory,
        )
    
    def test_list_pictures_ok(self):
        self._mock_file_tools.list_pictures.return_value = [PICTURE_PATH]

        result = self._backup_use_case.list_pictures(root_path=Path("test"))

        self.assertEqual([PICTURE_PATH], result)
        self._mock_file_tools.list_pictures.assert_called_once_with(root_path=Path("test"))

    def test_backup_strict_mode_OK(self):
        self._mock_picture_id_service.get_from_cache.return_value = PICTURE_DATA_2
        self._mock_picture_data_factory.compute_data.return_value = PICTURE_DATA

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
        self._mock_picture_data_factory.compute_data.return_value = PICTURE_DATA

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
        self._mock_picture_data_factory.compute_data.assert_not_called()
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

        def raise_hasher_exception(path: Path, current_timezone: timezone) -> iPictureData:
            raise HasherException("xxxx")

        self._mock_picture_data_factory.compute_data.side_effect = (
            raise_hasher_exception
        )

        result = self._backup_use_case.backup(
            picture_list_to_backup=[PICTURE_PATH], strict_mode=False
        )

        self.assertEqual(0, result)

class TestBackupUseCaseFactory(unittest.TestCase):
    def test_factory_ok(self):
        instance = backup_use_case_factory(backup_folder_path=Path("test"))
        self.assertIsInstance(instance, BackupUseCase)