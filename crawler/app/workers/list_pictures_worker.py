from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from enum import Enum
from itertools import count
import json
import logging
from pathlib import Path
from unittest.mock import Base
from uuid import UUID
from h11 import Data
from pydantic import BaseModel

from isort import file

from app.use_cases.backup import BackupUseCase, backup_use_case_factory
from app.tools.config_file import ConfigFileManager
from app.workers.data_store import DataStore

logger = logging.getLogger("app.backup_worker")

class ListPictureJobResult(BaseModel):
    status: str = "pending"
    result: list[str] = []
    count: int = 0
    error: str | None = None

class AsyncJob(ABC):
    @abstractmethod
    async def run(self) -> None:
        """Run the job asynchronously"""
        pass

class ListPicturesJob(AsyncJob):
    """Represents a backup job"""
    def __init__(
            self, 
            job_id: UUID, 
            backup_use_case: BackupUseCase,
            data_store: DataStore[ListPictureJobResult]
        ):
        self.job_id = job_id
        self._backup_use_case = backup_use_case
        
        self._data_store = data_store

    def init(self, target_folder: Path) -> None:
        """Initialize the job with the target folder"""
        self.folder_path = target_folder
        
        self._result = ListPictureJobResult()   

    async def run(self) -> None:
        """Run the backup job asynchronously"""
        # Implement the actual backup logic here

        self._result.status = "running"
        logger.info(f"Starting ListFolderJob {self.job_id} for folder {self.folder_path}")
        self._data_store.save_data(self._result, str(self.job_id))

        try:
            picture_list = self._backup_use_case.list_pictures(root_path=self.folder_path)
            logger.info(f"Completed ListFolderJob {self.job_id} found {len(picture_list)} pictures")
            self._result.result = [str(picture) for picture in picture_list]
            self._result.status = "completed"
            self._result.count = len(picture_list)

            self._data_store.save_data(self._result, str(self.job_id))
        except Exception as e:
            logger.exception(f"ListFolderJob {self.job_id} failed: {e}")
            self._result.status = "failed"
            self._result.error = str(e)

            self._data_store.save_data(self._result, str(self.job_id))