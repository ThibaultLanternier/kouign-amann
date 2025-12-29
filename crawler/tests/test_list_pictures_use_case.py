import unittest
from pathlib import Path
from unittest.mock import MagicMock

from app.tools.file import iFileTools
from app.use_cases.list_pictures import (ListPicturesUseCase,
                                         list_pictures_use_case_factory)


class TestListPicturesUseCase(unittest.TestCase):
    def setUp(self):
        self._mock_file_tools = MagicMock(spec=iFileTools)

        self._mock_file_tools.list_pictures.return_value = [
            Path("/path/to/picture1.jpg"),
            Path("/path/to/picture2.jpg"),
        ]

        return super().setUp()

    def test_list_pictures_use_case(self):
        use_case = ListPicturesUseCase(file_tools=self._mock_file_tools)

        result = use_case.list_pictures(
            root_path=Path("/some/root/path"),
            folder_name_to_exclude=["exclude_this_folder"],
        )

        self._mock_file_tools.list_pictures.assert_called_once_with(
            root_path_list=[Path("/some/root/path")],
            folder_name_to_exclude=["exclude_this_folder"],
        )

        expected_result = [
            Path("/path/to/picture1.jpg"),
            Path("/path/to/picture2.jpg"),
        ]

        self.assertEqual(expected_result, result)

    def test_list_pictures_use_case_factory(self):
        use_case = list_pictures_use_case_factory()

        self.assertIsInstance(use_case, ListPicturesUseCase)
