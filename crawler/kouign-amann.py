from datetime import timezone
from typing import Union
from uuid import uuid4
import click
import logging
import configparser

from pathlib import Path

from app.tools.logger import init_console_log, init_file_log
from app.tools.config_file import ConfigFileManager

from app.use_cases.backup import backup_use_case_factory
from app.use_cases.group import group_use_case_factory
from app.use_cases.rename import rename_use_case_factory
from app.use_cases.check import check_use_case_factory

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
    "--delta", help="Time difference between two group of pictures in hours", default=36
)
@click.option(
    "--path",
    help="Group only a specific path",
    default=None,
    type=click.Path(exists=True),
)
@click.option("--debug", help="Writes debug log to file", is_flag=True, default=False)
@click.option(
    "--group_size", help="Minimum number of pictures for a group", default=10, type=int
)
def group(delta: int, path: Union[str, None], debug: bool, group_size: int):
    """
    (NEW) Group pictures event
    """
    config = configparser.ConfigParser()
    config.read(ConfigFileManager().config_file_path)

    backup_folder_path = Path(config["backup"]["path"])

    if debug:
        log_file_path = (
            backup_folder_path / Path("logs") / Path(f"group-{uuid4().hex}.log")
        )
        logger.info(f"Debug mode enabled, writing log to file {log_file_path}")
        init_file_log(log_file=log_file_path)

    if path is None:
        folder_path_to_group = backup_folder_path
    else:
        logger.warning(f"Grouping only pictures in {path}")
        folder_path_to_group = Path(path)

    group_use_case = group_use_case_factory(
        hours_btw_pictures=delta, minimun_group_size=group_size
    )

    pictures_list = group_use_case.list_pictures(
        root_path=folder_path_to_group,
    )
    group_use_case.group(picture_list=pictures_list)


@cli.command()
@click.option(
    "--dry_run",
    help="Does not actually rename the folders",
    default=False,
    is_flag=True,
)
@click.option(
    "--sub_folder",
    default=None,
    help="Specific sub folder to rename DEBUG ONLY",
    type=click.Path(exists=True),
)
def rename(dry_run: bool, sub_folder: Union[str, None] = None):
    """
    !! EXPERIMENTAL FEATURE !! Try to rename new event folders based on historical path
    """
    config = configparser.ConfigParser()
    config.read(ConfigFileManager().config_file_path)

    backup_folder_path = Path(config["backup"]["path"])

    rename_use_case = rename_use_case_factory(backup_folder_path=backup_folder_path)

    verbose_mode = sub_folder is not None

    if sub_folder is not None:
        picture_path_list = rename_use_case.list_pictures(
            root_path=Path(sub_folder),  # type: ignore
        )
        logger.warning(f"Try to rename only sub folder {sub_folder}")
    else:
        picture_path_list = rename_use_case.list_pictures(
            root_path=backup_folder_path,
        )

    rename_use_case.rename_folders(
        picture_path_list=picture_path_list, dry_run=dry_run, verbose=verbose_mode
    )


@cli.command()
@click.argument("check_path", type=click.Path(exists=True))
def check(check_path: str):
    """
    Check all pictures in check_path have already been backed up.
    """
    config = configparser.ConfigParser()
    config.read(ConfigFileManager().config_file_path)

    backup_folder_path = Path(config["backup"]["path"])

    check_use_case = check_use_case_factory()

    backup_list = check_use_case.list_pictures(root_path=backup_folder_path)

    picture_list = check_use_case.list_pictures(root_path=Path(check_path))

    not_in_backup_count = check_use_case.check_pictures(
        backup_list=backup_list,
        picture_list=picture_list,
        current_timezone=timezone.utc,
    )

    if not_in_backup_count > 0:
        logger.error(f"{not_in_backup_count} pictures have not been backed up")
    else:
        logger.info("All pictures have been backed up")


if __name__ == "__main__":
    cli()
