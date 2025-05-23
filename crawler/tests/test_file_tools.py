from pathlib import Path
import unittest

from app.tools.file import FileTools


class TestFileTools(unittest.TestCase):
    def test_get_file_case_sensitive_jpg(self):
        file_list = FileTools().list_pictures(Path("tests/files/crawl"))

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

