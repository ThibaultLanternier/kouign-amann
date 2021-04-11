import os

from src.app.adapteurs import BackupManager, PictureManager
from src.app.models import StorageConfig, StorageType
from src.http.server import get_flask_app
from src.persistence.adapteurs import get_mongo_persistence

DEBUG = os.getenv("DEBUG") == "1"
HOST = os.getenv("HOST")
MONGO_HOST = str(os.getenv("MONGO_HOST"))

app = get_flask_app()

DEFAULT_STORAGE_ID = "xxxx"

storage_list = [
    StorageConfig(
        id=DEFAULT_STORAGE_ID,
        type=StorageType.AWS_S3,
        config={
            "key": str(os.getenv("AWS_KEY")),
            "secret": str(os.getenv("AWS_SECRET")),
            "bucket": str(os.getenv("AWS_BUCKET")),
        },
    )
]

persistence = get_mongo_persistence(host=MONGO_HOST)
picture_manager = PictureManager(persistence=persistence)
backup_manager = BackupManager(
    persistence=persistence,
    storage_config_list=storage_list,
)

app.config["picture_manager"] = picture_manager
app.config["backup_manager"] = backup_manager

app.run(debug=DEBUG, host=HOST)
