import platform
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from app.controllers.file import FileCrawler
from app.models.file import LocalFile


class TestFileCrawler(unittest.TestCase):
    @unittest.skipIf(
        platform.system() != "Linux", "Not relevant as Windows is not Case Sensitive"
    )
    def test_get_file_list(self):
        file_crawler = FileCrawler(
            directory_list=["tests/files/crawl"],
            pattern_match_list=["**/*.JPG"],
        )

        actual_list = list(
            [local_file.path for local_file in file_crawler.get_file_list()]
        )

        self.assertEqual(
            [Path("tests/files/crawl/sub-directory/small-2.JPG")],
            actual_list,
        )

    def test_get_file_list_2_extensions(self):
        file_crawler = FileCrawler(
            directory_list=["tests/files/crawl"],
            pattern_match_list=["**/*.JPG", "**/*.jpg"],
        )

        actual_list = [local_file.path for local_file in file_crawler.get_file_list()]

        self.assertEqual(
            set(
                [
                    Path("tests/files/crawl/sub-directory/small-2.JPG"),
                    Path("tests/files/crawl/small-1.jpg"),
                    Path("tests/files/crawl/sub-directory/small-3.jpg"),
                ]
            ),
            set(actual_list),
        )

    def test_get_relevant_file_modified_since_crawl(self):
        TIME = datetime(1980, 11, 30)

        file_list = [LocalFile(Path("/path_1"), TIME + timedelta(days=1))]

        crawl_history = {Path("/path_1"): LocalFile(Path("/path_1"), TIME)}

        self.assertEqual(
            file_list, list(FileCrawler.get_relevant_files(file_list, crawl_history))
        )

    def test_get_relevant_file_not_modified_since_crawl(self):
        TIME = datetime(1980, 11, 30)

        file_list = [LocalFile(Path("/path_1"), TIME)]

        crawl_history = {Path("/path_1"): LocalFile(Path("/path_1"), TIME)}

        self.assertEqual(
            [], list(FileCrawler.get_relevant_files(file_list, crawl_history))
        )

    def test_get_relevant_file_unkown_file(self):
        TIME = datetime(1980, 11, 30)

        file_list = [LocalFile(Path("/path_1"), TIME)]

        crawl_history = {Path("/path_2"): LocalFile(Path("/path_1"), TIME)}

        self.assertEqual(
            file_list, list(FileCrawler.get_relevant_files(file_list, crawl_history))
        )
