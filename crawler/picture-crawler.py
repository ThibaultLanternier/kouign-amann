import click
import logging
import configparser
import asyncio
import uuid
import platform
import random

from pathlib import Path

from datetime import datetime
from progressbar import ProgressBar

from app.processor import (
    PictureProcessor,
    ParalellPictureProcessor,
    BackupProcessor,
    ParallelBackupProcessor,
    AsyncPictureProcessor,
)
from app.controllers.picture import AbstractPictureAnalyzer, PictureAnalyzerFactory
from app.controllers.recorder import (
    PictureRESTRecorder,
    CrawlHistoryStore,
    AsyncRecorder,
    AsyncCrawlHistoryStore,
)
from app.controllers.backup import BackupHandler
from app.controllers.file import FileCrawler
from app.tools.logger import init_console, init_file_log
from app.storage.factory import StorageFactory

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
    config_file_path = Path("config.ini")

    if config_file_path.is_file():
        raise Exception("config.ini already exists please delete it first")

    new_config = configparser.ConfigParser()

    default_id = platform.node() + "-" + str(uuid.uuid4())

    new_config["crawler"] = {}
    new_config["crawler"]["id"] = click.prompt("Enter Crawler Id", default=default_id)
    new_config["crawler"]["worker_qty"] = "4"
    new_config["crawler"]["picture_path"] = click.prompt(
        "Enter absolute path to your pictures directory"
    )

    new_config["server"] = {}
    new_config["server"]["url"] = click.prompt(
        "Enter API URL", default="https://photos.kerjeannic.com/api"
    )

    with open("config.ini", "w") as config_file:
        new_config.write(config_file)


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

    progressbar = ProgressBar()

    parallel_backup_processor = ParallelBackupProcessor(
        backup_processor, logger, progressbar
    )

    asyncio.run(parallel_backup_processor.run_forever())


@cli.command()
@click.option(
    "--config-file", default="config.ini", help="Location of the configuration file"
)
def crawlasync(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    CRAWLER_ID = config["crawler"]["id"]
    REST_API_URL = config["server"]["url"]
    CRAWL_TIME = datetime.utcnow()

    DIRECTORY_SECTION = config.items("picture_directories")
    DIRECTORY_LIST = [x[1] for x in DIRECTORY_SECTION]

    file_history_recorder = AsyncCrawlHistoryStore()

    file_crawler = FileCrawler(DIRECTORY_LIST)
    file_list = file_crawler.get_file_list()

    new_modified_files = FileCrawler.get_relevant_files(
        file_list=file_list,
        crawl_history=file_history_recorder.get_crawl_history(),
    )

    path_list = [local_file.path for local_file in new_modified_files]

    async_processor = AsyncPictureProcessor(
        picture_path_list=path_list,
        crawler_id=CRAWLER_ID,
        crawl_time=CRAWL_TIME,
        async_recorder=AsyncRecorder(base_url=REST_API_URL),
        file_history_recorder=file_history_recorder,
    )

    asyncio.run(async_processor.process())


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

    DIRECTORY_SECTION = config.items("picture_directories")
    DIRECTORY_LIST = [x[1] for x in DIRECTORY_SECTION]

    REST_API_URL = config["server"]["url"]
    CRAWL_TIME = datetime.utcnow()
    CRAWLER_ID = config["crawler"]["id"]
    WORKER_QTY = int(config["crawler"].get("worker_qty", "5"))
    METRICS_OUTPUT_PATH = config["crawler"].get("metrics_output_path", None)
    FILE_LOGS_PATH = config["crawler"].get("file_logs_path", None)

    if FILE_LOGS_PATH is not None:
        init_file_log(logging.DEBUG, FILE_LOGS_PATH)

    file_crawler = FileCrawler(directory_list=DIRECTORY_LIST)
    picture_recorder = PictureRESTRecorder(REST_API_URL)

    def picture_with_perception_hash(picture_path: Path) -> AbstractPictureAnalyzer:
        return PictureAnalyzerFactory().perception_hash(picture_path)

    CRAWL_ID = uuid.uuid4()

    crawl_history_store = CrawlHistoryStore()

    processor = PictureProcessor(
        picture_with_perception_hash,
        picture_recorder,
        CRAWLER_ID,
        CRAWL_TIME,
        METRICS_OUTPUT_PATH,
        CRAWL_ID,
        crawl_history_store,
    )

    progressbar = ProgressBar()

    file_list = file_crawler.get_file_list()

    local_file_list = FileCrawler.get_relevant_files(
        file_list=file_list,
        crawl_history=crawl_history_store.get_crawl_history(),
    )

    path_list = [local_file.path for local_file in local_file_list]

    random.shuffle(path_list)

    paralell_processor = ParalellPictureProcessor(
        path_list,
        processor.process,
        logger,
        progressbar,
        WORKER_QTY,
    )

    paralell_processor.run()


if __name__ == "__main__":
    cli()
