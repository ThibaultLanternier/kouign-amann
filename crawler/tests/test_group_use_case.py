import unittest
from datetime import timezone
from pathlib import Path
from unittest.mock import MagicMock

from app.entities import picture
from app.entities.picture_data import iPictureData
from app.entities.picture_group import iPictureGroup
from app.factories.picture_data import (NotStandardFileNameException,
                                        iPictureDataFactory)
from app.services.backup import iBackupService, iFileTools
from app.services.group_creator import iGroupCreatorService
from app.use_cases.group import GroupUseCase, group_use_case_factory

PICTURE_PATH = Path("path1")
PICTURE_PATH_2 = Path("path2")

PICTURE_DATA = MagicMock(name="fake_picture_data", spec=iPictureData)
PICTURE_GROUP = MagicMock(name="fake_picture_group", spec=iPictureGroup)


class TestGroupUseCase(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self._mock_file_service = MagicMock(
            name="mock_file_service", spec=iBackupService
        )
        self._mock_group_creator_svc = MagicMock(
            name="mock_group_creator_service", spec=iGroupCreatorService
        )
        self._mock_picture_data_factory = MagicMock(
            name="mock_picture_data_factory", spec=iPictureDataFactory
        )
        self._mock_file_tools = MagicMock(name="mock_file_tools", spec=iFileTools)

        self._group_use_case = GroupUseCase(
            file_tools=self._mock_file_tools,
            picture_data_factory=self._mock_picture_data_factory,
            group_creator_service=self._mock_group_creator_svc,
        )

    def test_group_get_data_from_path_ok(self):
        self._mock_picture_data_factory.from_standard_path.return_value = PICTURE_DATA

        PICTURE_GROUP.list_pictures_to_move.return_value = [
            (PICTURE_PATH, PICTURE_PATH_2)
        ]
        self._mock_group_creator_svc.get_group_list_from_time.return_value = [
            PICTURE_GROUP
        ]

        self._group_use_case.group(picture_list=[PICTURE_PATH])

        self._mock_picture_data_factory.from_standard_path.assert_called_once_with(
            path=PICTURE_PATH, current_timezone=timezone.utc
        )

        self._mock_group_creator_svc.get_group_list_from_time.assert_called_once_with(
            picture_list=[PICTURE_DATA]
        )

        self._mock_file_tools.move_file.assert_called_once_with(
            origin_path=PICTURE_PATH, target_path=PICTURE_PATH_2
        )

    def test_group_cannot_get_data_from_path_ok(self):
        def raise_not_standard_file_name_exception(*args, **kwargs):
            raise NotStandardFileNameException("Not standard file name")

        self._mock_picture_data_factory.from_standard_path.side_effect = (
            raise_not_standard_file_name_exception
        )
        self._mock_picture_data_factory.compute_data.return_value = PICTURE_DATA

        PICTURE_GROUP.list_pictures_to_move.return_value = [
            (PICTURE_PATH, PICTURE_PATH_2)
        ]
        self._mock_group_creator_svc.get_group_list_from_time.return_value = [
            PICTURE_GROUP
        ]

        self._group_use_case.group(picture_list=[PICTURE_PATH])

        self._mock_group_creator_svc.get_group_list_from_time.assert_called_once_with(
            picture_list=[PICTURE_DATA]
        )

        self._mock_file_tools.move_file.assert_called_once_with(
            origin_path=PICTURE_PATH, target_path=PICTURE_PATH_2
        )

    def test_group_cannot_get_data_from_path_and_cannot_compute_nothing_happens(self):
        def raise_not_standard_file_name_exception(*args, **kwargs):
            raise NotStandardFileNameException("Not standard file name")

        self._mock_picture_data_factory.from_standard_path.side_effect = (
            raise_not_standard_file_name_exception
        )

        def raise_picture_exception(*args, **kwargs):
            raise picture.PictureException("Cannot compute picture data")

        self._mock_picture_data_factory.compute_data.side_effect = (
            raise_picture_exception
        )

        PICTURE_GROUP.list_pictures_to_move.return_value = [
            (PICTURE_PATH, PICTURE_PATH_2)
        ]

        self._mock_group_creator_svc.get_group_list_from_time.return_value = []

        self._group_use_case.group(picture_list=[PICTURE_PATH])

        self._mock_group_creator_svc.get_group_list_from_time.assert_called_once_with(
            picture_list=[]
        )

        self._mock_file_tools.move_file.assert_not_called()


class TestGroupUseCaseFactory(unittest.TestCase):
    def test_factory_ok(self):
        instance = group_use_case_factory(hours_btw_pictures=24)

        self.assertIsInstance(instance, GroupUseCase)
