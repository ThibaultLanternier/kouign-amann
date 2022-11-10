from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Mapping, Sequence, Tuple, Union

from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING, MongoClient

from src.app.models import (Backup, BackupRequest, BackupStatus, File,
                            GoogleAccessToken, GoogleRefreshToken, Picture,
                            PictureCount, PictureInfo)
from src.persistence.ports import CredentialsPersistencePort, PersistencePort
from src.tools.date import DateTimeConverter, DateTimeFormatException


class MongoCredentialsPersistence(CredentialsPersistencePort):
    def __init__(self, client: MongoClient, db_name: str = "credentials"):
        self.client = client
        self.db = self.client[db_name]
        self.creds_id = ObjectId(b"123456789012")

    def record_refresh_token(self, refresh_token: GoogleRefreshToken):
        self.db.refresh_tokens.insert_one(asdict(refresh_token))

    def get_refresh_token(self) -> Union[GoogleRefreshToken, None]:
        refresh_token_list = self.db.refresh_tokens.find().sort("issued_at", DESCENDING)

        for refresh_token in refresh_token_list:
            del refresh_token["_id"]
            return GoogleRefreshToken(**refresh_token)

        return None

    def record_access_token(self, creds: GoogleAccessToken):
        self.db.access_tokens.insert_one(asdict(creds))

    def get_access_token(self) -> Union[GoogleAccessToken, None]:
        access_token_list = self.db.access_tokens.find().sort("expires_at", DESCENDING)

        for access_token in access_token_list:
            del access_token["_id"]
            return GoogleAccessToken(**access_token)

        return None

    def get_current_state(self) -> str:
        # Temporary : to be changed when managing user session
        return "Ltd9crg0zzdvXyOBqfklJkwC5jIBil"


class MongoPersistence(PersistencePort):
    def __init__(self, client: MongoClient, db_name: str):
        self.client = client
        self.db = self.client[db_name]

    def _mongo_dict_to_picture(self, mongo_dict: Dict) -> Picture:
        del mongo_dict["_id"]
        if mongo_dict.get("updated_on") is not None:
            del mongo_dict["updated_on"]

        output = Picture(**mongo_dict)

        output.info = PictureInfo(**mongo_dict["info"])
        output.file_list = [File(**file) for file in mongo_dict["file_list"]]
        output.backup_list = [
            self._to_backup(backup) for backup in mongo_dict["backup_list"]
        ]

        return output

    def _mongo_dict_to_picture_count(self, mongo_dict: Dict) -> PictureCount:
        month = mongo_dict["_id"]["month"]
        year = mongo_dict["_id"]["year"]

        return PictureCount(
            **{
                "date": datetime(year, month, 1),
                "count": mongo_dict["picture_count"],
                "start_date": mongo_dict["start_date"],
                "end_date": mongo_dict["end_date"],
            }
        )

    def _to_backup_request(self, mongo_dict: Dict) -> BackupRequest:
        mongo_dict.pop("_id")
        mongo_dict["status"] = BackupStatus(mongo_dict["status"])

        if "backup_id" not in mongo_dict:
            mongo_dict["backup_id"] = None

        return BackupRequest(**mongo_dict)

    def _to_backup(self, mongo_dict: Dict) -> Backup:
        if "backup_id" not in mongo_dict:
            mongo_dict["backup_id"] = None

        return Backup(**mongo_dict)

    def get_picture(self, hash: str) -> Union[Picture, None]:
        pictures = self.db.pictures

        picture = pictures.find_one({"hash": hash})

        if picture is not None:
            return self._mongo_dict_to_picture(picture)

        return None

    def list_pictures(self, start: datetime, end: datetime) -> List[Picture]:
        date_time_converter = DateTimeConverter()

        if not date_time_converter.is_timezone_aware(
            start
        ) or not date_time_converter.is_timezone_aware(end):
            raise DateTimeFormatException("time aware datetimes are compulsory")

        pictures = self.db.pictures

        picture_list = pictures.find(
            {
                "info.creation_time": {
                    "$gte": start,
                    "$lte": end,
                }
            }
        ).sort("info.creation_time", ASCENDING)

        return [self._mongo_dict_to_picture(picture) for picture in picture_list]

    def list_recently_updated_pictures(self, duration: timedelta) -> List[Picture]:
        start_time = datetime.now(tz=timezone.utc) - duration

        pictures = self.db.pictures

        picture_list = pictures.find({"updated_on": {"$gte": start_time}})

        return [self._mongo_dict_to_picture(picture) for picture in picture_list]

    def record_picture(
        self, picture: Picture, updated_on: Union[datetime, None] = None
    ) -> None:
        pictures = self.db.pictures

        new_picture = asdict(picture)

        if updated_on is None:
            updated_on = datetime.now(timezone.utc)

        new_picture["updated_on"] = updated_on

        existing_picture = pictures.find_one({"hash": picture.hash})

        if existing_picture is None:
            pictures.insert_one(new_picture)
        else:
            pictures.replace_one({"_id": existing_picture["_id"]}, new_picture)

    def count_picture(self) -> List[PictureCount]:
        pictures = self.db.pictures

        count_query: Sequence[Mapping[str, Any]] = [
            {
                "$group": {
                    "_id": {
                        "month": {"$month": "$info.creation_time"},
                        "year": {"$year": "$info.creation_time"},
                    },
                    "picture_count": {"$sum": 1},
                    "start_date": {"$min": "$info.creation_time"},
                    "end_date": {"$max": "$info.creation_time"},
                },
            },
            {
                "$sort": {
                    "_id.year": 1,
                    "_id.month": 1,
                }
            },
        ]

        command_cursor = pictures.aggregate(count_query)

        return [
            self._mongo_dict_to_picture_count(picture_count)
            for picture_count in command_cursor
        ]

    def get_pending_backup_request(
        self, crawler_id: str, limit: int
    ) -> List[BackupRequest]:
        pictures = self.db.pictures

        query: Sequence[Mapping[str, Any]] = [
            {"$unwind": {"path": "$backup_list"}},
            {
                "$match": {
                    "backup_list.crawler_id": crawler_id,
                    "backup_list.status": {"$in": ["PENDING", "PENDING_DELETE"]},
                }
            },
            {
                "$project": {
                    "crawler_id": "$backup_list.crawler_id",
                    "storage_id": "$backup_list.storage_id",
                    "file_path": "$backup_list.file_path",
                    "picture_hash": "$hash",
                    "status": "$backup_list.status",
                    "backup_id": "$backup_list.backup_id",
                }
            },
            {"$limit": limit},
        ]

        backup_list_cursor = pictures.aggregate(query)

        return [self._to_backup_request(backup) for backup in backup_list_cursor]


def get_mongo_persistences(
    host: str, port: int = 27017
) -> Tuple[PersistencePort, CredentialsPersistencePort]:
    client: MongoClient = MongoClient(host=host, port=port, tz_aware=True)
    return (
        MongoPersistence(client=client, db_name="pictures-manager"),
        MongoCredentialsPersistence(client=client, db_name="pictures-manager"),
    )
