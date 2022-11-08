from typing import TypedDict, List
from abc import ABC, abstractmethod
import boto3
from app.storage.basic import AbstractStorage, BackupResult
from app.models.backup import StorageConfig


class S3Content(TypedDict):
    Key: str


class S3ListContentResponse(TypedDict):
    Contents: List[S3Content]


class S3DeleteObjectResponse(TypedDict):
    DeleteMarker: bool
    VersionId: str
    RequestCharged: str


class AbstractS3Client(ABC):
    @abstractmethod
    def upload_file(self, file_name: str, bucket: str, object_name: str) -> bool:
        pass

    @abstractmethod
    def list_objects(self, Bucket: str, Prefix: str) -> List[S3Content]:
        pass

    @abstractmethod
    def delete_object(self, Bucket: str, Prefix: str) -> None:
        pass


class S3Client(AbstractS3Client):
    def __init__(self, aws_key: str, aws_secret: str) -> None:
        self._client = boto3.client(
            "s3",
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
        )

    def upload_file(self, file_name: str, bucket: str, object_name: str) -> bool:
        try:
            self._client.upload_file(file_name, bucket, object_name)
            return True

        except boto3.exceptions.S3UploadFailedError:
            return False

    def list_objects(self, Bucket: str, Prefix: str) -> List[S3Content]:
        object_list = self._client.list_objects(
            Bucket=Bucket,
            Prefix=Prefix,
        )

        if object_list.get("Contents") is not None:
            return object_list.get("Contents")
        else:
            return []

    def delete_object(self, Bucket: str, Prefix: str) -> None:
        self._client.delete_object(Bucket=Bucket, Key=Prefix)

        return


class S3BackupStorage(AbstractStorage):
    def __init__(
        self,
        s3_client: AbstractS3Client,
        bucket: str,
        prefix: str = "picture-backup/",
    ):
        self._bucket = bucket
        self._prefix = prefix

        self._client = s3_client

    def __del__(self):
        del self._client

    def backup(self, picture_local_path: str, picture_hash) -> BackupResult:
        if not self.check_hash(picture_local_path, picture_hash):
            return BackupResult(status=False, picture_bckup_id=picture_hash)

        upload_result = self._client.upload_file(
            picture_local_path, self._bucket, f"{self._prefix}{picture_hash}"
        )

        return BackupResult(status=upload_result, picture_bckup_id=picture_hash)

    def check_still_exists(self, picture_backup_id: str) -> bool:
        content_list = self._client.list_objects(
            Bucket=self._bucket,
            Prefix=f"{self._prefix}{picture_backup_id}",
        )

        return f"{self._prefix}{picture_backup_id}" in content_list

    def delete(self, picture_backup_id: str) -> bool:
        self._client.delete_object(
            Bucket=self._bucket, Prefix=f"{self._prefix}{picture_backup_id}"
        )

        return True


def AWS_S3_factory(config: StorageConfig) -> AbstractStorage:
    return S3BackupStorage(
        bucket=config.config["bucket"],
        s3_client=S3Client(
            aws_key=config.config["key"],
            aws_secret=config.config["secret"],
        ),
    )
