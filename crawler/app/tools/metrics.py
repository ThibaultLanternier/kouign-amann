from influxdb_client import Point
from datetime import datetime

def test_2():
    p = Point("record")

    p.tag("type","new")
    p.field("temps",456)
    p.time(datetime.datetime.now())

    return p.to_line_protocol()

class MetricRecorder:
    def __init__(self, measurement_name: str, current_datetime: datetime = None) -> None:
        self.__p = Point(measurement_name)

        self.__last_timestamp = datetime.now() if current_datetime is None else current_datetime

    def add_step(self, name: str, current_datetime: datetime = None) -> None:
        current_datetime = datetime.now() if current_datetime is None else current_datetime

        step_duration = (current_datetime - self.__last_timestamp).microseconds * 1000

        self.__p.field(name, step_duration)
        self.__last_timestamp = current_datetime

    def add_tag(self, name: str, value: str) -> None:
        self.__p.tag(name, value)

    def set_hash(self, hash: str) -> None:
        self.__p.tag("hash", hash)

    def get_steps(self) -> Point:
        return self.__p._fields

    def get_line(self, current_datetime: datetime = None) -> str:
        if current_datetime is None:
            current_datetime = datetime.now()

        self.__p.time(current_datetime)

        return self.__p.to_line_protocol()
