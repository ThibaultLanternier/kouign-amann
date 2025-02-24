from datetime import datetime
from pathlib import Path
from typing import Dict
from app.controllers.async_recorder import iAsyncRecorder
from app.models.picture import PictureFile, PictureInfo
import os


class AsyncFileRecorder(iAsyncRecorder):

    def __init__(self, base_file_path: Path):
        super().__init__()
        self._base_file_path = base_file_path
        self._creation_time: Dict[str, datetime] = {}
        self._file_dict = {}

        file_list = [x for x in self._base_file_path.glob("**/*.jpg")]

        for file in file_list:
            full_file_name = file.name.split(".")[0]
            timpstamp, hash = full_file_name.split("-")
            
            self._file_dict[hash] = file

    def __get_file_path(self, hash: str, creation_date: datetime):
        integer_timestamp = int(creation_date.timestamp())

        return (
            self._base_file_path
            / Path(f"{creation_date.year}")
            / Path(f"{creation_date.year}-{creation_date.month}-{creation_date.day}")
            / Path(f"{integer_timestamp}-{hash}.jpg")
        )

    async def record_info(self, info: PictureInfo, hash: str) -> bool:
        self._creation_time[hash] = info.creation_time

        return True

    async def record_file(self, file: PictureFile, hash: str) -> bool:
        if hash not in self._creation_time:
            raise Exception("Missing creation time")

        creation_time = self._creation_time[hash]

        with open(file.picture_path, "rb") as picture_file:
            new_file_path = self.__get_file_path(hash, creation_date=creation_time)

            os.makedirs(new_file_path.parent, exist_ok=True)
            with open(new_file_path, "wb+") as new_picture_file:
                new_picture_file.write(picture_file.read())
                os.utime(
                    new_file_path,
                    (creation_time.timestamp(), creation_time.timestamp()),
                )
            self._file_dict[hash] = new_file_path

        return True

    async def check_picture_exists(self, hash: str) -> bool:
        return hash in self._file_dict

    async def close_session(self):
        pass
