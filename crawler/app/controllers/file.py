import logging
from typing import List, Iterator, Dict
from pathlib import Path

from app.models.file import LocalFile


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

    def _get_file_list(self) -> Iterator[LocalFile]:
        unique_path_list = set()

        for pattern in self._pattern_match_list:
            for _path in self._directory_list:
                for path in _path.glob(pattern):
                    if path not in unique_path_list:
                        unique_path_list.add(path)
                        yield LocalFile.from_path(path=path)

    def get_file_list(self) -> list[LocalFile]:
        file_list = list(self._get_file_list())
        self.logger.info(f"Found a total of {len(file_list)} picture files to process")

        return file_list

    @classmethod
    def get_relevant_files(
        cls, file_list: list[LocalFile], crawl_history: Dict[Path, LocalFile]
    ) -> Iterator[LocalFile]:
        for file in file_list:
            if file.path in crawl_history.keys():
                if file.last_modified > crawl_history[file.path].last_modified:
                    yield file
            else:
                yield file
