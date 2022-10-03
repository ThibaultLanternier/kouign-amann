from dataclasses import dataclass
import shutil
import os

from abc import abstractmethod

from app.controllers.picture import PictureAnalyzerFactory


class StorageException(Exception):
    pass


class PictureHashMissmatch(StorageException):
    pass


class PictureWithNoHash(StorageException):
    pass


@dataclass
class BackupResult:
    status: bool
    picture_bckup_id: str


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
    def backup(self, picture_local_path: str, picture_hash: str) -> BackupResult:
        pass

    @abstractmethod
    def check_still_exists(self, picture_backup_id: str) -> bool:
        pass

    @abstractmethod
    def delete(self, picture_hash: str, picture_backup_id) -> bool:
        pass


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
