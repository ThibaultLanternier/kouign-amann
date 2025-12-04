import configparser
import logging
from pathlib import Path
from platformdirs import user_config_dir


class ConfigFileException(Exception):
    pass


class ConfigFileManager:
    config_file_path: Path

    def __init__(self, force_config_path: Path | None = None) -> None:
        if force_config_path is not None:
            self.config_file_path = force_config_path
        else:
            self.config_file_path = Path(user_config_dir("kouign-amann")) / Path(
                "config.ini"
            )

        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger("app.configmanager")
        self._logger.info(f"Config file path: {self.config_file_path}")

        self._config_parser: configparser.ConfigParser | None = None

    def get_backup_folder_path(self) -> Path:
        if not self._config_parser:
            self._config_parser = configparser.ConfigParser()
            self._config_parser.read(self.config_file_path)

        return Path(self._config_parser["backup"]["path"])

    def set_backup_folder_path(
        self, backup_folder_path: Path, force: bool = False
    ) -> None:
        if self.config_file_path.is_file() and not force:
            raise ConfigFileException(
                "config.ini already exists please delete it first or use --force"
            )

        new_config = configparser.ConfigParser()

        new_config["backup"] = {}
        new_config["backup"]["path"] = str(backup_folder_path)

        with open(self.config_file_path, "w") as config_file:
            new_config.write(config_file)

    def get_sharded_backup_folder_path(self) -> dict[int, Path]:
        if not self._config_parser:
            self._config_parser = configparser.ConfigParser()
            self._config_parser.read(self.config_file_path)

        sharded_folder_path: dict[int, Path] = {}

        if "sharding" in self._config_parser:
            for key in self._config_parser["sharding"]:
                sharded_folder_path[int(key)] = Path(
                    self._config_parser["sharding"][key]
                )

        return sharded_folder_path
