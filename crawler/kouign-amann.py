from datetime import timezone
from typing import Union
from uuid import uuid4
import click
import logging

from pathlib import Path

from app.tools.logger import init_console_log, init_file_log
from app.tools.config_file import ConfigFileManager

from app.use_cases.backup import backup_use_case_factory
from app.use_cases.group import group_use_case_factory
from app.use_cases.rename import rename_use_case_factory
from app.use_cases.check import check_use_case_factory

init_console_log()

logger = logging.getLogger("app.crawl")

config_manager = ConfigFileManager()

def enable_debug_log(action_name: str) -> None:
    backup_folder_path = config_manager.get_backup_folder_path()

    log_file_path = (
        backup_folder_path / Path("logs") / Path(f"{action_name}-{uuid4().hex}.log")
    )
    logger.info(f"Debug mode enabled, writing log to file {log_file_path}")
    
    init_file_log(log_file=log_file_path)

@click.group()
def cli():
    pass


@cli.command()
@click.argument("backup_path", type=click.Path(exists=True))
@click.option("--force", is_flag=True,default=False, help="Force refresh of the config file")
def init(backup_path: str, force: bool):
    """
    record backup_path in config.ini
    """
    config_manager.set_backup_folder_path(Path(backup_path), force=force)


@cli.command()
@click.option(
    "--strict",
    default=False,
    help="Does not rely on local file store only on perception hash",
    is_flag=True,
)
@click.option("--debug", help="Writes debug log to file", is_flag=True)
@click.option(
    "--exclude_folder",
    help="name of subfolder(s) that need to be excluded from backup",
    multiple=True,
)
@click.argument("target_path", type=click.Path(exists=True))
def backup(target_path: str, strict: bool, debug: str, exclude_folder: list[str]):
    """
    (NEW) Copy new pictures found in target directory to backup directory
    """
    backup_use_case = backup_use_case_factory(
        backup_folder_path=config_manager.get_backup_folder_path(),
        sharded_folder_path=config_manager.get_sharded_backup_folder_path()
    )

    if len(exclude_folder) > 0:
        for folder in exclude_folder:
            logger.info(f"Excluding pictures contained in folder {folder} from backup")

    if debug:
        enable_debug_log(action_name="backup")

    target_folder_path = Path(target_path)

    file_list = backup_use_case.list_pictures(
        root_path=target_folder_path, folder_name_to_exclude=exclude_folder
    )

    backup_use_case.backup(
        picture_list_to_backup=file_list,
        strict_mode=strict,
    )


@cli.command()
@click.option(
    "--delta", help="Time difference between two group of pictures in hours", default=36
)
@click.option("--debug", help="Writes debug log to file", is_flag=True, default=False)
@click.option(
    "--group_size", help="Minimum number of pictures for a group", default=10, type=int
)
@click.argument(
    "path",
    default=None,
    required=False,
    type=click.Path(exists=True),
)
def group(delta: int, debug: bool, group_size: int, path: Union[str, None]):
    """
    (NEW) Group all pictures located in path by event
    """
    if debug:
        enable_debug_log(action_name="group")

    if path is None:
        folder_path_to_group = config_manager.get_backup_folder_path()
        logger.warning(f"Grouping the whole backup folder {folder_path_to_group}")
    else:
        folder_path_to_group = Path(path)
        logger.warning(f"Grouping only pictures in {folder_path_to_group}")

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
@click.option("--verbose", help="Verbose mode", is_flag=True, default=False)
@click.argument(
    "path",
    default=None,
    type=click.Path(exists=True),
)
def rename(dry_run: bool, verbose: bool, path: Union[str, None] = None):
    """
    !! EXPERIMENTAL !! Try to rename new event folders in path based on historical path
    """
    if path is None:
        folder_path_to_rename = config_manager.get_backup_folder_path()
        logger.warning(f"Renaming the complete backup folder{folder_path_to_rename}")
    else:
        folder_path_to_rename = Path(path)
        logger.warning(f"Renaming folders only in {folder_path_to_rename}")

    rename_use_case = rename_use_case_factory(backup_folder_path=config_manager.get_backup_folder_path())
    
    picture_path_list = rename_use_case.list_pictures(
        root_path=folder_path_to_rename,
    )

    rename_use_case.rename_folders(
        picture_path_list=picture_path_list, dry_run=dry_run, verbose=verbose
    )


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def check(path: str):
    """
    Check all pictures in check_path have already been backed up.
    """
    backup_folder_path = config_manager.get_backup_folder_path()

    check_use_case = check_use_case_factory()

    backup_list = check_use_case.list_pictures(root_path=backup_folder_path)

    picture_list = check_use_case.list_pictures(root_path=Path(path))

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
