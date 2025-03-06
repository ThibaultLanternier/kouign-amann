from pathlib import Path
from platformdirs import user_config_dir 

class ConfigFileManager:
    config_file_path: Path

    def __init__(self):
        self.config_file_path = Path(user_config_dir('kouign-amann')) / Path('config.ini')
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)