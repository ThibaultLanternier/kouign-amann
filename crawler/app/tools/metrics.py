from influxdb_client import Point
from datetime import datetime, timezone, tzinfo
from time import time, time_ns

class MetricRecorder:
    def __init__(self, measurement_name: str, current_timestamp_ns: int = None) -> None:
        self.__p = Point(measurement_name)

        self.__last_timestamp_ns = self.__get_now_timestamp_ns() if current_timestamp_ns is None else current_timestamp_ns

    def get_datetime_from_ns_timestamp(timestamp_ns: int) -> datetime:
        timestamp_s = timestamp_ns / 10e9
        return datetime.fromtimestamp(timestamp_s, tz=timezone.utc)

    def __get_now_timestamp_ns(self) -> int:
        return int(time_ns())

    def add_step(self, name: str, current_timestamp_ns: datetime = None) -> None:
        current_timestamp_ns = self.__get_now_timestamp_ns() if current_timestamp_ns is None else current_timestamp_ns

        step_duration = current_timestamp_ns - self.__last_timestamp_ns

        self.__p.field(name, step_duration)
        self.__last_timestamp_ns = current_timestamp_ns

    def add_tag(self, name: str, value: str) -> None:
        self.__p.tag(name, value)

    def set_hash(self, hash: str) -> None:
        self.__p.tag("hash", hash)

    def get_steps(self) -> Point:
        return self.__p._fields

    def get_line(self, current_timestamp_ns: datetime = None) -> str:
        if current_timestamp_ns is None:
            current_timestamp_ns = self.__get_now_timestamp_ns()

        self.__p.time(current_timestamp_ns)

        return self.__p.to_line_protocol()
