import json
import logging
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

logger = logging.getLogger("app.data_store")

T = TypeVar("T", bound=BaseModel)


class DataStore(Generic[T]):
    def __init__(self, output_directory: Path) -> None:
        self._output_directory = Path(output_directory)
        self._output_directory.mkdir(parents=True, exist_ok=True)

    def save_data(self, data: T, identifier: str) -> None:
        filepath = self._output_directory / f"{identifier}.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data.model_dump(), f, indent=2, ensure_ascii=False)

        logger.info(f"Data saved to {filepath}")

    def load_data(self, identifier: str, model_class: type[T]) -> T:
        filepath = self._output_directory / f"{identifier}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"No data found for identifier: {identifier}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return model_class.model_validate(data)
