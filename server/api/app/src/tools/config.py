import json
from typing import List, Union

from marshmallow import Schema, fields

from src.app.models import StorageConfig, StorageType


class S3Config(Schema):
    key = fields.String(required=True)
    secret = fields.String(required=True)
    bucket = fields.String(required=True)


class GooglePhotosConfig(Schema):
    config_file = fields.String(required=True)
    token_url = fields.String(required=True)
    callback_url = fields.String(required=True)


class ConfigManager:
    def __init__(self, config_file_name: str) -> None:
        self._config_schema_list = {
            StorageType.GOOGLE_PHOTOS: GooglePhotosConfig,
            StorageType.AWS_S3: S3Config,
        }

        with open(config_file_name, "r") as config_file:
            self._config = json.load(config_file)

    def check_config(self, storage_config: StorageConfig):
        schema = self._config_schema_list[storage_config.type]
        schema().load(storage_config.config)

    def storage_config_list(self) -> List[StorageConfig]:
        if "storage_list" not in self._config:
            raise Exception("missing storage_list key in config")

        storage_list = self._config.get("storage_list")

        if not isinstance(storage_list, list):
            raise Exception("storage_list is not a list")

        output = []

        for storage in storage_list:
            storage_config = StorageConfig(**storage)
            self.check_config(storage_config=storage_config)

            output.append(StorageConfig(**storage))

        return output

    def get_storage_first_id_by_type(self, type: StorageType) -> Union[str, None]:
        config_list = [
            storage for storage in self.storage_config_list() if storage.type == type
        ]

        if len(config_list) == 0:
            return None

        return config_list[0].id

    @staticmethod
    def get_google_photos_config_file(
        storage_list: List[StorageConfig],
    ) -> Union[str, None]:
        google_photos_config = [
            storage
            for storage in storage_list
            if storage.type == StorageType.GOOGLE_PHOTOS
        ]

        if len(google_photos_config) > 1:
            raise Exception("only one storage of type GOOGLE_PHOTOS allowed")

        if len(google_photos_config) == 0:
            return None

        return google_photos_config[0].config["config_file"]
