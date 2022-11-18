import logging
from typing import List, Iterator
from pathlib import Path


class FileCrawler:
    def __init__(
        self, start_path: str, pattern_match_list: List[str] = ["**/*.jpg", "**/*.JPG"]
    ):
        self._pattern_match_list = pattern_match_list
        self._path = Path(start_path)

        self.logger = logging.getLogger("app.file")
        self.logger.info(f"Creating FileCrawler with start path {self._path}")

    def get_file_list(self) -> Iterator[Path]:
        unique_path_list = set()

        for pattern in self._pattern_match_list:
            for path in self._path.glob(pattern):
                if path not in unique_path_list:
                    unique_path_list.add(path)
                    yield path
