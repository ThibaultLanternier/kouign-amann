import logging
import csv
import os

from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Iterator

import requests

from app.models.picture import PictureData
from app.models.shared import DictFactory
from app.models.file import LocalFile
from app.tools.metrics import MetricRecorder

from dataclasses import asdict
from pathlib import Path


class RecorderException(Exception):
    pass


class CrawlHistoryStore:
    def __init__(self, file_directory: Path = Path("")) -> None:
        self._directory_path = file_directory

    def _get_storage_file_list(self) -> List[Path]:
        return [path for path in self._directory_path.glob("*-localstore.csv")]

    def _get_file_name(self, worker_id: int):
        return self._directory_path / f"{worker_id}-localstore.csv"

    def _get_raw_data_list(self) -> Iterator[Tuple[str, str]]:
        for path in self._get_storage_file_list():
            with open(path, "r") as file:
                csv_file = csv.reader(file, delimiter=";")
                for csv_line in csv_file:
                    yield (csv_line[0], csv_line[1])

    def get_crawl_history(self) -> Dict[Path, LocalFile]:
        output: Dict[Path, LocalFile] = {}

        for data in self._get_raw_data_list():
            path = Path(data[0])
            last_modified = datetime.fromisoformat(data[1])

            local_file = LocalFile(path=path, last_modified=last_modified)

            if path not in output.keys():
                output[path] = local_file
            else:
                if output[path].last_modified < local_file.last_modified:
                    output[path] = local_file

        return output

    def add_file(self, path: Path, worker_id: int):
        last_modified_ts = os.path.getmtime(path)
        last_modified = datetime.fromtimestamp(last_modified_ts)

        with open(self._get_file_name(worker_id=worker_id), "a+") as f:
            csv_writer = csv.writer(f, delimiter=";")
            csv_writer.writerow([str(path), last_modified.isoformat()])

    def reset(self):
        for storage_file in self._get_storage_file_list():
            os.remove(storage_file)


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
                self.record_metric.add_tag("picture_type", "new")
            else:
                self.record_metric.add_tag("picture_type", "existing")

            self._record_file(picture_data, crawl_time, crawler_id)
            self.record_metric.add_step("recording_file_location")
            return True

        except RecorderException as e:
            self.logger.exception(e)
            return False

    def picture_already_exists(self, picture_hash: str):
        response = requests.get(f"{self.base_url}/picture/exists/{picture_hash}")

        return response.status_code == 200
