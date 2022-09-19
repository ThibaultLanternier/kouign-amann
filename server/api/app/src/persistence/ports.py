from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Union

from src.app.models import (BackupRequest, GoogleAccessToken, GoogleRefreshToken, Picture,
                            PictureCount)


class CredentialsPersistencePort(ABC):
    @abstractmethod
    def record_refresh_token(self, refresh_token: GoogleRefreshToken):
        pass

    @abstractmethod
    def get_refresh_token(self) -> GoogleRefreshToken:
        pass

    @abstractmethod
    def record_access_token(self, creds: GoogleAccessToken):
        pass

    @abstractmethod
    def get_access_token(self) -> GoogleAccessToken:
        pass

    @abstractmethod
    def get_current_state(self) -> str:
        pass


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
