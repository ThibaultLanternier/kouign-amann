import os

from src.app.adapteurs import BackupManager, PictureManager
from src.http.server import get_flask_app
from src.persistence.adapteurs import get_mongo_persistences
from src.tools.config import ConfigManager

DEBUG = os.getenv("DEBUG") == "1"
SSL = os.getenv("SSL", "0") == "1"
HOST = os.getenv("HOST")
MONGO_HOST = str(os.getenv("MONGO_HOST"))
STORAGE_CONFIG = os.getenv("STORAGE_CONFIG", "storage.json")

app = get_flask_app()

storage_list = ConfigManager(STORAGE_CONFIG).storage_config_list()

persistence, credentials_storage = get_mongo_persistences(host=MONGO_HOST)
picture_manager = PictureManager(persistence=persistence)
backup_manager = BackupManager(
    persistence=persistence,
    storage_config_list=storage_list,
)

app.config["picture_manager"] = picture_manager
app.config["backup_manager"] = backup_manager
app.config["credentials_storage"] = credentials_storage

if __name__ == "__main__":
    if SSL:
        app.run(
            debug=DEBUG, host=HOST, ssl_context=("X509KouignAmann.crt", "MyPrivate.key")
        )
    else:
        app.run(debug=DEBUG, host=HOST)
