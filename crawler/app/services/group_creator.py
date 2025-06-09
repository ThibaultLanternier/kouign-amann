from abc import ABC, abstractmethod
from datetime import timedelta
from pathlib import Path

from app.entities.picture_data import iPictureData
from app.entities.picture_group import PictureGroup, iPictureGroup


class iGroupCreatorService(ABC):
    @abstractmethod
    def get_group_list_from_time(
        self, picture_list: list[iPictureData]
    ) -> list[iPictureGroup]:
        pass

    @abstractmethod
    def get_group_list_from_folders(
        self, picture_list: list[iPictureData]
    ) -> list[iPictureGroup]:
        pass


class GroupCreatorService(iGroupCreatorService):
    def __init__(self, hours_btw_picture: int = 24) -> None:
        self._hours_btw_picture = timedelta(days=0, hours=hours_btw_picture)

    def _convert_to_group(
        self, group_list: list[list[iPictureData]]
    ) -> list[iPictureGroup]:
        return [PictureGroup(group) for group in group_list]

    def get_group_list_from_time(
        self, picture_list: list[iPictureData]
    ) -> list[iPictureGroup]:
        sorted_picture_list = sorted(picture_list, key=lambda x: x.get_creation_date())
        grouped_picture_path = []
        current_group = []

        previous_picture = None

        for picture in sorted_picture_list:
            if previous_picture is None:
                current_group.append(picture)
            else:
                time_difference = (
                    picture.get_creation_date() - previous_picture.get_creation_date()
                )

                if time_difference <= self._hours_btw_picture:
                    current_group.append(picture)
                else:
                    grouped_picture_path.append(current_group)
                    current_group = [picture]

            previous_picture = picture

        grouped_picture_path.append(current_group)

        return self._convert_to_group(grouped_picture_path)

    def get_group_list_from_folders(
        self, picture_list: list[iPictureData]
    ) -> list[iPictureGroup]:
        folder_dict: dict[Path, list[iPictureData]] = {}

        for picture in picture_list:
            folder_path = picture.get_path().parent
            if folder_path not in folder_dict:
                folder_dict[folder_path] = []
            folder_dict[folder_path].append(picture)

        group_list: list[iPictureGroup] = []

        for pictures in folder_dict.values():
            group_list.append(PictureGroup(pictures))

        return group_list
