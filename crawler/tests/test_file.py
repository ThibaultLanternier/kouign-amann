import unittest
import platform
from pathlib import Path

from app.controllers.file import FileCrawler


class TestFileCrawler(unittest.TestCase):
    @unittest.skipIf(platform.system() == "Windows", "Not relevant as Windows is not Case Sensitive")
    def test_get_file_list(self):
        self.assertEqual(
            [Path("tests/files/crawl/sub-directory/small-2.JPG")],
            list(
                FileCrawler(
                    start_path="tests/files/crawl",
                    pattern_match_list=["**/*.JPG"],
                ).get_file_list()
            ),
        )

    def test_get_file_list_2_extensions(self):
        actual_list = list(
            FileCrawler(
                start_path="tests/files/crawl",
                pattern_match_list=["**/*.JPG", "**/*.jpg"],
            ).get_file_list()
        )

        self.assertEqual(
            set([
                Path("tests/files/crawl/sub-directory/small-2.JPG"),
                Path("tests/files/crawl/small-1.jpg"),
                Path("tests/files/crawl/sub-directory/small-3.jpg"),
            ]),
            set(actual_list),
        )
