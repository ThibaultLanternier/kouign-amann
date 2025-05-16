from pathlib import Path
from progressbar import ProgressBar

from app.entities.picture_data import (
    NotStandardFileNameException,
    PictureData,
    iPictureData,
)
from app.repositories.picture_data import PictureDataRepository
from app.services.file import FileService, FileTools, iFileService
from app.services.picture_id import (
    PictureIdComputeException,
    PictureIdService,
    iPictureIdService,
)
from app.use_cases.backup import baseUseCase
from app.services.group_creator import GroupCreatorService, iGroupCreatorService


class GroupUseCase(baseUseCase):
    def __init__(
        self,
        file_service: iFileService,
        picture_id_service: iPictureIdService,
        group_creator_service: iGroupCreatorService,
    ):
        super().__init__(file_service=file_service)
        self._group_creator_service = group_creator_service
        self._picture_id_service = picture_id_service

    def group(self, picture_list: list[Path]):
        picture_data_list: list[iPictureData] = []

        for picture_path in picture_list:
            try:
                picture_data = PictureData.from_standard_path(
                    standard_path=picture_path
                )
                picture_data_list.append(picture_data)
            except NotStandardFileNameException as e:
                self._logger.warning(
                    f"Found non standard path for picture {picture_path}: {e}"
                )
                try:
                    picture_data = self._picture_id_service.compute_id(
                        picture_path=picture_path
                    )

                    picture_data_list.append(picture_data)
                except PictureIdComputeException as e:
                    self._logger.warning(
                        f"Failed to compute picture id for {picture_path}: {e}"
                    )

        self._logger.info(f"Found {len(picture_data_list)} to be analyzed for grouping")
        picture_group = GroupCreatorService()
        picture_group_list = picture_group.get_group_list(
            picture_list=picture_data_list
        )

        pictures_to_move: list[tuple[Path, Path]] = []

        for group in picture_group_list:
            pictures_to_move.extend(group.list_pictures_to_move())

        self._logger.info(
            f"Found {len(pictures_to_move)} pictures that need to be moved"
        )

        progress_bar = ProgressBar()
        progress_bar.start(max_value=len(pictures_to_move))
        progress_bar_count = 0

        for picture in pictures_to_move:
            FileTools.move_file(origin_path=picture[0], target_path=picture[1])
            progress_bar_count = progress_bar_count + 1
            progress_bar.update(progress_bar_count)


def group_use_case_factory(
    backup_folder_path: Path, hours_btw_pictures: int
) -> GroupUseCase:
    picture_data_repo = PictureDataRepository(
        cache_file_path=Path(f"{backup_folder_path}/cache.jsonl")
    )

    file_service = FileService(backup_folder_path=backup_folder_path)
    picture_id_service = PictureIdService(picture_data_repo=picture_data_repo)

    group_creator_service = GroupCreatorService(hours_btw_picture=hours_btw_pictures)

    return GroupUseCase(
        file_service=file_service,
        picture_id_service=picture_id_service,
        group_creator_service=group_creator_service,
    )
