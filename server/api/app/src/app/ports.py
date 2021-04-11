from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Union

from src.app.models import (BackupRequest, File, Picture, PictureCount,
                            PictureInfo, Storage, StorageConfig)


class MissingPictureException(Exception):
    pass


class AbstractPictureManager(ABC):
    @abstractmethod
    def list_pictures(self, start_date: datetime, end_date: datetime) -> List[Picture]:
        pass

    @abstractmethod
    def list_recently_updated_pictures(self, duration: timedelta) -> List[Picture]:
        pass

    @abstractmethod
    def get_picture(self, picture_hash: str) -> Union[Picture, None]:
        pass

    @abstractmethod
    def record_picture_info(self, hash: str, info: PictureInfo) -> None:
        pass

    @abstractmethod
    def record_picture_file(self, hash: str, file: File) -> None:
        pass

    @abstractmethod
    def record_picture(self, picture: Picture) -> None:
        pass

    @abstractmethod
    def count(self) -> List[PictureCount]:
        pass


class AbstractBackupManager(ABC):
    @abstractmethod
    def get_storages(self) -> List[Storage]:
        pass

    @abstractmethod
    def get_storage_config(self, storage_id: str) -> Union[None, StorageConfig]:
        pass

    @abstractmethod
    def get_pending_backup_request(
        self, crawler_id: str, limit: int = 20
    ) -> List[BackupRequest]:
        pass
