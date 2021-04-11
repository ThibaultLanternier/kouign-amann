from dataclasses import dataclass
from enum import Enum
from typing import Dict


@dataclass
class BackupRequest:
    crawler_id: str
    storage_id: str
    file_path: str
    picture_hash: str


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
