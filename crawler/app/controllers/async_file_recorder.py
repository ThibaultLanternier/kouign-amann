from datetime import datetime
from pathlib import Path
from typing import Dict
from app.controllers.async_recorder import iAsyncRecorder
import os

from app.tools.path import PicturePath, PicturePathException, abstractPicturePath
from app.tools.path_manager import PicturePathManager


class AsyncFileRecorder(iAsyncRecorder):
    _path_manager: PicturePathManager

    def __init__(self, base_file_path: Path):
        super().__init__()
        self._base_file_path = base_file_path
        self._creation_time: Dict[str, datetime] = {}

        path_list = [x for x in self._base_file_path.glob("**/*.jpg")]

        picture_path_list: list[abstractPicturePath] = []

        for path in path_list:
            try:
                picture_path = PicturePath(path)
                picture_path_list.append(picture_path)
            except PicturePathException:
                pass

        self._path_manager = PicturePathManager(picture_path_list, self._base_file_path)

    def __get_file_path(self, hash: str, creation_date: datetime):
        integer_timestamp = int(creation_date.timestamp())

        return self._path_manager.get_folder_path(creation_date.date()) / Path(
            f"{integer_timestamp}-{hash}.jpg"
        )

    async def record_file(
        self, picture_path: Path, hash: str, creation_time: datetime
    ) -> bool:
        with open(picture_path, "rb") as picture_file:
            new_file_path = self.__get_file_path(hash=hash, creation_date=creation_time)

            os.makedirs(new_file_path.parent, exist_ok=True)
            with open(new_file_path, "wb+") as new_picture_file:
                new_picture_file.write(picture_file.read())
                os.utime(
                    new_file_path,
                    (creation_time.timestamp(), creation_time.timestamp()),
                )
            self._path_manager.add_picture_path(PicturePath(new_file_path))

        return True

    async def check_picture_exists(self, hash: str) -> bool:
        return self._path_manager.check_hash_exists(hash)
