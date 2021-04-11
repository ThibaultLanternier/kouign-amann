from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Union

from src.app.models import BackupRequest, Picture, PictureCount


class PersistencePort(ABC):
    @abstractmethod
    def get_picture(self, hash: str) -> Union[Picture, None]:
        pass

    @abstractmethod
    def list_pictures(self, start: datetime, end: datetime) -> List[Picture]:
        pass

    @abstractmethod
    def list_recently_updated_pictures(self, duration: timedelta) -> List[Picture]:
        pass

    @abstractmethod
    def record_picture(self, picture: Picture) -> None:
        pass

    @abstractmethod
    def count_picture(self) -> List[PictureCount]:
        pass

    @abstractmethod
    def get_pending_backup_request(
        self, crawler_id: str, limit: int
    ) -> List[BackupRequest]:
        pass
