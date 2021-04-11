from abc import ABC, abstractmethod
from typing import List
from dataclasses import asdict

import requests

from app.models.backup import BackupRequest, StorageConfig, StorageType


class BackupHandlerException(Exception):
    pass


class AbstractStorageConfigProvider(ABC):
    @abstractmethod
    def get_storage_config(self, storage_id: str) -> StorageConfig:
        pass


class AbstractBackupHandler(AbstractStorageConfigProvider):
    @abstractmethod
    def get_backup_requests(self) -> List[BackupRequest]:
        pass

    @abstractmethod
    def send_backup_completed(self, status: BackupRequest) -> bool:
        pass

    @abstractmethod
    def send_backup_error(self, status: BackupRequest) -> bool:
        pass


class BackupHandler(AbstractBackupHandler):
    def __init__(self, crawler_id: str, base_url: str) -> None:
        self.crawler_id = crawler_id
        self.base_url = base_url

    def get_backup_requests(self) -> List[BackupRequest]:
        response = requests.get(f"{self.base_url}/crawler/backup/{self.crawler_id}")

        if response.status_code == 200:
            content = response.json()
            try:
                return [BackupRequest(**request_dict) for request_dict in content]
            except TypeError:
                raise BackupHandlerException(
                    "ERROR RETRIEVING BACKUP REQUESTS - MALFORMED ANSWER"
                )
        else:
            raise BackupHandlerException("ERROR RETRIEVING BACKUP REQUESTS")

    def send_backup_completed(self, status: BackupRequest) -> bool:
        response = requests.post(
            f"{self.base_url}/crawler/backup/{self.crawler_id}", json=asdict(status)
        )

        if response.status_code == 201:
            return True
        else:
            return False

    def send_backup_error(self, status: BackupRequest) -> bool:
        response = requests.delete(
            f"{self.base_url}/crawler/backup/{self.crawler_id}", json=asdict(status)
        )

        if response.status_code == 201:
            return True
        else:
            return False

    def get_storage_config(self, storage_id: str) -> StorageConfig:
        response = requests.get(f"{self.base_url}/crawler/storage/{storage_id}")

        if response.status_code == 200:
            content = response.json()
            try:
                content["type"] = StorageType(content["type"])
                return StorageConfig(**content)
            except TypeError:
                raise BackupHandlerException(
                    "ERROR RETRIEVING STORAGE CONFIG - MALFORMED ANSWER"
                )
        else:
            raise BackupHandlerException("ERROR RETRIEVING STORAGE CONFIG")
