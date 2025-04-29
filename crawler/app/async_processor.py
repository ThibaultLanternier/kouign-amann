import logging
from pathlib import Path
from typing import List

from progressbar import ProgressBar

from app.controllers.async_history_store import iAsyncCrawlHistoryStore
from app.controllers.async_recorder import iAsyncRecorder
from app.controllers.exif import (ExifException, ExifImageImpossibleToOpen,
                                  ExifManager)
from app.controllers.hashing import Hasher, HasherException


class AsyncPictureProcessor:
    def __init__(
        self,
        picture_path_list: List[Path],
        async_recorder: iAsyncRecorder,
        file_history_recorder: iAsyncCrawlHistoryStore,
        filter_year: int = 0,
    ) -> None:
        self._picture_path_list = picture_path_list
        self._async_recorder = async_recorder
        self._file_history_recorder = file_history_recorder
        self._filter_year = filter_year

        self._logger = logging.getLogger("app.crawlasync")
        self._logger.info(f"Received {len(picture_path_list)} unprocessed pictures")

        if self._filter_year != 0:
            self._logger.warning(
                f"Pictures from year {self._filter_year} other files will be ignored"
            )

        self._init_progress_bar()

    def _init_progress_bar(self) -> None:
        self._progress_bar = ProgressBar()
        self._progress_counter = 0

    def _update_progress_bar(self) -> None:
        self._progress_counter = self._progress_counter + 1
        self._progress_bar.update(self._progress_counter)

    async def _process(self, path: Path, filter_year: int) -> Path:
        try:
            exif_manager = ExifManager(path=path)

            creation_time = await exif_manager.get_creation_time()

            if filter_year != 0 and creation_time.year != filter_year:
                self._update_progress_bar()
                return path

            hash = await Hasher(exif_manager.get_image()).hash()

            already_exists = await self._async_recorder.check_picture_exists(hash=hash)

            if not already_exists:
                await self._async_recorder.record_file(
                    picture_path=path, hash=hash, creation_time=creation_time
                )

        except ExifImageImpossibleToOpen:
            self._update_progress_bar()
            await self._file_history_recorder.add_file(path)
            return path
        except HasherException:
            self._logger.warning(
                f"Hashing failed for {path} file is propably corrupted"
            )
            self._update_progress_bar()
            return path
        except ExifException as e:
            self._logger.warning(f"Exif processing error {type(e)} for file {path}")
            self._update_progress_bar()
            return path

        except Exception as e:
            self._update_progress_bar()
            raise e

        self._update_progress_bar()

        await self._file_history_recorder.add_file(path)
        return path

    async def process(self) -> None:
        self._progress_bar.start(max_value=len(self._picture_path_list))

        result: list[Path] = []

        for path in self._picture_path_list:
            result.append(await self._process(path=path, filter_year=self._filter_year))

        success = [value for value in result if isinstance(value, Path)]

        self._logger.info(f"Added {len(success)} new files successfully")
