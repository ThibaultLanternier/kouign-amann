from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Dict, cast

import flask
import requests
from flask import current_app, request
from flask_restful import Resource
from google_auth_oauthlib.flow import Flow
from marshmallow import Schema, fields, post_load

from src.app.models import (BackupRequest, BackupStatus, DictFactory, File,
                            GoogleRefreshToken, PictureInfo,
                            google_access_token_factory)
from src.app.ports import (AbstractBackupManager, AbstractPictureManager,
                           MissingPictureException)
from src.persistence.ports import CredentialsPersistencePort


def get_google_oauth_secret_filename() -> str:
    return current_app.config["google_auth_config_file"]


def get_picture_manager() -> AbstractPictureManager:
    return current_app.config["picture_manager"]


def get_backup_manager() -> AbstractBackupManager:
    return current_app.config["backup_manager"]


def get_credentials_storage() -> CredentialsPersistencePort:
    return current_app.config["credentials_storage"]


class Ping(Resource):
    def get(self):
        return {"ping": "ok"}, 200


class PictureCount(Resource):
    def get(self):
        picture_count_list = get_picture_manager().count()
        picture_count_list_dict = [
            asdict(x, dict_factory=DictFactory) for x in picture_count_list
        ]

        return picture_count_list_dict, 200


class DateRangeSchema(Schema):
    start = fields.AwareDateTime()
    end = fields.AwareDateTime()


class GoogleRefreshTokenAnswer(Schema):
    access_token = fields.String()
    expires_in = fields.Integer()
    token_type = fields.String()
    scope = fields.String()

    @post_load()
    def convert_scope_to_list(self, data, **kwargs):
        data["scope"] = data["scope"].split(" ")
        return data


class GoogleAuthAccessTokenAnswer(Schema):
    access_token = fields.String()
    expires_in = fields.Integer()
    refresh_token = fields.String(required=False)
    scope = fields.List(fields.String())
    token_type = fields.String()
    expires_at = fields.Float()


class PictureList(Resource):
    def get(self):
        date_range_schema = DateRangeSchema()
        args = date_range_schema.load(request.args.to_dict())

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
        request_payload = cast(Dict, request.json)

        picture_info = PictureInfo(**request_payload)

        get_picture_manager().record_picture_info(hash, picture_info)

        return f"/picture/{hash}", 201


class PictureFile(Resource):
    def put(self, hash: str):
        request_payload = cast(Dict, request.json)

        picture_file = File(**request_payload)

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
    # Used to trigger adding new planned backup to a picture based on available storages
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

    # Gets the list of available backup for a picture
    def get(self, hash: str):
        picture = get_picture_manager().get_picture(hash)

        if picture is not None:
            picture_dict = asdict(picture, dict_factory=DictFactory)
            return picture_dict["backup_list"], 200
        else:
            return "NOT FOUND", 404


class CrawlerBackup(Resource):
    # Used to retrieve the list of pending backup requests for a given crawler
    def get(self, crawler_id: str):
        backup_manager = get_backup_manager()

        backup_request_list = backup_manager.get_pending_backup_request(
            crawler_id=crawler_id, limit=20
        )

        backup_request_list_dict = [
            asdict(x, dict_factory=DictFactory) for x in backup_request_list
        ]

        return backup_request_list_dict, 200

    def _add_missing_backup_id(self, backup_request: Dict):
        if "backup_id" not in backup_request:
            backup_request["backup_id"] = None

        return backup_request

    # Use to acknowledge completion of a backup request (PENDING or PENDING_DELETE)
    def post(self, crawler_id: str):
        picture_manager = get_picture_manager()

        backup_request = BackupRequest(
            **self._add_missing_backup_id(cast(Dict, request.json))
        )

        if backup_request.status not in [
            BackupStatus.PENDING,
            BackupStatus.PENDING_DELETE,
        ]:
            return "INCORRECT BACKUP STATUS", 400

        picture = picture_manager.get_picture(backup_request.picture_hash)

        if picture is None:
            return "NOT FOUND", 404

        if backup_request.status == BackupStatus.PENDING:
            picture.record_done(
                storage_id=backup_request.storage_id,
                crawler_id=backup_request.crawler_id,
                backup_id=backup_request.backup_id,
            )
        else:
            picture.record_deleted(
                storage_id=backup_request.storage_id,
                crawler_id=backup_request.crawler_id,
            )

        picture_manager.record_picture(picture=picture)

        return f"/picture/{backup_request.picture_hash}", 201

    # Used to record a backup error
    def delete(self, crawler_id: str):
        picture_manager = get_picture_manager()

        backup_request = BackupRequest(
            **self._add_missing_backup_id(cast(Dict, request.json))
        )

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


