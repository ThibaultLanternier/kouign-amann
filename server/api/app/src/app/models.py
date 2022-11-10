import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Tuple, Union

from src.tools.date import DateTimeConverter, DateTimeFormatException


class DictFactory(dict):
    def __init__(self, data):
        data = [x for x in data if x[1] is not None]
        super().__init__(self._format_value(key=x[0], value=x[1]) for x in data)

    def _format_value(self, key: str, value: Any) -> Tuple[str, Any]:
        if isinstance(value, datetime):
            value = DateTimeConverter().to_string(value)

        if isinstance(value, Enum):
            value = value.name

        return (key, value)


class BackupStatus(str, Enum):
    PENDING = "PENDING"
    DONE = "DONE"
    ERROR = "ERROR"
    PENDING_DELETE = "PENDING_DELETE"


@dataclass
class File:
    crawler_id: str
    resolution: Tuple[int, int]
    picture_path: str
    last_seen: datetime

    def __post_init__(self):
        if not isinstance(self.last_seen, datetime):
            self.last_seen = DateTimeConverter().from_string(self.last_seen)

        if not DateTimeConverter().is_timezone_aware(self.last_seen):
            raise DateTimeFormatException("creation_time needs to be timeaware")

    def _get_pixels(self):
        return self.resolution[0] * self.resolution[1]

    def __eq__(self, other) -> bool:
        return (
            self._get_pixels() == other._get_pixels()
            and self.last_seen == other.last_seen
        )

    def __gt__(self, other) -> bool:
        """
        File with higher resolution are considered better for storage,
        if resolution are the same, the younger file is kept for storage
        """

        if self._get_pixels() > other._get_pixels():
            return True

        if self._get_pixels() == other._get_pixels():
            return self.last_seen > other.last_seen

        return False

    def __ge__(self, other) -> bool:
        return self > other or self == other


@dataclass
class BackupRequest:
    crawler_id: str
    storage_id: str
    file_path: str
    picture_hash: str
    status: BackupStatus
    backup_id: str


@dataclass
class BackupWithoutBackupId:
    crawler_id: str
    storage_id: str
    file_path: str
    status: BackupStatus
    creation_time: datetime


@dataclass
class Backup(BackupWithoutBackupId):
    backup_id: Union[str, None]


class StorageType(Enum):
    AWS_GLACIER = 0
    AWS_S3 = 1
    GOOGLE_PHOTOS = 2


@dataclass
class Storage:
    id: str


@dataclass
class StorageConfig(Storage):
    type: StorageType
    config: Dict[str, str]

    def __post_init__(self):
        if not isinstance(self.type, StorageType):
            if self.type not in StorageType._member_map_:
                raise Exception(f"Unknown storage type {self.type}")

            self.type = StorageType[self.type]

        for key in self.config.keys():
            value = self.config[key]

            if isinstance(value, dict) and value.get("from_env") is not None:
                env_key = value["from_env"]
                value = os.getenv(env_key)
                if value is None:
                    raise Exception(f"Environment variable {env_key} is None")

                self.config[key] = value

            if not isinstance(value, str):
                raise Exception(f"Config key {key} is of type {type(value)} not string")


class BackupException(Exception):
    pass


@dataclass
class PictureInfo:
    creation_time: datetime
    thumbnail: str
    orientation: str

    def __post_init__(self):
        if not isinstance(self.creation_time, datetime):
            self.creation_time = DateTimeConverter().from_string(self.creation_time)

        if not DateTimeConverter().is_timezone_aware(self.creation_time):
            raise DateTimeFormatException("creation_time needs to be timeaware")


@dataclass
class Picture:
    hash: str
    info: PictureInfo
    backup_required: bool
    file_list: List[File]
    backup_list: List[Backup]

    def plan_backup(self, storage_list: List[Storage], current_time: datetime) -> None:
        if self.backup_required:
            for storage in storage_list:
                if not self._check_backup_exists(storage.id):
                    best_file = self._get_best_file()

                    self.backup_list.append(
                        Backup(
                            crawler_id=best_file.crawler_id,
                            storage_id=storage.id,
                            file_path=best_file.picture_path,
                            status=BackupStatus.PENDING,
                            creation_time=current_time,
                            backup_id=None,
                        )
                    )
        else:
            self.backup_list = [
                self._change_backup_status(backup, BackupStatus.PENDING_DELETE)
                for backup in self._get_already_done_backup()
            ]

    def _change_backup_status(
        self, backup_request: Backup, new_status: BackupStatus
    ) -> Backup:
        backup_request.status = new_status
        return backup_request

    def _get_already_done_backup(self) -> List[Backup]:
        return [x for x in self.backup_list if x.status == BackupStatus.DONE]

    def _get_best_file(self) -> File:
        if len(self.file_list) == 0:
            raise BackupException("No file found for this Picture")

        self.file_list.sort(reverse=True)

        return self.file_list[0]

    def _check_backup_exists(self, storage_id: str) -> bool:
        for backup in self.backup_list:
            if backup.storage_id == storage_id:
                return True

        return False

    def update_file(self, new_file: File):
        for index, file in enumerate(self.file_list):
            if (
                file.crawler_id == new_file.crawler_id
                and file.picture_path == new_file.picture_path
            ):
                self.file_list[index] = new_file
                return

        self.file_list.append(new_file)

    def _set_backup_status(
        self, storage_id: str, crawler_id: str, status: BackupStatus
    ) -> None:
        for backup in self.backup_list:
            if backup.storage_id == storage_id and backup.crawler_id == crawler_id:
                backup.status = status
                return

        raise BackupException(
            f"No planned backup for storage {storage_id} and crawler {crawler_id}"
        )

    def _set_backup_id(self, storage_id: str, crawler_id: str, backup_id: str) -> None:
        for backup in self.backup_list:
            if backup.storage_id == storage_id and backup.crawler_id == crawler_id:
                backup.backup_id = backup_id
                return

        raise BackupException(
            f"No planned backup for storage {storage_id} and crawler {crawler_id}"
        )

    def record_done(self, storage_id: str, crawler_id: str, backup_id: str) -> None:
        self._set_backup_status(
            storage_id=storage_id, crawler_id=crawler_id, status=BackupStatus.DONE
        )
        self._set_backup_id(
            storage_id=storage_id, crawler_id=crawler_id, backup_id=backup_id
        )

    def record_deleted(self, storage_id: str, crawler_id: str) -> None:
        for backup in self.backup_list:
            if backup.storage_id == storage_id and backup.crawler_id == crawler_id:
                self.backup_list.remove(backup)

    def record_backup_error(self, storage_id: str, crawler_id: str) -> None:
        self._set_backup_status(storage_id, crawler_id, BackupStatus.ERROR)


@dataclass
class PictureCount:
    date: datetime
    count: int
    start_date: datetime
    end_date: datetime


@dataclass
class GoogleAccessToken:
    access_token: str
    scope: List[str]
    token_type: str
    expires_at: datetime


def google_access_token_factory(input: Dict, now: datetime) -> GoogleAccessToken:
    if "refresh_token" in input:
        del input["refresh_token"]

    expiry_date = now + timedelta(seconds=input["expires_in"])
    input["expires_at"] = expiry_date

    del input["expires_in"]

    return GoogleAccessToken(**input)


@dataclass
class GoogleRefreshToken:
    refresh_token: str
    scope: List[str]
    issued_at: datetime
