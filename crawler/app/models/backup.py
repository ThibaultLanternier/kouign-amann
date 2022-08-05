from dataclasses import dataclass
from enum import Enum
from typing import Dict


class BackupStatus(Enum):
    PENDING = "PENDING"
    PENDING_DELETE = "PENDING_DELETE"


@dataclass
class BackupRequest:
    crawler_id: str
    storage_id: str
    file_path: str
    picture_hash: str
    status: BackupStatus

    def __post_init__(self):
        if not isinstance(self.status, BackupStatus):
            self.status = BackupStatus(self.status)


class StorageType(Enum):
    AWS_GLACIER = "AWS_GLACIER"
    AWS_S3 = "AWS_S3"


@dataclass
class Storage:
    id: str


@dataclass
class StorageConfig(Storage):
    type: StorageType
    config: Dict[str, str]
