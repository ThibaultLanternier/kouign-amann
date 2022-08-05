import unittest
from datetime import datetime
from unittest.mock import MagicMock

from progressbar import ProgressBar

from app.controllers.backup import BackupHandler
from app.controllers.picture import AbstractPictureAnalyzer
from app.controllers.recorder import PictureRESTRecorder
from app.models.backup import BackupRequest, BackupStatus
from app.processor import (BackupProcessor, ParalellPictureProcessor,
                           ParallelBackupProcessor, PictureProcessor)
from app.storage.basic import AbstractStorage, StorageException, StorageFactory


class TestPictureProcessor(unittest.TestCase):
    def test_process(self):
        mock_picture_instance = MagicMock(spec=AbstractPictureAnalyzer)
        mock_picture_instance.get_data.return_value = "PICTURE_DATA"
        mock_picture_instance.image_hash = "IMAGE_HASH"

        mock_picture_factory = MagicMock(return_value=mock_picture_instance)

        mock_picture_recorder = MagicMock(spec=PictureRESTRecorder)
        mock_picture_recorder.picture_already_exists.return_value = True
        mock_picture_recorder.record.return_value = "RETOUR"

        test_time = datetime(1980, 11, 30)

        processor = PictureProcessor(
            mock_picture_factory, mock_picture_recorder, 123, test_time, None, "xxx"
        )

        self.assertEqual(processor.process("picture_path"), "RETOUR")

        mock_picture_instance.get_data.assert_called_once_with(create_thumbnail=False)
        mock_picture_recorder.record.assert_called_once_with(
            picture_data="PICTURE_DATA", crawler_id=123, crawl_time=test_time
        )


class TestParalellPictureProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_logger = MagicMock(name="logger")
        self.mock_progress_bar = MagicMock(name="progress_bar", spec=ProgressBar)

    def test_constructor_run(self):
        mock_picture_processor = MagicMock(name="picture_processor", return_value=True)

        test_picture_processor = ParalellPictureProcessor(
            ["file1"],
            mock_picture_processor,
            self.mock_logger,
            self.mock_progress_bar,
            1,
        )
        test_picture_processor.run()

        mock_picture_processor.assert_called_once_with("file1", 0)
        self.assertGreaterEqual(self.mock_logger.info.call_count, 2)
        self.mock_progress_bar.start.assert_called_once_with(max_value=1)
        self.mock_progress_bar.update.assert_called_once_with(1)
        self.mock_progress_bar.finish.assert_called_once_with()

    def test_constructor_run_with_error(self):
        mock_picture_processor = MagicMock(name="picture_processor", return_value=False)

        test_picture_processor = ParalellPictureProcessor(
            ["file1"],
            mock_picture_processor,
            self.mock_logger,
            self.mock_progress_bar,
            1,
        )
        test_picture_processor.run()

        mock_picture_processor.assert_called_once_with("file1", 0)
        self.mock_logger.error.assert_called_once()

    def test_constructor_run_with_exception(self):
        mock_picture_processor = MagicMock(
            name="picture_processor", return_value=True, side_effect=Exception("Error")
        )

        test_picture_processor = ParalellPictureProcessor(
            ["file1"],
            mock_picture_processor,
            self.mock_logger,
            self.mock_progress_bar,
            1,
        )
        test_picture_processor.run()

        mock_picture_processor.assert_called_once_with("file1", 0)
        self.mock_logger.exception.assert_called_once()


class TestBackupProcessor(unittest.TestCase):
    def setUp(self):
        self.mock_handler = MagicMock(spec=BackupHandler)
        mock_logger = MagicMock()

        self.mock_storage = MagicMock(spec=AbstractStorage)

        self.mock_storage_factory = MagicMock(spec=StorageFactory)
        self.mock_storage_factory.create_from_id.return_value = self.mock_storage

        self.processor = BackupProcessor(
            self.mock_handler, self.mock_storage_factory, mock_logger
        )
        self.backup_request = BackupRequest(
            crawler_id="A",
            storage_id="B",
            file_path="/file",
            picture_hash="C",
            status=BackupStatus.PENDING,
        )

    def test_process_ok(self):
        self.assertTrue(self.processor.process(self.backup_request))

        self.mock_handler.send_backup_completed.assert_called_once_with(
            self.backup_request
        )
        self.mock_storage.backup.assert_called_once_with(
            picture_local_path="/file", picture_hash="C"
        )

    def test_process_storage_exception(self):
        self.mock_storage.backup.side_effect = StorageException

        self.assertFalse(self.processor.process(self.backup_request))

        self.mock_handler.send_backup_error.assert_called_once_with(self.backup_request)
        self.mock_handler.send_backup_completed.assert_not_called()


class TestParallelBackupProcessor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_backup_processor = MagicMock(spec=BackupProcessor)
        mock_logger = MagicMock(name="logger")
        self.mock_progressbar = MagicMock(name="progressbar")

        self.mock_backup_processor.get_backup_requests.return_value = [
            BackupRequest(
                crawler_id="A",
                storage_id="B",
                file_path="/file",
                picture_hash="C",
                status=BackupStatus.PENDING,
            )
        ]

        self.parallel_processor = ParallelBackupProcessor(
            backup_processor=self.mock_backup_processor,
            logger=mock_logger,
            progressbar=self.mock_progressbar,
            worker_qty=2,
        )

    async def test_fill_queue(self):
        await self.parallel_processor._fill_queue()
        self.assertEqual(1, self.parallel_processor._backup_queue.qsize())

    async def test_create_workers(self):
        await self.parallel_processor._create_workers()
        self.assertEqual(2, len(self.parallel_processor._workers))
        self.assertFalse(self.parallel_processor._workers[0].done())
        self.assertFalse(self.parallel_processor._workers[0].cancelled())

    async def test_delete_workers(self):
        await self.parallel_processor._create_workers()
        await self.parallel_processor._delete_workers()
        self.assertEqual(2, len(self.parallel_processor._workers))
        self.assertTrue(self.parallel_processor._workers[0].cancelled())

    async def test_run(self):
        await self.parallel_processor.run()

        self.mock_progressbar.start.assert_called_once_with(max_value=1)
        self.mock_progressbar.update.assert_called_once_with(1)

    async def test_run_with_exception(self):
        self.mock_backup_processor.process.side_effect = Exception
        await self.parallel_processor.run()
