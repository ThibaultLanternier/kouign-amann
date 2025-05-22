from uuid import uuid4
import click
import logging
import configparser

from pathlib import Path

from app.tools.logger import init_console_log, init_file_log
from app.tools.config_file import ConfigFileManager

from app.use_cases.backup import backup_use_case_factory
from app.use_cases.group import group_use_case_factory

init_console_log()

logger = logging.getLogger("app.crawl")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("backup_path", type=click.Path(exists=True))
@click.option("--force", default=False, help="Force refresh of the config file")
def init(backup_path: str, force: bool):
    """
    record backup_path in config.ini
    """
    config_file_path = ConfigFileManager().config_file_path

    if config_file_path.is_file() and not force:
        raise Exception(
            "config.ini already exists please delete it first or use --force"
        )

    new_config = configparser.ConfigParser()

    new_config["backup"] = {}
    new_config["backup"]["path"] = backup_path

    with open(config_file_path, "w") as config_file:
        new_config.write(config_file)


@cli.command()
@click.option(
    "--strict",
    default=False,
    help="Does not rely on local file store only on perception hash",
    is_flag=True,
)
@click.option("--debug", help="Writes debug log to file", is_flag=True)
@click.argument("target_path", type=click.Path(exists=True))
def backup(target_path: str, strict: bool, debug: str):
    """
    (NEW) Copy new pictures found in target directory to backup directory
    """
    print(debug)
    print(strict)
    config = configparser.ConfigParser()
    config.read(ConfigFileManager().config_file_path)

    backup_folder_path = Path(config["backup"]["path"])

    if debug:
        log_file_path = (
            backup_folder_path / Path("logs") / Path(f"backup-{uuid4().hex}.log")
        )
        logger.info(f"Debug mode enabled, writing log to file {log_file_path}")
        init_file_log(log_file=log_file_path)

    target_folder_path = Path(target_path)

    backup_use_case = backup_use_case_factory(backup_folder_path=backup_folder_path)

    file_list = backup_use_case.list_pictures(root_path=target_folder_path)

    backup_use_case.backup(
        picture_list_to_backup=file_list,
        strict_mode=strict,
    )


@cli.command()
@click.option(
    "--delta", help="Time difference between two group of pictures in hours", default=24
)
def group(delta: int):
    """
    (NEW) Group pictures event
    """
    config = configparser.ConfigParser()
    config.read(ConfigFileManager().config_file_path)

    backup_folder_path = Path(config["backup"]["path"])

    group_use_case = group_use_case_factory(
        backup_folder_path=backup_folder_path,
        hours_btw_pictures=delta,
    )

    pictures_list = group_use_case.list_pictures(
        root_path=backup_folder_path,
    )
    group_use_case.group(picture_list=pictures_list)

if __name__ == "__main__":
    cli()
