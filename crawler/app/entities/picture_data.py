from abc import ABC, abstractmethod
from datetime import datetime


class iPictureData(ABC):
    @abstractmethod
    def get_creation_date(self) -> datetime:
        pass

    @abstractmethod
    def get_hash(self) -> str:
        pass

    @abstractmethod
    def is_group_break(self) -> bool:
        pass

    @abstractmethod
    def is_selected(self) -> bool:
        pass


class PictureData(iPictureData):
    def __init__(
        self,
        creation_date: datetime,
        hash: str,
        group_break: bool = False,
        is_selected: bool = False,
    ) -> None:
        self._creation_date = creation_date
        self._hash = hash
        self._group_break = group_break
        self._is_selected = is_selected

    def get_creation_date(self) -> datetime:
        return self._creation_date

    def get_hash(self) -> str:
        return self._hash

    def is_group_break(self) -> bool:
        return self._group_break

    def is_selected(self) -> bool:
        return self._is_selected
