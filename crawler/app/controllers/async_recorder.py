from abc import ABC, abstractmethod
import logging

from typing import Callable
from aiohttp import ClientSession

from app.models.picture import PictureFile, PictureInfo
from app.models.shared import DictFactory

from dataclasses import asdict

from app.tools.exceptions import RecorderInfoException
from app.tools.exceptions import RecorderFileException


class iAsyncRecorder(ABC):
    @abstractmethod
    async def record_info(self, info: PictureInfo, hash: str) -> bool:
        pass

    @abstractmethod
    async def record_file(self, file: PictureFile, hash: str) -> bool:
        pass

    @abstractmethod
    async def check_picture_exists(self, hash: str) -> bool:
        pass

    @abstractmethod
    async def close_session(self):
        pass


class AsyncRecorder(iAsyncRecorder):
    def __init__(
        self,
        base_url: str,
        client_session_ctor: Callable[[], ClientSession] = ClientSession,
    ) -> None:
        self._base_url = base_url
        self._logger = logging.getLogger("app.async_recorder")
        self._client_session_ctor = client_session_ctor

    async def _get_session(self):
        if not hasattr(self, "_session"):
            self._session = self._client_session_ctor()

        return self._session

    async def close_session(self):
        if hasattr(self, "_session"):
            await self._session.close()

    async def record_info(self, info: PictureInfo, hash: str) -> bool:
        session = await self._get_session()
        response = await session.post(
            f"{self._base_url}/picture/{hash}",
            json=asdict(info, dict_factory=DictFactory),
        )

        if response.status == 201:
            return True
        else:
            content = await response.text()
            raise RecorderInfoException(hash, response.status, content)

    async def record_file(self, file: PictureFile, hash: str) -> bool:
        session = await self._get_session()
        response = await session.put(
            f"{self._base_url}/picture/file/{hash}",
            json=asdict(file, dict_factory=DictFactory),
        )

        if response.status == 201:
            return True
        else:
            content = await response.text()
            raise RecorderFileException(hash, response.status, content)

    async def check_picture_exists(self, hash: str) -> bool:
        session = await self._get_session()
        response = await session.get(f"{self._base_url}/picture/exists/{hash}")

        return response.status == 200
