from cmath import pi
import logging
from datetime import datetime, timedelta
from typing import List, Tuple

import requests

from app.models.picture import PictureData, DictFactory
from app.tools.metrics import MetricRecorder

from dataclasses import asdict


class RecorderException(Exception):
    pass


class PictureRESTRecorder:
    def __init__(self, base_url: str):
        self.step_list: List[Tuple[str, timedelta]] = []

        self.base_url = base_url
        self.logger = logging.getLogger("app.recorder")

        self.logger.debug(f"Start PictureRESTRecorder with url {self.base_url}")

    def _record_info(self, picture_data: PictureData) -> bool:
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

    def _record_file(
        self, picture_data: PictureData, crawl_time: datetime, crawler_id: str
    ) -> bool:
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

    def record(
        self, picture_data: PictureData, crawl_time: datetime, crawler_id: str
    ) -> bool:
        self.record_metric = MetricRecorder(measurement_name="picture_record")
        self.record_metric.set_hash(picture_data.hash)

        try:
            if picture_data.thumbnail is not None:
                self._record_info(picture_data)
                self.record_metric.add_step("recording_thumbnail")

            self._record_file(picture_data, crawl_time, crawler_id)
            self.record_metric.add_step("recording_file_location")
            return True

        except RecorderException as e:
            self.logger.exception(e)
            return False

    def picture_already_exists(self, picture_hash: str):
        self.picture_exists_metric = MetricRecorder(measurement_name="picture_check")
        self.picture_exists_metric.set_hash(picture_hash)
        response = requests.get(f"{self.base_url}/picture/exists/{picture_hash}")
        self.picture_exists_metric.add_step("checking_picture_exists")

        return response.status_code == 200
