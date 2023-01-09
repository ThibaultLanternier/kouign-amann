import logging
from typing import List, Iterator
from pathlib import Path


class FileCrawler:
    def __init__(
        self,
        directory_list: List[str],
        pattern_match_list: List[str] = ["**/*.jpg", "**/*.JPG"],
    ):
        self._pattern_match_list = pattern_match_list
        self._directory_list = [Path(x) for x in directory_list]

        self.logger = logging.getLogger("app.file")
        directory_list_str = " ".join(directory_list)
        self.logger.info(
            f"Creating FileCrawler with following directories : {directory_list_str}"
        )

    def get_file_list(self) -> Iterator[Path]:
        unique_path_list = set()

        for pattern in self._pattern_match_list:
            for _path in self._directory_list:
                for path in _path.glob(pattern):
                    if path not in unique_path_list:
                        unique_path_list.add(path)
                        yield path
