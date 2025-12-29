from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from app.entities.picture_data import iPictureData


class PictureHeapException(Exception):
    pass


class HeapType(Enum):
    NOT_GROUPED = "NOT_GROUPED"
    OTHER = "OTHER"
    GROUPED = "GROUPED"


class iPictureHeap(ABC):
    @abstractmethod
    def get_description(self) -> str | None:
        pass

    @abstractmethod
    def get_start_date(self) -> datetime:
        pass

    @abstractmethod
    def get_end_date(self) -> datetime:
        pass

    @abstractmethod
    def get_picture_list(self) -> list[iPictureData]:
        pass

    @abstractmethod
    def get_type(self) -> HeapType:
        pass


class PictureHeap(iPictureHeap):
    def __init__(
        self,
        heap_type: HeapType,
        picture_list: list[iPictureData],
        description: str | None,
    ) -> None:
        self._picture_list = picture_list
        self._heap_type = heap_type

        self._ordered_picture_list = sorted(
            self._picture_list,
            key=lambda picture: picture.get_creation_date(),
        )
        self._description = description

    def get_description(self) -> str | None:
        return self._description

    def get_start_date(self) -> datetime:
        return self._ordered_picture_list[0].get_creation_date()

    def get_end_date(self) -> datetime:
        return self._ordered_picture_list[-1].get_creation_date()

    def get_picture_list(self) -> list[iPictureData]:
        return self._ordered_picture_list

    def get_type(self) -> HeapType:
        return self._heap_type
