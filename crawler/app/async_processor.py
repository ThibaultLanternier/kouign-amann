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
        self._logger.info(f'Received {len(picture_path_list)} pictures that have not already been processed')
        self._init_progress_bar()

    def _init_progress_bar(self) -> None:
        self._progress_bar = ProgressBar()
        self._progress_counter = 0

    def _update_progress_bar(self) -> None:
        self._progress_counter = self._progress_counter + 1
        self._progress_bar.update(self._progress_counter)

    async def _process(self, path: Path, semaphore: Semaphore) -> Path:
        async with semaphore:
            try:
                exif_manager = ExifManager(path=path)

                hash = await exif_manager.get_hash()

                if hash is None:
                    hash = await Hasher(exif_manager.get_image()).hash()
                    # Do not record hash in exif to prevent file modification
                    # await exif_manager.record_hash_in_exif(hash=hash)

                already_exists = await self._async_recorder.check_picture_exists(
                    hash=hash
                )

                if not already_exists:
                    thumbnail_manager = ThumbnailImage(exif_manager.get_image())

                    picture_info = PictureInfo(
                        creation_time=await exif_manager.get_creation_time(),
                        thumbnail=await thumbnail_manager.get_base64_thumbnail(),
                        orientation=await thumbnail_manager.get_orientation(),
                    )

                    await self._async_recorder.record_info(info=picture_info, hash=hash)

                picture_file = PictureFile(
                    crawler_id=self._crawler_id,
                    picture_path=str(path),
                    last_seen=self._crawl_time,
                    resolution=await exif_manager.get_resolution(),
                )

                await self._async_recorder.record_file(file=picture_file, hash=hash)

            except ExifImageImpossibleToOpen:
                self._update_progress_bar()
                await self._file_history_recorder.add_file(path)
                return path
            except HasherException:
                raise HasherException(str(path))

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
        semaphore = asyncio.Semaphore(20)

        self._progress_bar.start(max_value=len(self._picture_path_list))

        task_list = [
            asyncio.create_task(self._process(path=path, semaphore=semaphore))
            for path in self._picture_path_list
        ]

        result = await asyncio.gather(*task_list, return_exceptions=True)

        await self._async_recorder.close_session()

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
