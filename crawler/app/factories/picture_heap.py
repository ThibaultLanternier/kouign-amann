from pathlib import Path
import re
from app.entities.picture_data import iPictureData
from app.entities.picture_heap import (
    HeapType,
    PictureHeap,
    PictureHeapException,
    iPictureHeap,
)


class PictureHeapFactory:
    def _get_type_from_folder_name(self, parent_folder_path: Path) -> HeapType:
        parent_folder_name = parent_folder_path.name

        if parent_folder_name == "NOT_GROUPED":
            return HeapType.NOT_GROUPED
        elif re.match(r"^\d{4} OTHER$", parent_folder_name):
            return HeapType.OTHER
        elif re.match(r"^\d{4}-\d{2}-\d{2}( .+)?$", parent_folder_name):
            return HeapType.GROUPED
        else:
            # If folder name is malformed consider it as NOT_GROUPED
            return HeapType.NOT_GROUPED

    def _get_description_from_folder_name(self, parent_folder_path: Path) -> str | None:
        parent_folder_name = parent_folder_path.name
        match = re.match(r"^\d{4}-\d{2}-\d{2} (.+)$", parent_folder_name)

        if match:
            description = match.group(1)

            if description.find("<EVENT DESCRIPTION") != -1:
                return None
            else:
                return description
        else:
            raise PictureHeapException("Folder name does not contain a description")

    def from_folder_path(
        self, folder_path: Path, picture_list: list[iPictureData]
    ) -> iPictureHeap:
        heap_type = self._get_type_from_folder_name(folder_path)

        description: str | None = None

        if heap_type == HeapType.GROUPED:
            description = self._get_description_from_folder_name(folder_path)

        return PictureHeap(
            heap_type=heap_type,
            picture_list=picture_list,
            description=description,
        )
