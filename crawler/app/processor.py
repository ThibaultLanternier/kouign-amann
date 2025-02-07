import asyncio
import logging
from asyncio import Semaphore, Task
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Any, Callable, List, Type
from uuid import UUID

from progressbar import ProgressBar

from app.controllers.backup import AbstractBackupHandler
from app.controllers.exif import (ExifException, ExifImageImpossibleToOpen,
                                  ExifManager)
from app.controllers.hashing import Hasher, HasherException
from app.controllers.picture import (AbstractPictureAnalyzer,
                                     CorruptedPictureFileError)
from app.controllers.recorder import (AsyncCrawlHistoryStore, AsyncRecorder,
                                      CrawlHistoryStore, PictureRESTRecorder,
                                      RecorderException, iAsyncRecorder)
from app.controllers.thumbnail import ThumbnailImage
from app.models.backup import BackupRequest, BackupStatus
from app.models.picture import PictureFile, PictureInfo
from app.storage.factory import StorageFactory
from app.tools.metrics import MetricRecorder


class ParalellPictureProcessor:
    def __init__(
        self,
        picture_path_list: List[Path],
        picture_processor: Callable[[Path, int], bool],
        logger,
        progressbar: ProgressBar,
        worker_qty: int = 4,
    ):
        self.picture_processor = picture_processor
        self.worker_qty = worker_qty

        self.picture_path_queue: Queue = Queue(maxsize=-1)
        self.logger = logger

        for file_path in picture_path_list:
            self.picture_path_queue.put(file_path)

        self.threads = []

        self.total_queue_size = self.picture_path_queue.qsize()

        self.logger.info(f"Found {self.total_queue_size} pictures to process")
        self.logger.info(f"Starting processing with {self.worker_qty} workers")

        self.progressbar = progressbar
        self.progressbar.start(max_value=self.total_queue_size)

        for i in range(self.worker_qty):
            t = Thread(target=self.__process, args=[i])
            t.start()
            self.threads.append(t)

    def __process(self, worker_id):
        while True:
            current_picture_path = self.picture_path_queue.get()

            if current_picture_path is None:
                break

            try:
                if not self.picture_processor(current_picture_path, worker_id):
                    self.logger.error(
                        f"Worker {worker_id} failed for {current_picture_path}"
                    )
            except Exception:
                self.logger.exception(
                    f"Worker {worker_id} failed for {current_picture_path}"
                )

            self.picture_path_queue.task_done()
            self.progressbar.update(
                self.total_queue_size - self.picture_path_queue.qsize()
            )

    def run(self):
        self.picture_path_queue.join()

        for i in range(self.worker_qty):
            self.picture_path_queue.put(None)

        for t in self.threads:
            t.join()

        self.progressbar.finish()


def record_metric_file(recorder: MetricRecorder, file_name: str) -> None:
    with open(file_name, "a") as file:
        file.write(recorder.get_line())
        file.write("\n")


class PictureProcessor:
    def __init__(
        self,
        picture_factory: Callable[[Path], AbstractPictureAnalyzer],
        picture_recorder: PictureRESTRecorder,
        crawler_id: str,
        crawl_time: datetime,
        metrics_output_path: str,
        crawl_id: UUID,
        crawl_history: CrawlHistoryStore,
    ):
        self.picture_factory = picture_factory
        self.picture_recorder = picture_recorder
        self.crawler_id = crawler_id
        self.crawl_time = crawl_time
        self.metrics_path = metrics_output_path
        self.crawl_id = crawl_id
        self.crawl_history = crawl_history

    def _get_file_name(self, worker_id, name) -> str:
        influx_file = f"picture-{name}-{self.crawl_id}-{worker_id}.influx"
        return f"{self.metrics_path}/{influx_file}"

    def process(self, picture_path: Path, worker_id: int) -> bool:
        try:
            picture = self.picture_factory(picture_path)

            if self.picture_recorder.picture_already_exists(picture.get_hash()):
                picture_data = picture.get_data(create_thumbnail=False)
            else:
                picture_data = picture.get_data(create_thumbnail=True)

            record_result = self.picture_recorder.record(
                picture_data=picture_data,
                crawler_id=self.crawler_id,
                crawl_time=self.crawl_time,
            )
        except CorruptedPictureFileError:
            self.crawl_history.add_file(path=picture_path, worker_id=worker_id)
            return False

        if self.metrics_path is not None:
            record_metric_file(
                picture.get_metric(), self._get_file_name(worker_id, "analyze")
            )
            record_metric_file(
                self.picture_recorder.record_metric,
                self._get_file_name(worker_id, "record"),
            )

        if record_result:
            self.crawl_history.add_file(path=picture_path, worker_id=worker_id)

        return record_result


