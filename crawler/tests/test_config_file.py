import os
import unittest
from pathlib import Path
from uuid import uuid4

from app.tools.config_file import ConfigFileException, ConfigFileManager


class TestConfigFileManager(unittest.TestCase):
    def setUp(self):
        self._test_config_manager = ConfigFileManager(
            force_config_path=Path("tests/files/fake_config.ini")
        )

        self._test_config_manager_no_sharding = ConfigFileManager(
            force_config_path=Path("tests/files/fake_config_no_sharding.ini")
        )

        self._temporary_path = Path(f"tests/files/{uuid4()}_config.ini")
        self._new_config_manager = ConfigFileManager(
            force_config_path=self._temporary_path
        )

        return super().setUp()

    def tearDown(self):
        if self._temporary_path.is_file():
            os.remove(self._temporary_path)

        return super().tearDown()

    def test_get_backup_folder_path_from_config(self):
        backup_folder_path = self._test_config_manager.get_backup_folder_path()

        self.assertEqual(
            Path("/home/john/Images/Photos/"),
            backup_folder_path,
        )

    def test_get_sharded_backup_folder_path_from_config(self):
        sharded_folder_path = self._test_config_manager.get_sharded_backup_folder_path()

        self.assertEqual(
            {
                2007: Path("/home/john/Images/Photos-sharded-2007/"),
            },
            sharded_folder_path,
        )

    def test_get_not_sharded_backup_folder_path_from_config(self):
        sharded_folder_path = (
            self._test_config_manager_no_sharding.get_sharded_backup_folder_path()
        )

        self.assertEqual(
            {},
            sharded_folder_path,
        )

    def test_config_file_does_not_exist(self):
        test_config_manager_no_file = ConfigFileManager(
            force_config_path=Path("tests/files/non_existent_config.ini")
        )

        with self.assertRaises(KeyError):
            test_config_manager_no_file.get_backup_folder_path()

    def test_set_backup_folder_path(self):
        self._new_config_manager.set_backup_folder_path(
            backup_folder_path=Path("/new/backup/path/")
        )

        with self.assertRaises(ConfigFileException):
            self._new_config_manager.set_backup_folder_path(
                backup_folder_path=Path("/another/backup/path-2/")
            )

        self._new_config_manager.set_backup_folder_path(
            backup_folder_path=Path("/another/backup/path-3/"),
            force=True,
        )

        test_config_manager = ConfigFileManager(force_config_path=self._temporary_path)

        self.assertEqual(
            Path("/another/backup/path-3/"),
            test_config_manager.get_backup_folder_path(),
        )
