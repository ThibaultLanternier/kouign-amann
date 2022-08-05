import asyncio
from asyncio import Task
from datetime import datetime
from queue import Queue
from threading import Thread
from typing import Callable, List

from progressbar import ProgressBar

from app.controllers.backup import AbstractBackupHandler
from app.controllers.picture import AbstractPictureAnalyzer
from app.controllers.recorder import PictureRESTRecorder
from app.models.backup import BackupRequest, BackupStatus
from app.storage.basic import StorageException, StorageFactory
from app.tools.metrics import MetricRecorder


class ParalellPictureProcessor:
    def __init__(
        self,
        picture_path_list: List[str],
        picture_processor: Callable[[str], bool],
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
        picture_factory: Callable[[str], AbstractPictureAnalyzer],
        picture_recorder: PictureRESTRecorder,
        crawler_id: str,
        crawl_time: datetime,
        metrics_output_path: str,
        crawl_id: str,
    ):
        self.picture_factory = picture_factory
        self.picture_recorder = picture_recorder
        self.crawler_id = crawler_id
        self.crawl_time = crawl_time
        self.metrics_output_path = metrics_output_path
        self.crawl_id = crawl_id

    def _get_file_name(self, worker_id, name) -> str:
        return f"{self.metrics_output_path}/picture-{name}-{self.crawl_id}-{worker_id}.influx"

    def process(self, picture_path, worker_id=1):
        picture = self.picture_factory(picture_path)

        if self.picture_recorder.picture_already_exists(picture.image_hash):
            picture_data = picture.get_data(create_thumbnail=False)
        else:
            picture_data = picture.get_data(create_thumbnail=True)

        record_result = self.picture_recorder.record(
            picture_data=picture_data,
            crawler_id=self.crawler_id,
            crawl_time=self.crawl_time,
        )

        if self.metrics_output_path is not None:
            record_metric_file(
                picture.get_metric(), self._get_file_name(worker_id, "analyze")
            )
            record_metric_file(
                self.picture_recorder.record_metric,
                self._get_file_name(worker_id, "record"),
            )
            record_metric_file(
                self.picture_recorder.picture_exists_metric,
                self._get_file_name(worker_id, "check"),
            )

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

    def process(self, backup_request: BackupRequest) -> bool:
        self._logger.debug(
            f"SYNC processing backup for picture {backup_request.picture_hash}"
        )
        storage = self._storage_factory.create_from_id(backup_request.storage_id)

        try:
            if backup_request.status == BackupStatus.PENDING:
                storage.backup(
                    picture_local_path=backup_request.file_path,
                    picture_hash=backup_request.picture_hash,
                )
            else:
                storage.delete(picture_hash=backup_request.picture_hash)

        except StorageException as e:
            self._logger.warning(
                f"Processing of picture {backup_request.picture_hash} failed : {e}"
            )
            self._backup_handler.send_backup_error(backup_request)
            return False

        self._backup_handler.send_backup_completed(backup_request)
        return True

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
        backup_delete_requests = await loop.run_in_executor(
            None, self._backup_processor.get_backup_requests
        )

        delete_requests = [request for request in backup_delete_requests if request.status == BackupStatus.PENDING_DELETE]
        backup_requests = [request for request in backup_delete_requests if request.status == BackupStatus.PENDING]

        self._logger.info(f"Retrieved {len(backup_delete_requests)} backup requests")
        self._logger.info(f"{len(delete_requests)} deletion(s), {len(backup_requests)} backup(s)")

        for request in backup_delete_requests:
            await self._backup_queue.put(request)

        self._total_backup_requests = self._backup_queue.qsize()

        if self._total_backup_requests > 0:
            self._progressbar.start(max_value=self._total_backup_requests)

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
                f"{name} retrieved backup request for {backup_request.picture_hash}"
            )

            try:
                result = await loop.run_in_executor(
                    None, self._backup_processor.process, backup_request
                )
                if result:
                    self._progressbar.update(
                        self._total_backup_requests - self._backup_queue.qsize()
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
