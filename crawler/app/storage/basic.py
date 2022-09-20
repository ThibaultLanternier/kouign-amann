import shutil
import os
import boto3
import requests

from abc import ABC, abstractmethod
from typing import Dict, Callable, List, TypedDict

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
    def delete(self, picture_hash: str) -> bool:
        pass


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

class GooglePhotosAPIException(Exception):
    pass
class GooglePhotosAPIClient:
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    def _upload_bytes(self, picture_file_path: str) -> str:
        with open(picture_file_path, 'rb') as f:
            data = f.read()
            res = requests.post(
                    url='https://photoslibrary.googleapis.com/v1/uploads',
                    data=data,
                    headers={
                        'Content-Type': 'application/octet-stream',
                        "Authorization": f"Bearer {self._access_token}",
                        "X-Goog-Upload-Content-Type": "image/jpeg",
                        "X-Goog-Upload-Protocol": "raw"
                    })
            if res.status_code == 200:
                return res.text

        raise GooglePhotosAPIException(res.json())

    def _create_media_item(self, upload_token: str, picture_hash: str) -> str:
        res = requests.post(
            url='https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate',
            json={
                "newMediaItems": [
                    {
                        "description": "Imported by Kouign-Aman",
                        "simpleMediaItem": {
                                "fileName": f"{picture_hash}.jpg",
                                "uploadToken": upload_token
                            }
                    }
                ]
            },
            headers={
                "Authorization": f"Bearer {self._access_token}",
            }
        )

        if res.status_code == 200:
            return res.json()

        raise GooglePhotosAPIException(res.json())

    def upload_picture(self, picture_file_path: str, picture_hash: str) -> str:
        upload_token = self._upload_bytes(picture_file_path=picture_file_path)
        result = self._create_media_item(upload_token=upload_token, picture_hash=picture_hash)

        return result["newMediaItemResults"][0]['mediaItem']['id']

    def edit_picture_description(self, picture_id: str, new_description: str) -> bool:
        res = requests.patch(
            url=f"https://photoslibrary.googleapis.com/v1/mediaItems/{picture_id}?updateMask=description",
            json={"description": new_description},
            headers={
                "Authorization": f"Bearer {self._access_token}",
            }
        )

        if res.status_code == 200:
            return True

        raise GooglePhotosAPIException(res.json())

    def get_picture_info(self, picture_id: str) -> Dict:
        res = requests.get(
            url=f"https://photoslibrary.googleapis.com/v1/mediaItems/{picture_id}",
            headers={
                "Authorization": f"Bearer {self._access_token}",
            }
        )

        if res.status_code == 400:
            return None

        if res.status_code == 200:
            return res.json()

        raise GooglePhotosAPIException(res.json())

class GooglePhotosStorage(AbstractStorage):
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    def backup(self, picture_local_path: str, picture_hash: str) -> bool:
        raise NotImplementedError()

    def check_still_exists(self, picture_hash: str) -> bool:
        raise NotImplementedError()

    def delete(self, picture_hash: str) -> bool:
        raise NotImplementedError()

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

    def backup(self, picture_local_path: str, picture_hash) -> bool:
        if not self.check_hash(picture_local_path, picture_hash):
            raise PictureHashMissmatch

        return self._client.upload_file(
            picture_local_path, self._bucket, f"{self._prefix}{picture_hash}"
        )

    def check_still_exists(self, picture_hash: str) -> bool:
        content_list = self._client.list_objects(
            Bucket=self._bucket,
            Prefix=f"{self._prefix}{picture_hash}",
        )

        return f"{self._prefix}{picture_hash}" in content_list

    def delete(self, picture_hash: str) -> bool:
        self._client.delete_object(
            Bucket=self._bucket, Prefix=f"{self._prefix}{picture_hash}"
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
            bucket=config.config["bucket"],
            s3_client=S3Client(
                aws_key=config.config["key"],
                aws_secret=config.config["secret"],
            ),
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
