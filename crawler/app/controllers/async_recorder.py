from abc import ABC, abstractmethod
from datetime import datetime

from pathlib import Path


class iAsyncRecorder(ABC):
    @abstractmethod
    async def record_file(
        self, picture_path: Path, hash: str, creation_time: datetime
    ) -> bool:
        pass

    @abstractmethod
    async def check_picture_exists(self, hash: str) -> bool:
        pass
