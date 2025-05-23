from datetime import timezone
from pathlib import Path

from app.entities.picture_data import iPictureData
from app.tools.file import FileTools, iFileTools
from app.use_cases.backup import baseUseCase
from app.services.group_creator import GroupCreatorService, iGroupCreatorService
from app.factories.picture_data import (
    NotStandardFileNameException,
    PictureDataFactory,
    iPictureDataFactory,
)
from app.entities.picture import PictureException


class GroupUseCase(baseUseCase):
    def __init__(
        self,
        file_tools: iFileTools,
        picture_data_factory: iPictureDataFactory,
        group_creator_service: iGroupCreatorService,
    ):
        super().__init__(
            file_tools=file_tools, picture_data_factory=picture_data_factory
        )

        self._group_creator_service = group_creator_service

    def group(self, picture_list: list[Path]):
        picture_data_list: list[iPictureData] = []

        for picture_path in picture_list:
            try:
                picture_data = self._picture_data_factory.from_standard_path(
                    path=picture_path, current_timezone=timezone.utc
                )
                picture_data_list.append(picture_data)
            except NotStandardFileNameException as e:
                self._logger.warning(
                    f"Found non standard path for picture {picture_path}: {e}"
                )
                try:
                    picture_data = self._picture_data_factory.compute_data(
                        path=picture_path, current_timezone=timezone.utc
                    )

                    picture_data_list.append(picture_data)
                except PictureException as e:
                    self._logger.warning(
                        f"Failed to compute picture id for {picture_path}: {e}"
                    )

        self._logger.info(f"Found {len(picture_data_list)} to be analyzed for grouping")

        picture_group_list = self._group_creator_service.get_group_list(
            picture_list=picture_data_list
        )

        pictures_to_move: list[tuple[Path, Path]] = []

        for group in picture_group_list:
            pictures_to_move.extend(group.list_pictures_to_move())

        self._logger.info(
            f"Found {len(pictures_to_move)} pictures that need to be moved"
        )

        for picture in pictures_to_move:
            self._file_tools.move_file(origin_path=picture[0], target_path=picture[1])

        self._logger.info("Grouping completed")


def group_use_case_factory(hours_btw_pictures: int) -> GroupUseCase:
    picture_data_factory = PictureDataFactory()
    file_tools = FileTools()

    group_creator_service = GroupCreatorService(hours_btw_picture=hours_btw_pictures)

    return GroupUseCase(
        file_tools=file_tools,
        picture_data_factory=picture_data_factory,
        group_creator_service=group_creator_service,
    )
