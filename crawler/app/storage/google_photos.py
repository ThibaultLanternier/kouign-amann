import requests

from typing import Callable, Dict
from abc import ABC, abstractmethod
from app.storage.basic import AbstractStorage, BackupResult


class GooglePhotosAPIException(Exception):
    pass


class GooglePhotosAPIAuthenficationException(GooglePhotosAPIException):
    pass


class GooglePhotosAPIClient:
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    def refresh_token(self, new_token) -> None:
        self._access_token = new_token

    def _check_authentication(self, res: requests.Response) -> None:
        if res.status_code == 401:
            raise GooglePhotosAPIAuthenficationException("Access Token is incorrect")

        return

    def _upload_bytes(self, picture_file_path: str) -> str:
        with open(picture_file_path, "rb") as f:
            data = f.read()
            res = requests.post(
                url="https://photoslibrary.googleapis.com/v1/uploads",
                data=data,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Authorization": f"Bearer {self._access_token}",
                    "X-Goog-Upload-Content-Type": "image/jpeg",
                    "X-Goog-Upload-Protocol": "raw",
                },
            )

            self._check_authentication(res)

            if res.status_code == 200:
                return res.text

        raise GooglePhotosAPIException(res.json())

    def _create_media_item(self, upload_token: str, picture_hash: str) -> str:
        res = requests.post(
            url="https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
            json={
                "newMediaItems": [
                    {
                        "description": "Imported by Kouign-Aman",
                        "simpleMediaItem": {
                            "fileName": f"{picture_hash}.jpg",
                            "uploadToken": upload_token,
                        },
                    }
                ]
            },
            headers={
                "Authorization": f"Bearer {self._access_token}",
            },
        )

        self._check_authentication(res)

        if res.status_code == 200:
            return res.json()

        raise GooglePhotosAPIException(res.json())

    def upload_picture(self, picture_file_path: str, picture_hash: str) -> str:
        upload_token = self._upload_bytes(picture_file_path=picture_file_path)
        result = self._create_media_item(
            upload_token=upload_token, picture_hash=picture_hash
        )

        return result["newMediaItemResults"][0]["mediaItem"]["id"]

    def edit_picture_description(self, picture_id: str, new_description: str) -> bool:
        res = requests.patch(
            url=f"https://photoslibrary.googleapis.com/v1/mediaItems/{picture_id}?updateMask=description",
            json={"description": new_description},
            headers={
                "Authorization": f"Bearer {self._access_token}",
            },
        )

        self._check_authentication(res)

        if res.status_code == 200:
            return True

        raise GooglePhotosAPIException(res.json())

    def get_picture_info(self, picture_id: str) -> Dict:
        res = requests.get(
            url=f"https://photoslibrary.googleapis.com/v1/mediaItems/{picture_id}",
            headers={
                "Authorization": f"Bearer {self._access_token}",
            },
        )

        self._check_authentication(res)

        if res.status_code == 400:
            return None

        if res.status_code == 200:
            return res.json()

        raise GooglePhotosAPIException(res.json())


class AbstractCaller(ABC):
    @abstractmethod
    def call(self, func: Callable, params: Dict) -> str:
        pass


class AbstractTokenProvider(ABC):
    @abstractmethod
    def get_new_token(self) -> str:
        pass


class RefreshAccessTokenCaller(AbstractCaller):
    def __init__(
        self, client: GooglePhotosAPIClient, token_provider: AbstractTokenProvider
    ) -> None:
        self._client = client
        self._token_provider = token_provider

    def call(self, func: Callable, params: Dict) -> str:
        try:
            return func(**params)
        except GooglePhotosAPIAuthenficationException:
            new_token = self._token_provider.get_new_token()
            self._client.refresh_token(new_token=new_token)

            return func(**params)


class GooglePhotosStorage(AbstractStorage):
    def __init__(
        self, api_client: GooglePhotosAPIClient, caller: AbstractCaller
    ) -> None:
        self._api_client = api_client
        self._func_caller = caller

    def backup(self, picture_local_path: str, picture_hash: str) -> BackupResult:
        return self._func_caller.call(
            func=self._api_client.upload_picture,
            params={
                "picture_file_path": picture_local_path,
                "picture_hash": picture_hash,
            },
        )

    def check_still_exists(self, picture_backup_id: str) -> bool:
        return (
            self._func_caller.call(
                func=self._api_client.get_picture_info,
                params={"picture_id": picture_backup_id},
            )
            is not None
        )

    def delete(self, picture_backup_id: str) -> bool:
        return self._func_caller.call(
            func=self._api_client.edit_picture_description,
            params={
                "picture_id": picture_backup_id,
                "new_description": "TO BE DELETED",
            },
        )
