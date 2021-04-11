import logging
from datetime import datetime, timedelta
from typing import List, Tuple

import requests

from app.models.picture import PictureData, DictFactory

from dataclasses import asdict


class RecorderException(Exception):
    pass


class PictureRESTRecorder:
    def __init__(self, base_url: str):
        self.__reset_reference_time()

        self.step_list: List[Tuple[str, timedelta]] = []

        self.base_url = base_url
        self.logger = logging.getLogger("app.recorder")

        self.logger.info(f"Start PictureRESTRecorder with url {self.base_url}")

        self.__record_step_duration("init")

    def __record_step_duration(self, step_name: str):
        new_reference_time = datetime.now()

        self.step_list.append((step_name, new_reference_time - self.__reference_time))
        self.__reference_time: datetime = new_reference_time

    def __reset_reference_time(self):
        self.__reference_time = datetime.now()

    def _record_info(self, picture_data: PictureData) -> bool:
        self.__reset_reference_time()

        response = requests.post(
            f"{self.base_url}/picture/{picture_data.hash}",
            json=asdict(picture_data.get_picture_info(), dict_factory=DictFactory),
        )

        if response.status_code == 201:
            self.logger.debug(f"New picture {picture_data.hash} successfully recorded")
            return True
        else:
            raise RecorderException(
                "Info recording : %s %s with %s",
                response.status_code,
                response.content,
                picture_data.hash,
            )

        self.__record_step_duration("record_picture_info")

    def _record_file(
        self, picture_data: PictureData, crawl_time: datetime, crawler_id: str
    ) -> bool:
        self.__reset_reference_time()

        response = requests.put(
            f"{self.base_url}/picture/file/{picture_data.hash}",
            json=asdict(
                picture_data.get_picture_file(
                    current_time=crawl_time, crawler_id=crawler_id
                ),
                dict_factory=DictFactory,
            ),
        )

        if response.status_code == 201:
            self.logger.debug(
                f"New picture file {picture_data.hash} successfully recorded"
            )
            return True
        else:
            raise RecorderException(
                "File recording : %s %s with %s",
                response.status_code,
                response.content,
                picture_data.hash,
            )

        self.__record_step_duration("record_picture_file")

    def record(
        self, picture_data: PictureData, crawl_time: datetime, crawler_id: str
    ) -> bool:
        try:
            if picture_data.thumbnail is not None:
                self._record_info(picture_data)

            self._record_file(picture_data, crawl_time, crawler_id)
            return True

        except RecorderException as e:
            self.logger.exception(e)
            return False

    def picture_already_exists(self, picture_hash: str):
        self.__reset_reference_time()

        response = requests.get(f"{self.base_url}/picture/exists/{picture_hash}")

        self.__record_step_duration("check_already_exists")
        return response.status_code == 200
