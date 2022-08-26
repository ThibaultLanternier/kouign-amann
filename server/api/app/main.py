import os

from src.tools.config import ConfigManager
from src.app.adapteurs import BackupManager, PictureManager
from src.app.models import StorageConfig, StorageType
from src.http.server import get_flask_app
from src.persistence.adapteurs import get_mongo_persistence

DEBUG = os.getenv("DEBUG") == "1"
HOST = os.getenv("HOST")
MONGO_HOST = str(os.getenv("MONGO_HOST"))
STORAGE_CONFIG = os.getenv("STORAGE_CONFIG","storage.json")

app = get_flask_app()

storage_list = ConfigManager(STORAGE_CONFIG).storage_config_list()

persistence = get_mongo_persistence(host=MONGO_HOST)
picture_manager = PictureManager(persistence=persistence)
backup_manager = BackupManager(
    persistence=persistence,
    storage_config_list=storage_list,
)

app.config["picture_manager"] = picture_manager
app.config["backup_manager"] = backup_manager

if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST)
