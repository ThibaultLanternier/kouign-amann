from abc import ABC, abstractmethod
import logging
from pathlib import Path
from app.entities.picture_data import iPictureData
from app.repositories.picture_data import iPictureDataRepository
import re


class PictureGroupException(Exception):
    pass


class NotUniqueFolderException(PictureGroupException):
    pass


class NotEditableGroupException(PictureGroupException):
    pass


class iPictureGroup(ABC):
    @abstractmethod
    def get_folder_path(self) -> Path:
        pass

    @abstractmethod
    def list_pictures_to_move(self) -> list[tuple[Path, Path]]:
        pass

    @abstractmethod
    def get_new_folder_name(
        self, picture_repository: iPictureDataRepository, verbose: bool
    ) -> Path:
        pass

    @abstractmethod
    def is_editable(self) -> bool:
        pass


MIN_GROUP_SIZE = 10


class PictureGroup(iPictureGroup):
    def _count_pictures_per_folder(
        self, picture_list: list[iPictureData]
    ) -> dict[Path, int]:
        folder_count: dict[Path, int] = {}

        for picture in picture_list:
            folder_path = picture.get_path().parent
            folder_name = folder_path.name

            if (
                folder_name != "NOT_GROUPED"
                and folder_name != self._get_other_folder_name()
            ):
                if folder_path not in folder_count:
                    folder_count[folder_path] = 0

                folder_count[folder_path] += 1

        return folder_count

    def _get_ordered_folder_list(self, folder_count: dict[Path, int]) -> list[Path]:
        def picture_count(item) -> int:
            return item[1]

        return [
            k
            for (k, v) in sorted(folder_count.items(), key=picture_count, reverse=True)
        ]

    def _add_not_grouped_folder(self, folder_list: list[Path]) -> list[Path]:
        if len(folder_list) == 0:
            first_picture: iPictureData = self._picture_list[0]
            root_folder = first_picture.get_path().parent.parent
            folder_list = [
                root_folder
                / Path(
                    f"{first_picture.get_creation_date().date()} <EVENT_DESCRIPTION>"
                )
            ]

        return folder_list

    def _get_other_folder_name(self) -> str:
        first_picture: iPictureData = self._picture_list[0]
        return f"{first_picture.get_creation_date().date().year} OTHER"

    def _get_too_small_group_folder_name(self) -> list[Path]:
        first_picture: iPictureData = self._picture_list[0]
        root_folder = first_picture.get_path().parent.parent
        return [root_folder / Path(self._get_other_folder_name())]

    def __init__(
        self, picture_list: list[iPictureData], min_group_size: int = MIN_GROUP_SIZE
    ) -> None:
        self._picture_list = picture_list

        self._min_group_size = min_group_size

        self._logger = logging.getLogger("app.picture_group_entity")

        self._logger.debug(f"Minimum group size {self._min_group_size}")

        if len(self._picture_list) == 0:
            raise Exception("A group must contain at least one picture path")

        if len(self._picture_list) >= self._min_group_size:
            # The group is large enough, so we can proceed with the grouping
            self._logger.debug(f"Size is OK {len(self._picture_list)} pictures")

            # Count the number of pictures in each folder (excluding "NOT_GROUPED")
            self._picture_path_count = self._count_pictures_per_folder(
                self._picture_list
            )

            # Sort the folders by the number of pictures in descending order
            self._folder_list = self._get_ordered_folder_list(self._picture_path_count)

            # If no folders are found, create a folder based on the first picture's date
            self._folder_list = self._add_not_grouped_folder(self._folder_list)
        else:
            self._logger.debug(
                f"Group too small, only {len(self._picture_list)} pictures"
            )

            # The group is too small all pictures shall go to <YEAR> OTHER folder
            self._folder_list = self._get_too_small_group_folder_name()

        self._logger.debug(
            f"PictureGroup initialized target path is ${self._folder_list[0]}"
        )

        for picture in self._picture_list:
            self._logger.debug(
                f"Picture {picture.get_path()} created on {picture.get_creation_date()}"
            )

    def get_picture_list(self) -> list[iPictureData]:
        return self._picture_list

    def get_folder_path(self) -> Path:
        return self._folder_list[0]

    def list_pictures_to_move(self) -> list[tuple[Path, Path]]:
        output: list[tuple[Path, Path]] = []

        for picture in self._picture_list:
            if self.get_folder_path() != picture.get_path().parent:
                origin_path = picture.get_path()
                target_path = self.get_folder_path() / picture.get_path().name

                output.append((origin_path, target_path))

        return output

    def _remove_date_from_name(self, folder_name: str) -> str:
        pattern = re.compile(r"\d{4}-\d{2}")
        match = re.match(pattern, folder_name)

        if match is not None:
            return re.sub(pattern, "", folder_name).strip()
        else:
            return folder_name

    def _get_folder_name_with_date(self, folder_name: str) -> str:
        min_date = min(picture.get_creation_date() for picture in self._picture_list)

        return f"{min_date.date()} {folder_name}".strip()

    def _is_raw_camera_folder(self, folder_name: str) -> bool:
        strings_to_exclude = ["CANON", "FUJI", "APPLE"]

        for string in strings_to_exclude:
            if string in folder_name:
                return True

        return False

    def get_new_folder_name(
        self, picture_repository: iPictureDataRepository, verbose=False
    ) -> Path:
        if not self.is_editable():
            raise NotEditableGroupException("This group is not editable")

        folder_name_count: dict[str, int] = {}

        if verbose:
            self._logger.info("get_new_folder_name VERBOSE MODE ENABLED")

        for picture in self._picture_list:
            folder_name_list = picture_repository.get_parents_folder_list(
                picture.get_hash()
            )

            if verbose:
                for folder_name in folder_name_list:
                    self._logger.debug(
                        f"Folder : {folder_name} for hash {picture.get_hash()}"
                    )

            folder_name_whitout_camera_folder = [
                folder
                for folder in folder_name_list
                if not self._is_raw_camera_folder(folder)
            ]

            clean_folder_name_list = [
                self._remove_date_from_name(folder_name)
                for folder_name in folder_name_whitout_camera_folder
            ]

            for folder_name in clean_folder_name_list:
                if folder_name not in folder_name_count:
                    folder_name_count[folder_name] = 0
                folder_name_count[folder_name] += 1

        if len(folder_name_count) == 0:
            return self.get_folder_path()

        USE_MAX_COUNT = False

        if USE_MAX_COUNT:
            new_folder_name = max(folder_name_count.items(), key=lambda k: k[1])[0]
        else:
            unique_folder_name = set(folder_name_count.keys())

            new_folder_name = "<OR>".join(list(unique_folder_name))

        new_folder_name_with_date = self._get_folder_name_with_date(new_folder_name)

        return self._picture_list[0].get_path().parent.parent / Path(
            new_folder_name_with_date
        )

    def is_editable(self) -> bool:
        folder_name_set: set[str] = {self._picture_list[0].get_path().parent.name}

        for picture in self._picture_list:
            folder_name_set.add(picture.get_path().parent.name)

        if len(folder_name_set) > 1:
            raise NotUniqueFolderException(
                f"This group contains more than one folder {folder_name_set}"
            )

        pattern = re.compile(r"^\d{4}-\d{2}-\d{2} <EVENT_DESCRIPTION>$")

        return re.match(pattern, list(folder_name_set)[0]) is not None
