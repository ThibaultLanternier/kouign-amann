from datetime import datetime, timezone

import pytz

MONGODB_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class DateTimeFormatException(Exception):
    pass


class DateTimeUtilities:
    def get_expiration_datetime(self, duration_s: int, now: datetime) -> datetime:
        raise NotImplementedError()


class DateTimeConverter:
    def from_string(self, input: str) -> datetime:
        unaware_datetime = datetime.strptime(input, MONGODB_ISO_FORMAT)

        return pytz.utc.localize(unaware_datetime)

    def to_string(self, input: datetime) -> str:
        return input.astimezone(timezone.utc).strftime(MONGODB_ISO_FORMAT)

    def is_timezone_aware(self, input: datetime) -> bool:
        return input.tzinfo is not None and input.tzinfo.utcoffset(input) is not None
