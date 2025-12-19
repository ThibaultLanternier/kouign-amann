import logging
from pathlib import Path
from app.tools.file import FileTools, iFileTools


class ListPicturesUseCase:
    def __init__(self, file_tools: iFileTools):
        self._file_tools = file_tools
        self._logger = logging.getLogger("app.list_picture_case")

    def list_pictures(
        self, root_path: Path, folder_name_to_exclude: list[str] = []
    ) -> list[Path]:
        self._logger.info(f"Listing pictures in {root_path}")
        picture_list = self._file_tools.list_pictures(
            root_path_list=[root_path], folder_name_to_exclude=folder_name_to_exclude
        )
        self._logger.info(f"Found {len(picture_list)} pictures")

        return picture_list


def list_pictures_use_case_factory() -> ListPicturesUseCase:
    file_tools = FileTools()

    return ListPicturesUseCase(
        file_tools=file_tools,
    )
