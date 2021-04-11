import logging
import os
from typing import List


class FileCrawler:
    def __init__(
        self,
        start_path: str,
        extension_list: List[str] = ["jpg", "JPG"],
        use_absolute_path=True,
    ):
        self.extension_list = extension_list

        self.logger = logging.getLogger("app.file")

        if use_absolute_path:
            self.start_path = os.path.join(os.getcwd(), start_path)
        else:
            self.start_path = start_path

        self.logger.info(f"Creating FileCrawler with start path {self.start_path}")

    def __is_extension_ok(self, filename: str):
        extension = filename.split(".")

        if len(extension) != 2:
            return False
        else:
            return extension[1] in self.extension_list

    def __empty_logger(self, message):
        pass

    def get_file_list(self):
        for dirpath, dirnames, filenames in os.walk(self.start_path):
            for filename in filenames:
                if self.__is_extension_ok(filename):
                    output = os.path.join(dirpath, filename)
                    self.logger.debug(f"Found file : {output}")

                    yield output
