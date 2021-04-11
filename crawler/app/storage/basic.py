import shutil
import os
import boto3

from abc import abstractmethod
from typing import Dict, Callable

from app.controllers.picture import PictureAnalyzerFactory
from app.controllers.backup import AbstractStorageConfigProvider
from app.models.backup import StorageConfig, StorageType


class StorageException(Exception):
    pass


class PictureHashMissmatch(StorageException):
    pass


class PictureWithNoHash(StorageException):
    pass


class AbstractStorage:
    def check_hash(self, picture_local_path: str, picture_hash: str) -> bool:
        recorded_picture_hash = (
            PictureAnalyzerFactory()
            .perception_hash(picture_local_path)
            .get_recorded_hash()
        )

        if recorded_picture_hash is None:
            raise PictureWithNoHash(
                f"Picture located at {picture_local_path} has no hash"
            )

        return picture_hash == recorded_picture_hash

    @abstractmethod
    def backup(self, picture_local_path: str, picture_hash: str) -> bool:
        pass

    @abstractmethod
    def check_still_exists(self, picture_hash: str) -> bool:
        pass

    @abstractmethod
    def delete(self, picture_hase: str) -> bool:
        pass


class S3BackupStorage(AbstractStorage):
    def __init__(
        self,
        aws_key: str,
        aws_secret: str,
        bucket: str,
        prefix: str = "picture-backup/",
    ):
        self._aws_key = aws_key
        self._aws_secret = aws_secret
        self._bucket = bucket
        self._prefix = prefix

        self._client = boto3.client(
            "s3",
            aws_access_key_id=self._aws_key,
            aws_secret_access_key=self._aws_secret,
        )

    def __del__(self):
        del self._client

    def backup(self, picture_local_path: str, picture_hash) -> bool:
        if not self.check_hash(picture_local_path, picture_hash):
            raise PictureHashMissmatch

        self._client.upload_file(
            picture_local_path, self._bucket, f"{self._prefix}{picture_hash}"
        )

        return True

    def check_still_exists(self, picture_hash: str) -> bool:
        response = self._client.list_objects(
            Bucket=self._bucket,
            Prefix=f"{self._prefix}{picture_hash}",
        )

        contents = response.get("Contents")
        if not isinstance(contents, list):
            return False

        if len(contents) == 1:
            return contents[0].get("Key") == f"{self._prefix}{picture_hash}"
        else:
            return False

    def delete(self, picture_hash: str) -> bool:
        self._client.delete_object(
            Bucket=self._bucket, Key=f"{self._prefix}{picture_hash}"
        )

        return True


class SimpleFileStorage(AbstractStorage):
    def __init__(self, storage_folder: str):
        self.storage_folder = storage_folder

    def _get_file_path(self, picture_hash: str) -> str:
        return f"{self.storage_folder}/{picture_hash}"

    def backup(self, picture_local_path: str, picture_hash: str) -> bool:
        if not self.check_hash(
            picture_local_path=picture_local_path, picture_hash=picture_hash
        ):
            raise PictureHashMissmatch(
                f"Picture {picture_local_path} does not match hash {picture_hash}"
            )
        else:
            shutil.copyfile(picture_local_path, self._get_file_path(picture_hash))

            return True

    def delete(self, picture_hash: str) -> bool:
        os.remove(self._get_file_path(picture_hash))

        return True

    def check_still_exists(self, picture_hash: str) -> bool:
        raise NotImplementedError


class StorageFactoryException(Exception):
    pass


class StorageFactory:
    def __init__(self, storage_config_provider: AbstractStorageConfigProvider):
        self._config_provider = storage_config_provider
        self._storages: Dict[str, AbstractStorage] = {}
        self._factories: Dict[
            StorageType, Callable[[StorageConfig], AbstractStorage]
        ] = {StorageType.AWS_S3: self.AWS_S3_factory}

    def AWS_S3_factory(self, config: StorageConfig) -> AbstractStorage:
        return S3BackupStorage(
            aws_key=config.config["key"],
            aws_secret=config.config["secret"],
            bucket=config.config["bucket"],
        )

    def create_from_id(self, storage_id: str) -> AbstractStorage:
        if self._storages.get(storage_id) is None:
            config = self._config_provider.get_storage_config(storage_id=storage_id)

            factory = self._factories.get(config.type)

            if factory is None:
                raise StorageFactoryException(
                    f"No Factory available for storage of type {config.type}"
                )

            self._storages[storage_id] = factory(config)

        return self._storages[storage_id]
