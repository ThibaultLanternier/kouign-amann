from app.storage.basic import AbstractStorage
from app.models.backup import StorageConfig, StorageType
from app.controllers.backup import AbstractStorageConfigProvider
from typing import Dict, Callable

from app.storage.aws_s3 import AWS_S3_factory
from app.storage.google_photos import GOOGLE_PHOTOS_FACTORY


class StorageFactoryException(Exception):
    pass


class StorageFactory:
    def __init__(self, storage_config_provider: AbstractStorageConfigProvider):
        self._config_provider = storage_config_provider
        self._storages: Dict[str, AbstractStorage] = {}
        self._factories: Dict[
            StorageType, Callable[[StorageConfig], AbstractStorage]
        ] = {
            StorageType.AWS_S3: AWS_S3_factory,
            StorageType.GOOGLE_PHOTOS: GOOGLE_PHOTOS_FACTORY
        }

    def create_from_id(self, storage_id: str) -> AbstractStorage:
        if self._storages.get(storage_id) is None:
            config = self._config_provider.get_storage_config(storage_id=storage_id)

            factory = self._factories.get(config.type)

            if factory is None:
                raise StorageFactoryException(
                    f"No Factory available for storage of type {config.type}"
                )

            self._storages[storage_id] = factory(config)

        return self._storages[storage_id]
