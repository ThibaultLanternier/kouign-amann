from dataclasses import dataclass

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
    def delete(self, picture_backup_id) -> bool:
        pass
