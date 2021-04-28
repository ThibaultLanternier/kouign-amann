from dataclasses import asdict
from datetime import datetime, timedelta

from flask import current_app, request
from flask_restful import Resource
from flask_restful.inputs import datetime_from_iso8601
from flask_restful.reqparse import RequestParser

from src.app.models import BackupRequest, DictFactory, File, PictureInfo
from src.app.ports import (AbstractBackupManager, AbstractPictureManager,
                           MissingPictureException)


def get_picture_manager() -> AbstractPictureManager:
    return current_app.config["picture_manager"]


def get_backup_manager() -> AbstractBackupManager:
    return current_app.config["backup_manager"]

class Ping(Resource):
    def get(self):
        return {"ping":"ok"} , 200

class PictureCount(Resource):
    def get(self):
        picture_count_list = get_picture_manager().count()
        picture_count_list_dict = [
            asdict(x, dict_factory=DictFactory) for x in picture_count_list
        ]

        return picture_count_list_dict, 200


class PictureList(Resource):
    def get(self):
        parser = RequestParser()
        parser.add_argument("start", type=datetime_from_iso8601)
        parser.add_argument("end", type=datetime_from_iso8601)
        args = parser.parse_args()

        picture_list = get_picture_manager().list_pictures(args["start"], args["end"])
        picture_list_dict = [asdict(x, dict_factory=DictFactory) for x in picture_list]

        return picture_list_dict, 200


class UpdatedPictureList(Resource):
    def get(self, duration: int):
        duration_timedelta = timedelta(seconds=duration)

        picture_list = get_picture_manager().list_recently_updated_pictures(
            duration=duration_timedelta
        )
        picture_list_dict = [asdict(x, dict_factory=DictFactory) for x in picture_list]

        return picture_list_dict, 200


class PictureExists(Resource):
    def get(self, hash):
        if get_picture_manager().get_picture(hash) is not None:
            return "OK", 200
        else:
            return "NOT FOUND", 404


class Picture(Resource):
    def get(self, hash: str):
        picture = get_picture_manager().get_picture(hash)

        if picture is not None:
            return asdict(picture, dict_factory=DictFactory), 200
        else:
            return "NOT FOUND", 404

    def post(self, hash: str):
        picture_info = PictureInfo(**request.json)

        get_picture_manager().record_picture_info(hash, picture_info)

        return f"/picture/{hash}", 201


class PictureFile(Resource):
    def put(self, hash: str):
        picture_file = File(**request.json)

        try:
            get_picture_manager().record_picture_file(hash, picture_file)
        except MissingPictureException:
            return "NOT FOUND", 404

        return f"/picture/{hash}", 201


class PictureBackupRequest(Resource):
    def _set_backup(self, hash: str, backup_required: bool):
        picture_manager = get_picture_manager()
        picture = picture_manager.get_picture(hash)

        if picture is None:
            return "NOT FOUND", 404

        picture.backup_required = backup_required

        picture_manager.record_picture(picture)

        return f"/picture/{hash}", 201

    def post(self, hash: str):
        return self._set_backup(hash, True)

    def delete(self, hash: str):
        return self._set_backup(hash, False)


class PicturePlanBackup(Resource):
    def put(self, hash: str):
        picture_manager = get_picture_manager()
        backup_manager = get_backup_manager()

        picture = picture_manager.get_picture(hash)

        if picture is None:
            return "NOT FOUND", 404

        picture.plan_backup(
            storage_list=backup_manager.get_storages(), current_time=datetime.utcnow()
        )

        picture_manager.record_picture(picture)

        return f"/backup/{hash}", 201

    def get(self, hash: str):
        picture = get_picture_manager().get_picture(hash)

        if picture is not None:
            picture_dict = asdict(picture, dict_factory=DictFactory)
            return picture_dict["backup_list"], 200
        else:
            return "NOT FOUND", 404


class CrawlerBackup(Resource):
    def get(self, crawler_id: str):
        backup_manager = get_backup_manager()

        backup_request_list = backup_manager.get_pending_backup_request(
            crawler_id=crawler_id, limit=20
        )

        backup_request_list_dict = [
            asdict(x, dict_factory=DictFactory) for x in backup_request_list
        ]

        return backup_request_list_dict, 200

    def post(self, crawler_id: str):
        picture_manager = get_picture_manager()

        backup_request = BackupRequest(**request.json)

        picture = picture_manager.get_picture(backup_request.picture_hash)

        if picture is None:
            return "NOT FOUND", 404

        picture.record_done(
            storage_id=backup_request.storage_id, crawler_id=backup_request.crawler_id
        )

        picture_manager.record_picture(picture=picture)

        return f"/picture/{backup_request.picture_hash}", 201

    def delete(self, crawler_id: str):
        picture_manager = get_picture_manager()

        backup_request = BackupRequest(**request.json)

        picture = picture_manager.get_picture(backup_request.picture_hash)

        if picture is None:
            return "NOT FOUND", 404

        picture.record_backup_error(
            storage_id=backup_request.storage_id, crawler_id=backup_request.crawler_id
        )

        picture_manager.record_picture(picture=picture)

        return f"/picture/{backup_request.picture_hash}", 201


class StorageConfig(Resource):
    def get(self, storage_id: str):
        backup_manager = get_backup_manager()

        storage_config = backup_manager.get_storage_config(storage_id)

        if storage_config is None:
            return "NOT FOUND", 404
        else:
            return asdict(storage_config, dict_factory=DictFactory), 200
