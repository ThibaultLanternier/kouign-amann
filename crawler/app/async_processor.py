import asyncio
import logging
from asyncio import Semaphore
from datetime import datetime
from pathlib import Path
from typing import Any, List, Type

from progressbar import ProgressBar

from app.controllers.async_history_store import iAsyncCrawlHistoryStore
from app.controllers.async_recorder import iAsyncRecorder
from app.controllers.exif import (ExifException, ExifImageImpossibleToOpen,
                                  ExifManager)
from app.controllers.hashing import Hasher, HasherException
from app.controllers.recorder import RecorderException
from app.controllers.thumbnail import ThumbnailImage
from app.models.picture import PictureFile, PictureInfo


class AsyncPictureProcessor:
    def __init__(
        self,
        picture_path_list: List[Path],
        async_recorder: iAsyncRecorder,
        file_history_recorder: iAsyncCrawlHistoryStore,
        crawler_id: str,
        crawl_time: datetime,
    ) -> None:
        self._picture_path_list = picture_path_list
        self._async_recorder = async_recorder
        self._file_history_recorder = file_history_recorder
        self._crawl_time = crawl_time
        self._crawler_id = crawler_id

        self._logger = logging.getLogger("app.crawlasync")
        self._logger.info(f"Received {len(picture_path_list)} unprocessed pictures")
        self._init_progress_bar()

    def _init_progress_bar(self) -> None:
        self._progress_bar = ProgressBar()
        self._progress_counter = 0

    def _update_progress_bar(self) -> None:
        self._progress_counter = self._progress_counter + 1
        self._progress_bar.update(self._progress_counter)

    async def _process(self, path: Path) -> Path:
        try:
            exif_manager = ExifManager(path=path)

            hash = await Hasher(exif_manager.get_image()).hash()
            creation_time = await exif_manager.get_creation_time()

            already_exists = await self._async_recorder.check_picture_exists(
                hash=hash
            )

            if not already_exists:
                await self._async_recorder.record_file(
                    picture_path=path, 
                    hash=hash, 
                    creation_time=creation_time
                )

        except ExifImageImpossibleToOpen:
            self._update_progress_bar()
            await self._file_history_recorder.add_file(path)
            return path
        except HasherException:
            self._logger.warning(f"Hashing failed for {path} file is propably corrupted")
            self._update_progress_bar()
            return path
        except ExifException as e:
            self._logger.warning(f"Exif processing error {type(e)} for file {path}")
            self._update_progress_bar()
            return ExifException

        except Exception as e:
            self._update_progress_bar()
            raise e

        self._update_progress_bar()

        await self._file_history_recorder.add_file(path)
        return path

    def _count_exception(self, result_list: List[Any], exception: Type) -> int:
        filtered_list = [value for value in result_list if isinstance(value, exception)]
        return len(filtered_list)

    async def process(self) -> None:
        self._progress_bar.start(max_value=len(self._picture_path_list))

        result: list[Path] = []

        for path in self._picture_path_list:
            result.append(await self._process(path=path))

        success = [value for value in result if isinstance(value, Path)]
        exif_exception_count = self._count_exception(result, ExifException)
        record_exception_count = self._count_exception(result, RecorderException)
        hashing_exception_count = self._count_exception(result, HasherException)

        self._logger.info(f"Added {len(success)} new files successfully")
        self._logger.info(f"Exif processing failed on {exif_exception_count} files")
        self._logger.info(f"File recording failed on {record_exception_count} files")
        self._logger.info(f"Hashing failed on {hashing_exception_count} files")

        total = len(success) + exif_exception_count + record_exception_count

        self._logger.info(f"TOTAL files processed : {total}")
