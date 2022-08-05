from enum import Enum
from typing import Tuple, Any
from datetime import datetime
from app.tools.date import DateTimeConverter


class DictFactory(dict):
    def __init__(self, data):
        super().__init__(
            self._format_value(key=x[0], value=x[1]) for x in data
        )  # noqa: E501

    def _format_value(self, key: str, value: Any) -> Tuple[str, Any]:
        if isinstance(value, datetime):
            value = DateTimeConverter().to_string(value)

        if isinstance(value, Enum):
            value = value.name

        return (key, value)
