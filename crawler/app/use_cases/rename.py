from datetime import timezone
from pathlib import Path
from app.use_cases.backup import baseUseCase
from app.repositories.picture_data import PictureDataRepository, iPictureDataRepository
from app.services.group_creator import GroupCreatorService, iGroupCreatorService
from app.entities.picture_data import iPictureData
from app.factories.picture_data import PictureDataFactory, iPictureDataFactory
from app.tools.file import FileTools, iFileTools


class RenameUseCase(baseUseCase):
    def __init__(
        self,
        file_tools: iFileTools,
        picture_data_factory: iPictureDataFactory,
        picture_repository: iPictureDataRepository,
        group_creator_service: iGroupCreatorService,
    ):
        super().__init__(
            file_tools=file_tools, picture_data_factory=picture_data_factory
        )
        self._picture_data_repository = picture_repository
        self._group_creator_service = group_creator_service

    def rename_folders(
        self, picture_path_list: list[Path], dry_run=False, verbose=False
    ) -> None:
        self._logger.info(
            f"Extracting picture data from {len(picture_path_list)} pictures"
        )

        if verbose:
            self._logger.info("VERBOSE MODE ENABLED, showing details of each rename")

        picture_data_list: list[iPictureData] = [
            self._picture_data_factory.from_standard_path(
                picture_path, current_timezone=timezone.utc
            )
            for picture_path in picture_path_list
        ]
        picture_data_list = [
            picture_data
            for picture_data in picture_data_list
            if picture_data is not None
        ]

        self._logger.info(
            f"Found {len(picture_data_list)} pictures with valid data for renaming"
        )
        group_list = self._group_creator_service.get_group_list_from_folders(
            picture_data_list
        )

        self._logger.info(f"Found {len(group_list)} directory to rename")

        for group in group_list:
            if group.is_editable():
                new_folder_name = group.get_new_folder_name(
                    picture_repository=self._picture_data_repository,
                    verbose=verbose,
                )
                folder_path = group.get_folder_path()

                if new_folder_name != folder_path:
                    self._logger.info(
                        f"Folder {folder_path} could be renamed {new_folder_name}"
                    )
                    if not dry_run:
                        self._file_tools.rename_file(
                            origin_folder_path=folder_path,
                            new_folder_path=new_folder_name,
                        )
                        self._logger.info(f"Renamed {folder_path} to {new_folder_name}")
                self._logger.warning(
                    f"No data found in history to rename {folder_path}, skipping"
                )
            else:
                self._logger.debug(
                    f"Group {group.get_folder_path()} is not editable, skipping rename"
                )


def rename_use_case_factory(backup_folder_path: Path) -> RenameUseCase:
    picture_data_repo = PictureDataRepository(
        cache_file_path=Path(f"{backup_folder_path}/cache.jsonl")
    )

    picture_data_factory = PictureDataFactory()
    file_tools = FileTools()

    group_creator_service = GroupCreatorService()

    return RenameUseCase(
        file_tools=file_tools,
        picture_data_factory=picture_data_factory,
        picture_repository=picture_data_repo,
        group_creator_service=group_creator_service,
    )
