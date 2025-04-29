from abc import ABC, abstractmethod
import logging
from pathlib import Path
from time import sleep

from app.entities.picture_data import iPictureData


class iFileService(ABC):
    @abstractmethod
    def backup(self, origin_path: Path, data: iPictureData) -> bool:
        pass

    @abstractmethod
    def move(self, origin_path: Path, target_path: Path) -> bool:
        pass

    @abstractmethod
    def list_pictures(self, root_path: Path) -> list[Path]:
        pass

class FileService(iFileService):
    def __init__(self, backup_folder_path: Path) -> None:
        self._backup_folder_path = backup_folder_path

        self._logger = logging.getLogger("app.file_service")
        self._logger.info(f"Init FileService Backup folder path is: {self._backup_folder_path}")

    def backup(self, origin_path: Path, data: iPictureData) -> bool:
        sleep(0.1)  # Simulate a delay for the backup process
        return True

    def move(self, origin_path: Path, target_path: Path) -> bool:
        raise NotImplementedError("Move method is not implemented")
    
    def list_pictures(self, root_path: Path) -> list[Path]:
        return [x for x in root_path.glob("**/*.jpg")]