from abc import ABC, abstractmethod

from app.models.backup import StorageConfig

class AbstractStorageConfigProvider(ABC):
    @abstractmethod
    def get_storage_config(self, storage_id: str) -> StorageConfig:
        pass