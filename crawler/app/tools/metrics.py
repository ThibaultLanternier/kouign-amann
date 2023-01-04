from influxdb_client import Point
from datetime import datetime, timezone
from time import time_ns
from typing import Union


class MetricRecorder:
    def __init__(self, measurement_name: str, now_ns: Union[int, None] = None) -> None:
        self.__p = Point(measurement_name)

        self.__last_timestamp_ns = (
            self.__get_now_timestamp_ns() if now_ns is None else now_ns
        )

    @staticmethod
    def get_datetime_from_ns_timestamp(timestamp_ns: int) -> datetime:
        timestamp_s = timestamp_ns / 10e9
        return datetime.fromtimestamp(timestamp_s, tz=timezone.utc)

    def __get_now_timestamp_ns(self) -> int:
        return int(time_ns())

    def add_step(self, name: str, now_ns: Union[int, None] = None) -> None:
        now_ns = self.__get_now_timestamp_ns() if now_ns is None else now_ns

        step_duration = now_ns - self.__last_timestamp_ns

        self.__p.field(name, step_duration)
        self.__last_timestamp_ns = now_ns

    def add_tag(self, name: str, value: str) -> None:
        self.__p.tag(name, value)

    def set_hash(self, hash: str) -> None:
        self.__p.tag("hash", hash)

    def get_steps(self) -> Point:
        return self.__p._fields

    def get_line(self, current_timestamp_ns: Union[int, None] = None) -> str:
        if current_timestamp_ns is None:
            current_timestamp_ns = self.__get_now_timestamp_ns()

        self.__p.time(current_timestamp_ns)

        return self.__p.to_line_protocol()
