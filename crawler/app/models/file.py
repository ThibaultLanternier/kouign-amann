import os

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class LocalFile:
    path: Path
    last_modified: datetime

    @classmethod
    def from_path(cls, path: Path):
        last_modified = datetime.fromtimestamp(os.path.getmtime(path))

        return LocalFile(path=path, last_modified=last_modified)
