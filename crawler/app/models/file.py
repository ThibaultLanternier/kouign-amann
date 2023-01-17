from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class LocalFile:
    path: Path
    last_modified: datetime
