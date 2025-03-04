from typing import Dict
import click
import logging
import configparser
import asyncio

from pathlib import Path

from datetime import datetime, timezone

from app.async_processor import AsyncPictureProcessor
from app.controllers.async_history_store import AsyncCrawlHistoryStore
from app.controllers.file import FileCrawler
from app.tools.logger import init_console
from app.controllers.async_file_recorder import AsyncFileRecorder

init_console(logging.INFO)

logger = logging.getLogger("app.crawl")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("backup_path", type=click.Path(exists=True))
def init(backup_path: str):
    """
    record backup_path in config.ini
    """
    config_file_path = Path("config.ini")

    if config_file_path.is_file():
        raise Exception("config.ini already exists please delete it first")

    new_config = configparser.ConfigParser()

    new_config["backup"] = {}
    new_config["backup"]["path"] = backup_path

    with open("config.ini", "w") as config_file:
        new_config.write(config_file)


@cli.command()
@click.option(
    "--config-file", default="config.ini", help="Location of the configuration file"
)
@click.argument("target_path", type=click.Path(exists=True))
def backup(config_file: Dict[str, str], target_path: str):
    """
    Copy new pictures found in target directory to backup directory
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    file_history_recorder = AsyncCrawlHistoryStore()

    file_crawler = FileCrawler([target_path])
    file_list = file_crawler.get_file_list()

    new_modified_files = FileCrawler.get_relevant_files(
        file_list=file_list,
        crawl_history=file_history_recorder.get_crawl_history(),
    )

    path_list = [local_file.path for local_file in new_modified_files]

    async_file_recorder = AsyncFileRecorder(Path(config["backup"]["path"]))

    async_processor = AsyncPictureProcessor(
        picture_path_list=path_list,
        crawler_id="useless_crawler_id",
        crawl_time=datetime.now(timezone.utc),
        async_recorder=async_file_recorder,
        file_history_recorder=file_history_recorder,
    )

    asyncio.run(async_processor.process())


if __name__ == "__main__":
    cli()
