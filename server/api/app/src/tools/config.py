import json
from typing import Dict, List

from src.app.models import StorageConfig, StorageType


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

    def get_google_photos_config_file(storage_list: List[StorageConfig]) -> str:
        google_photos_config = [storage for storage in storage_list if storage.type == StorageType.GOOGLE_PHOTOS]

        if len(google_photos_config) > 1:
            raise Exception("only one storage of type GOOGLE_PHOTOS allowed")

        if len(google_photos_config) == 0:
            return None

        return google_photos_config[0].config["config_file"]
