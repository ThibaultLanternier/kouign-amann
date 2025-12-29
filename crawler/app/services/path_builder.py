from pathlib import Path

from app.entities.picture_data import iPictureData
from app.entities.picture_heap import iPictureHeap


class LocalFilePathBuilderService:
    def __init__(
        self, root_folder: Path, sharded_folders_path: dict[int, Path]
    ) -> None:
        self._root_folder = root_folder
        self._sharded_folders_path = sharded_folders_path

    def _default_description(self, heap: iPictureHeap) -> str:
        return f"<EVENT DESCRIPTION {heap.get_start_date().timestamp()}>"

    def _get_root_folder(self, reference_year: int) -> Path:
        if reference_year in self._sharded_folders_path:
            return self._sharded_folders_path[reference_year]
        else:
            return self._root_folder

    def _get_folder_path(self, data: iPictureData, heap: iPictureHeap | None) -> Path:
        reference_year = data.get_creation_date().year
        parent_folder = Path("NOT_GROUPED")

        if heap is not None:
            reference_year = heap.get_start_date().year

            heap_date = heap.get_start_date().date()

            if heap.get_description() is None:
                parent_folder = Path(
                    f"{heap_date} {self._default_description(heap=heap)}"
                )
            else:
                parent_folder = Path(f"{heap_date} {heap.get_description()}")

        year_folder = self._get_root_folder(reference_year) / Path(str(reference_year))

        return year_folder / parent_folder

    def _get_file_name(self, data: iPictureData) -> Path:
        file_name = f"{int(data.get_creation_date().timestamp())}-{data.get_hash()}"

        if data.is_group_break():
            file_name = f"{file_name}-x"

        if data.is_selected():
            file_name = f"0-{file_name}"

        return Path(f"{file_name}.jpg")

    def build_path(self, data: iPictureData, heap: iPictureHeap | None = None) -> Path:
        folder_path = self._get_folder_path(data=data, heap=heap)

        file_name = self._get_file_name(data)

        return folder_path / file_name
