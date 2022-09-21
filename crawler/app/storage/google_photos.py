import requests

from typing import Dict

from app.storage.basic import AbstractStorage


class GooglePhotosAPIException(Exception):
    pass


class GooglePhotosAPIClient:
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

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

        if res.status_code == 400:
            return None

        if res.status_code == 200:
            return res.json()

        raise GooglePhotosAPIException(res.json())


class GooglePhotosStorage(AbstractStorage):
    def __init__(self, access_token: str) -> None:
        self._access_token = access_token

    def backup(self, picture_local_path: str, picture_hash: str) -> bool:
        raise NotImplementedError()

    def check_still_exists(self, picture_hash: str) -> bool:
        raise NotImplementedError()

    def delete(self, picture_hash: str) -> bool:
        raise NotImplementedError()