class BackupProcessor:
    def __init__(
        self,
        backup_handler: AbstractBackupHandler,
        storage_factory: StorageFactory,
        logger,
    ):
        self._backup_handler = backup_handler
        self._storage_factory = storage_factory
        self._logger = logger

    def process(self, request: BackupRequest) -> bool:
        self._logger.debug(
            f"SYNC processing backup for picture {request.picture_hash}"
        )  # noqa: E501
        storage = self._storage_factory.create_from_id(request.storage_id)

        try:
            if request.status == BackupStatus.PENDING:
                backup_result = storage.backup(
                    picture_local_path=Path(request.file_path),
                    picture_hash=request.picture_hash,
                )
                request.backup_id = backup_result.picture_bckup_id

                if backup_result.status:
                    self._backup_handler.send_backup_completed(request)
                else:
                    self._backup_handler.send_backup_error(request)

                return backup_result.status

            else:
                storage.delete(picture_backup_id=request.backup_id)
                self._backup_handler.send_backup_completed(request)

                return True

        except Exception as e:
            self._logger.warning(
                f"Picture {request.picture_hash} failed for {request.backup_id}: {e}"
            )
            self._backup_handler.send_backup_error(request)

            return False

    def get_backup_requests(self) -> List[BackupRequest]:
        return self._backup_handler.get_backup_requests()


class ParallelBackupProcessor:
    def __init__(
        self,
        backup_processor: BackupProcessor,
        logger,
        progressbar: ProgressBar,
        worker_qty: int = 3,
    ):
        self._backup_processor = backup_processor
        self._logger = logger
        self._worker_qty = worker_qty
        self._workers: List[Task] = []
        self._progressbar = progressbar

    async def _fill_queue(self):
        self._backup_queue = asyncio.Queue()

        loop = asyncio.get_event_loop()
        all_requests = await loop.run_in_executor(
            None, self._backup_processor.get_backup_requests
        )

        delete_requests = [
            request
            for request in all_requests
            if request.status == BackupStatus.PENDING_DELETE
        ]
        backup_requests = [
            request
            for request in all_requests
            if request.status == BackupStatus.PENDING
        ]

        self._logger.info(f"Retrieved {len(all_requests)} backup requests")
        self._logger.info(
            f"{len(delete_requests)} deletion(s), {len(backup_requests)} backup(s)"  # noqa: E501
        )

        for request in all_requests:
            await self._backup_queue.put(request)

        self._requests_count = self._backup_queue.qsize()

        if self._requests_count > 0:
            self._progressbar.start(max_value=self._requests_count)

    async def _create_workers(self):
        for i in range(self._worker_qty):
            worker = asyncio.create_task(
                self.backup_process_worker(f"backup-worker-{i}")
            )
            self._logger.debug(f"Worker {i} created")
            self._workers.append(worker)

    async def _delete_workers(self):
        for worker in self._workers:
            worker.cancel()

        await asyncio.gather(*self._workers, return_exceptions=True)

    async def backup_process_worker(self, name: str):
        while True:
            loop = asyncio.get_event_loop()
            backup_request: BackupRequest = await self._backup_queue.get()
            self._logger.debug(
                f"{name} retrieved backup request for {backup_request.picture_hash} on {backup_request.backup_id}"  # noqa: E501
            )

            try:
                result = await loop.run_in_executor(
                    None, self._backup_processor.process, backup_request
                )

                self._progressbar.update(
                    self._requests_count - self._backup_queue.qsize()
                )

                if not result:
                    self._logger.error(
                        f"backup failed for {backup_request.picture_hash}"
                    )

            except Exception as e:
                self._logger.exception(e)

            self._backup_queue.task_done()

    def _exception_handler(self, loop, context):
        self._logger.error(context)

    async def run(self):
        loop = asyncio.get_event_loop()

        loop.set_exception_handler(self._exception_handler)

        await self._fill_queue()

        await self._create_workers()

        await self._backup_queue.join()

        await self._delete_workers()

    async def run_forever(self):
        while True:
            self._logger.info("Polling new backup requests")
            await self.run()
            await asyncio.sleep(3)


class AsyncPictureProcessor:
    def __init__(
        self,
        picture_path_list: List[Path],
        async_recorder: iAsyncRecorder,
        file_history_recorder: AsyncCrawlHistoryStore,
        crawler_id: str,
        crawl_time: datetime,
    ) -> None:
        self._picture_path_list = picture_path_list
        self._async_recorder = async_recorder
        self._file_history_recorder = file_history_recorder
        self._crawl_time = crawl_time
        self._crawler_id = crawler_id

        self._logger = logging.getLogger("app.crawlasync")
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
                    await exif_manager.record_hash_in_exif(hash=hash)

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

        self._logger.info(f"Processed {len(success)} files successfully")
        self._logger.info(f"Exif processing failed on {exif_exception_count} files")
        self._logger.info(f"File recording failed on {record_exception_count} files")
        self._logger.info(f"Hashing failed on {hashing_exception_count} files")

        total = len(success) + exif_exception_count + record_exception_count

        self._logger.info(f"TOTAL files processed : {total}")
