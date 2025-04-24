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
    "--year", default=0, help="Only process files from this year (0 = all years)"
)
@click.option(
    "--strict", default=False, help="Does not rely on local file store only on perception hash"
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

    if strict: # In strict mode all files reprocessd and checked
        new_modified_files = file_list
    else:
        new_modified_files = FileCrawler.get_relevant_files(
            file_list=file_list,
            crawl_history=file_history_recorder.get_crawl_history(),
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


if __name__ == "__main__":
    cli()
