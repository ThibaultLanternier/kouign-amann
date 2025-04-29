import click
import logging
import configparser
import asyncio

from pathlib import Path

from app.async_processor import AsyncPictureProcessor
from app.controllers.async_history_store import AsyncCrawlHistoryStore
from app.controllers.file import FileCrawler
from app.tools.logger import init_console
from app.controllers.async_file_recorder import AsyncFileRecorder
from app.tools.config_file import ConfigFileManager
from app.tools.picture_grouper import PictureGrouper, PictureGroup
from app.tools.path import get_existing_picture

from app.use_cases.backup import backup_use_case_factory

init_console(logging.INFO)

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
)
@click.argument("target_path", type=click.Path(exists=True))
def backup2(target_path: str, strict: bool):
    """
    Copy new pictures found in target directory to backup directory
    """
    config = configparser.ConfigParser()
    config.read(ConfigFileManager().config_file_path)

    backup_folder_path = Path(config["backup"]["path"])
    target_folder_path = Path(target_path)

    backup_use_case = backup_use_case_factory(backup_folder_path=backup_folder_path)

    file_list = backup_use_case.list_pictures(root_path=target_folder_path)

    backup_use_case.backup(
        picture_list_to_backup=file_list,
        strict_mode=strict,
    )

@cli.command()
@click.option(
    "--year", default=0, help="Only process files from this year (0 = all years)"
)
@click.option(
    "--strict",
    default=False,
    help="Does not rely on local file store only on perception hash",
)
@click.argument("target_path", type=click.Path(exists=True))
def backup(target_path: str, year: int, strict: bool):
    """
    Copy new pictures found in target directory to backup directory
    """
    config = configparser.ConfigParser()
    config.read(ConfigFileManager().config_file_path)

    backup_folder_path = Path(config["backup"]["path"])

    file_history_recorder = AsyncCrawlHistoryStore(file_directory=backup_folder_path)

    file_crawler = FileCrawler([target_path])
    file_list = file_crawler.get_file_list()

    if strict:  # In strict mode all files reprocessd and checked
        new_modified_files = file_list
    else:
        new_modified_files = list(
            FileCrawler.get_relevant_files(
                file_list=file_list,
                crawl_history=file_history_recorder.get_crawl_history(),
            )
        )

    path_list = [local_file.path for local_file in new_modified_files]

    async_file_recorder = AsyncFileRecorder(base_file_path=backup_folder_path)

    async_processor = AsyncPictureProcessor(
        picture_path_list=path_list,
        async_recorder=async_file_recorder,
        file_history_recorder=file_history_recorder,
        filter_year=year,
    )

    asyncio.run(async_processor.process())


@cli.command()
@click.option(
    "--delta",
    default=1,
    help="Number of days time difference to group pictures together",
)
def group(delta: int):
    """
    Group pictures event
    """
    config = configparser.ConfigParser()
    config.read(ConfigFileManager().config_file_path)

    backup_folder_path = Path(config["backup"]["path"])

    existing_pictures = get_existing_picture(path=backup_folder_path)

    logger = logging.getLogger("app.group_pictures")

    logger.info(f"Received {len(existing_pictures)} that need to be grouped")

    group_list = [
        PictureGroup(x)
        for x in PictureGrouper(picture_path_list=existing_pictures).group_pictures(
            max_days=delta
        )
    ]

    logger.info(f"Found {len(group_list)} groups with a max delta of {delta} day(s)")

    for group in group_list:
        pictures_to_move = group.list_pictures_to_move()
        if len(pictures_to_move) > 0:
            logger.info(
                f"Group {group.get_folder_path()} with {len(pictures_to_move)} pictures"
            )
            for picture in group.list_pictures_to_move():
                logger.info(f"Starting moving picture {picture[0].name}")
                if not picture[1].parent.exists():
                    picture[1].parent.mkdir(parents=True)
                    logger.info(f"Created folder {picture[1].parent}")

                picture[0].rename(picture[1])
                logger.info(f"Moved picture {picture[0]} to {picture[1]}")


if __name__ == "__main__":
    cli()
