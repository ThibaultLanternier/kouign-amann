import json
from typing import Dict, List

from src.app.models import StorageConfig


class ConfigManager:
    def __init__(self, config_file: str) -> None:
        with open(config_file, "r") as config_file:
            self._config = json.load(config_file)

    def storage_config_list(self) -> List[Dict]:
        if "storage_list" not in self._config:
            raise Exception("missing storage_list key in config")

        storage_list = self._config.get("storage_list")

        if not isinstance(storage_list, list):
            raise Exception("storage_list is not a list")

        output = []

        for storage in storage_list:
            output.append(StorageConfig(**storage))

        return output
