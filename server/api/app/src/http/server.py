from datetime import datetime

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from src.http.resources import (CrawlerBackup, Ping, Picture, PictureBackupRequest,
                                PictureCount, PictureExists, PictureFile,
                                PictureList, PicturePlanBackup, StorageConfig,
                                UpdatedPictureList)


def fake_encoder(o):
    if isinstance(o, datetime):
        return o.isoformat()


def get_flask_app():
    app = Flask(__name__)
    CORS(app)

    app.config["RESTFUL_JSON"] = {"default": fake_encoder}
    api = Api(app)

    api.add_resource(Ping, "/ping")
    api.add_resource(Picture, "/picture/<string:hash>")
    api.add_resource(PictureFile, "/picture/file/<string:hash>")
    api.add_resource(PictureExists, "/picture/exists/<string:hash>")
    api.add_resource(PictureCount, "/picture/count")
    api.add_resource(PictureList, "/picture/list")
    api.add_resource(UpdatedPictureList, "/picture/updated/<int:duration>")
    api.add_resource(PictureBackupRequest, "/backup/request/<string:hash>")
    api.add_resource(PicturePlanBackup, "/backup/plan/<string:hash>")
    api.add_resource(CrawlerBackup, "/crawler/backup/<string:crawler_id>")
    api.add_resource(StorageConfig, "/crawler/storage/<string:storage_id>")

    return app
