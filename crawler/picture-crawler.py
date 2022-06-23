import click
import logging
import configparser
import asyncio
import uuid

from datetime import datetime
from app.processor import (
    PictureProcessor,
    ParalellPictureProcessor,
    BackupProcessor,
    ParallelBackupProcessor,
)
from app.controllers.picture import AbstractPictureAnalyzer, PictureAnalyzerFactory
from app.controllers.recorder import PictureRESTRecorder
from app.controllers.backup import BackupHandler
from app.controllers.file import FileCrawler
from app.tools.logger import init_console
from app.storage.basic import StorageFactory

FILE_PATH = "/home/thibault/Images"
REST_API_URL = "http://localhost:5000"
CRAWLER_ID = "debug-local"
CRAWL_TIME = datetime.utcnow()
WORKER_QTY = 10

init_console(logging.INFO)
logger = logging.getLogger("app.crawl")


@click.group()
def cli():
    pass


@cli.command()
def init():
    """
    To come generate a config.ini file with a unique id
    """
    raise NotImplementedError()


@cli.command()
@click.option(
    "--config-file", default="config.ini", help="Location of the configuration file"
)
def backup(config_file):
    """
    Start processing backup requests
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    CRAWLER_ID = config["crawler"]["id"]
    REST_API_URL = config["server"]["url"]

    handler = BackupHandler(crawler_id=CRAWLER_ID, base_url=REST_API_URL)
    storage_factory = StorageFactory(handler)
    backup_processor = BackupProcessor(handler, storage_factory, logger)
    parallel_backup_processor = ParallelBackupProcessor(backup_processor, logger)

    asyncio.run(parallel_backup_processor.run_forever())


@cli.command()
@click.option(
    "--config-file", default="config.ini", help="Location of the configuration file"
)
def crawl(config_file: str):
    """
    Start crawling for pictures
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    FILE_PATH = config["crawler"]["picture_path"]
    REST_API_URL = config["server"]["url"]
    CRAWL_TIME = datetime.utcnow()
    CRAWLER_ID = config["crawler"]["id"]
    WORKER_QTY = int(config["crawler"].get("worker_qty", "5"))
    METRICS_OUTPUT_PATH =  config["crawler"].get("metrics_output_path", None)

    file_crawler = FileCrawler(FILE_PATH)
    picture_recorder = PictureRESTRecorder(REST_API_URL)

    def picture_with_perception_hash(picture_path: str) -> AbstractPictureAnalyzer:
        return PictureAnalyzerFactory().perception_hash(picture_path)

    CRAWL_ID = uuid.uuid4()

    processor = PictureProcessor(
        picture_with_perception_hash, picture_recorder, CRAWLER_ID, CRAWL_TIME, METRICS_OUTPUT_PATH, CRAWL_ID
    )

    paralell_processor = ParalellPictureProcessor(
        file_crawler.get_file_list(), processor.process, logger, WORKER_QTY
    )

    paralell_processor.run()


if __name__ == "__main__":
    cli()
