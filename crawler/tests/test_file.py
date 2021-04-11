import unittest

from app.controllers.file import FileCrawler


class TestFileCrawler(unittest.TestCase):
    def test_get_file_list(self):
        self.assertEqual(
            ["tests/files/crawl/sub-directory/small-2.JPG"],
            list(
                FileCrawler(
                    "tests/files/crawl", extension_list=["JPG"], use_absolute_path=False
                ).get_file_list()
            ),
        )

    def test_get_file_list_2_extensions(self):
        actual_list = list(
            FileCrawler(
                "tests/files/crawl",
                extension_list=["jpg", "JPG", "png"],
                use_absolute_path=False,
            ).get_file_list()
        )

        self.assertEqual(
            [
                "tests/files/crawl/small-1.jpg",
                "tests/files/crawl/sub-directory/small-3.jpg",
                "tests/files/crawl/sub-directory/small-2.JPG",
            ],
            actual_list,
        )