GOOGLE_PHOTO_API_SCOPES = [
    "https://www.googleapis.com/auth/photoslibrary.readonly",
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata",
]


class Authentification(Resource):
    # Returns the URL needed to authenticate with Google API
    def get(self):
        if get_google_oauth_secret_filename() is None:
            return "Google Photos not enabled", 404

        flow = Flow.from_client_secrets_file(
            get_google_oauth_secret_filename(),
            scopes=GOOGLE_PHOTO_API_SCOPES,
            state=get_credentials_storage().get_current_state(),
        )

        ROOT_URL = request.root_url

        flow.redirect_uri = f"{ROOT_URL}auth/google/callback"

        authorization_url, state = flow.authorization_url(
            access_type="offline", include_granted_scopes="true"
        )

        return authorization_url, 200


class Oauth(Resource):
    def get(self):
        if get_google_oauth_secret_filename() is None:
            return "Google Photos not enabled", 404

        credentials_storage = get_credentials_storage()

        flow = Flow.from_client_secrets_file(
            get_google_oauth_secret_filename(),
            scopes=GOOGLE_PHOTO_API_SCOPES,
            state=credentials_storage.get_current_state(),
        )

        ROOT_URL = request.root_url

        flow.redirect_uri = f"{ROOT_URL}auth/google/callback"

        authorization_response = flask.request.url
        result = flow.fetch_token(authorization_response=authorization_response)

        google_auth_answer = GoogleAuthAccessTokenAnswer().load(result)

        if "refresh_token" in google_auth_answer:
            token = GoogleRefreshToken(
                refresh_token=google_auth_answer["refresh_token"],
                scope=google_auth_answer["scope"],
                issued_at=datetime.now(tz=timezone.utc),
            )
            credentials_storage.record_refresh_token(refresh_token=token)

        access_token = google_access_token_factory(
            google_auth_answer, now=datetime.now(tz=timezone.utc)
        )

        credentials_storage.record_access_token(access_token)

        return result, 200


class AccessToken(Resource):
    def get(self):
        credentials_storage = get_credentials_storage()

        return (
            asdict(credentials_storage.get_access_token(), dict_factory=DictFactory),
            200,
        )

    def patch(self):
        credentials_storage = get_credentials_storage()

        flow = Flow.from_client_secrets_file(
            get_google_oauth_secret_filename(),
            scopes=GOOGLE_PHOTO_API_SCOPES,
            state=credentials_storage.get_current_state(),
        )
        client_config = flow.client_config

        refresh_token = credentials_storage.get_refresh_token().refresh_token

        refresh_token_query = {
            "client_id": client_config["client_id"],
            "client_secret": client_config["client_secret"],
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        res = requests.post(url=client_config["token_uri"], json=refresh_token_query)

        res_json = res.json()

        if res.status_code != 200:
            return res_json, res.status_code

        google_auth_answer = GoogleRefreshTokenAnswer().load(res_json)
        access_token = google_access_token_factory(
            google_auth_answer, now=datetime.now(tz=timezone.utc)
        )
        credentials_storage.record_access_token(access_token)

        return asdict(access_token, dict_factory=DictFactory), 200
