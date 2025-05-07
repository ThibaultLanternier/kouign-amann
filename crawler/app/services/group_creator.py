from abc import ABC, abstractmethod
from datetime import timedelta

from app.entities.picture_data import iPictureData
from app.entities.picture_group import PictureGroup, iPictureGroup


class iGroupCreatorService(ABC):
    @abstractmethod
    def get_group_list(self, picture_list: list[iPictureData]) -> list[iPictureGroup]:
        raise NotImplementedError(
            "iGroupCreatorService.get_group_list() is not implemented"
        )


class GroupCreatorService(iGroupCreatorService):
    def __init__(self, hours_btw_picture: int = 24) -> None:
        self._hours_btw_picture = timedelta(days=0, hours=hours_btw_picture)

    def _convert_to_group(
        self, group_list: list[list[iPictureData]]
    ) -> list[iPictureGroup]:
        return [PictureGroup(group) for group in group_list]

    def get_group_list(self, picture_list: list[iPictureData]) -> list[iPictureGroup]:
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
