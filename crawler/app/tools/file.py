from abc import ABC, abstractmethod
import os
from pathlib import Path


class iFileTools(ABC):
    @abstractmethod
    def list_pictures(self, root_path: Path) -> list[Path]:
        """List all pictures in the given path"""
        pass

    @abstractmethod
    def move_file(self, origin_path: Path, target_path: Path):
        """Move file from origin to target path"""
        pass

    @abstractmethod
    def rename_file(self, origin_folder_path: Path, new_folder_path: Path) -> None:
        """Rename a file to a new name in the same directory."""
        pass


class FileTools(iFileTools):
    def __init__(self) -> None:
        pass

    def list_pictures(self, root_path: Path) -> list[Path]:
        small_case_jpg = [x for x in root_path.glob("**/*.jpg")]
        capital_case_jpg = [x for x in root_path.glob("**/*.JPG")]

        return [*small_case_jpg, *capital_case_jpg]

    def move_file(self, origin_path: Path, target_path: Path):
        if not target_path.parent.exists():
            target_path.parent.mkdir(parents=True)

        origin_path.rename(target_path)

    def rename_file(self, origin_folder_path: Path, new_folder_path: Path) -> None:
        """Rename a file to a new name in the same directory."""
        os.rename(origin_folder_path, new_folder_path)
