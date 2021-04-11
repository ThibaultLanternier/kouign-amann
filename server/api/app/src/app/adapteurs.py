from datetime import datetime, timedelta
from typing import List, Union

from src.app.models import (BackupRequest, File, Picture, PictureCount,
                            PictureInfo, Storage, StorageConfig)
from src.app.ports import (AbstractBackupManager, AbstractPictureManager,
                           MissingPictureException)
from src.persistence.ports import PersistencePort


class PictureManager(AbstractPictureManager):
    def __init__(self, persistence: PersistencePort):
        self._persistence = persistence

    def list_pictures(self, start_date: datetime, end_date: datetime) -> List[Picture]:
        return self._persistence.list_pictures(start=start_date, end=end_date)

    def list_recently_updated_pictures(self, duration: timedelta) -> List[Picture]:
        return self._persistence.list_recently_updated_pictures(duration=duration)

    def get_picture(self, picture_hash: str) -> Union[Picture, None]:
        return self._persistence.get_picture(picture_hash)

    def record_picture_info(self, hash: str, info: PictureInfo) -> None:
        picture = self._persistence.get_picture(hash)

        if picture is None:
            picture = Picture(
                hash=hash,
                backup_required=False,
                file_list=[],
                info=info,
                backup_list=[],
            )
        else:
            picture.info = info

        self._persistence.record_picture(picture)

    def record_picture_file(self, hash: str, file: File) -> None:
        picture = self._persistence.get_picture(hash)

        if picture is None:
            raise MissingPictureException(f"Picture with hash {hash} not found")

        picture.update_file(file)

        self._persistence.record_picture(picture)

    def record_picture(self, picture: Picture) -> None:
        self._persistence.record_picture(picture)

    def count(self) -> List[PictureCount]:
        return self._persistence.count_picture()


DEFAULT_STORAGE_ID = "xxxx"


class BackupManager(AbstractBackupManager):
    def __init__(
        self, persistence: PersistencePort, storage_config_list: List[StorageConfig]
    ):
        self._persistence = persistence
        self._storage_config_list = {}

        for storage in storage_config_list:
            self._storage_config_list[storage.id] = storage

    def get_storages(self) -> List[Storage]:
        return [
            Storage(id=storage_id) for storage_id in self._storage_config_list.keys()
        ]

    def get_storage_config(self, storage_id: str) -> Union[None, StorageConfig]:
        return self._storage_config_list.get(storage_id, None)

    def get_pending_backup_request(
        self, crawler_id: str, limit: int = 20
    ) -> List[BackupRequest]:
        return self._persistence.get_pending_backup_request(
            crawler_id=crawler_id, limit=limit
        )
