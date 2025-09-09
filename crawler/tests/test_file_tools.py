import unittest
from pathlib import Path

from app.tools.file import FileTools


class TestFileTools(unittest.TestCase):
    def test_get_file_case_sensitive_jpg(self):
        file_list = FileTools().list_pictures(
            root_path_list=[Path("tests/files/crawl")],
            folder_name_to_exclude=[],
        )

        self.assertEqual(
            set(
                [
                    Path("tests/files/crawl/sub-directory/small-2.JPG"),
                    Path("tests/files/crawl/small-1.jpg"),
                    Path("tests/files/crawl/sub-directory/small-3.jpg"),
                    Path(
                        "tests/files/crawl/sub-directory/OtherStrangeFolder/small-3.jpg"
                    ),
                    Path("tests/files/crawl/sub-directory/.AppleDouble/small-3.jpg"),
                ]
            ),
            set(file_list),
        )

    def test_get_file_case_sensitive_jpg_exclude_folder(self):
        file_list = FileTools().list_pictures(
            root_path_list=[Path("tests/files/crawl")],
            folder_name_to_exclude=[".AppleDouble", "OtherStrangeFolder"],
        )

        self.assertEqual(
            set(
                [
                    Path("tests/files/crawl/sub-directory/small-2.JPG"),
                    Path("tests/files/crawl/small-1.jpg"),
                    Path("tests/files/crawl/sub-directory/small-3.jpg"),
                ]
            ),
            set(file_list),
        )
