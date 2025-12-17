from abc import ABC, abstractmethod
import os
from pathlib import Path


class iFileTools(ABC):
    @abstractmethod
    def list_pictures(
        self, root_path_list: list[Path], folder_name_to_exclude: list[str]
    ) -> list[Path]:
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

    @abstractmethod
    def list_directories(self, root_path: Path) -> list[Path]:
        """List all directories in the given root path"""
        pass


class FileTools(iFileTools):
    def __init__(self) -> None:
        pass

    def _list_pictures_in_path(
        self, root_path: Path, folder_name_to_exclude: list[str]
    ) -> list[Path]:
        small_case_jpg = [x for x in root_path.glob("**/*.jpg")]
        capital_case_jpg = [x for x in root_path.glob("**/*.JPG")]

        output = [*small_case_jpg, *capital_case_jpg]

        for folder_name in folder_name_to_exclude:
            output = self.exclude_file_from_folder(
                paths=output, folder_name=folder_name
            )

        return output

    def list_pictures(
        self, root_path_list: list[Path], folder_name_to_exclude: list[str]
    ) -> list[Path]:

        output = []

        for root_path in root_path_list:
            output.extend(
                self._list_pictures_in_path(
                    root_path=root_path, folder_name_to_exclude=folder_name_to_exclude
                )
            )

        return output

    def exclude_file_from_folder(
        self, paths: list[Path], folder_name: str
    ) -> list[Path]:
        return [p for p in paths if not any(part == folder_name for part in p.parts)]

    def move_file(self, origin_path: Path, target_path: Path):
        if not target_path.parent.exists():
            target_path.parent.mkdir(parents=True)

        origin_path.rename(target_path)

    def rename_file(self, origin_folder_path: Path, new_folder_path: Path) -> None:
        """Rename a file to a new name in the same directory."""
        os.rename(origin_folder_path, new_folder_path)

    def list_directories(self, root_path: Path) -> list[Path]:
        """List all directories in the given root_path"""
        if not root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")

        if not root_path.is_dir():
            raise ValueError(f"Path is not a directory: {root_path}")

        return [p for p in root_path.iterdir() if p.is_dir() and p != root_path]
