import os
import unittest
import uuid

from app.storage.google_photos import GooglePhotosAPIAuthenficationException, GooglePhotosAPIClient

TEST_PICTURE="tests/files/test_image_1_3000.JPG"

OUTDATED_TOKEN = "ya29.a0Aa4xrXOFxWOO8hKhLszQHOdvdneVfV7sH-Nl4EOUtsTyznhHNWUZHuvce31Kakt5ogcImsssTvop5FMtkt8WTUaE4ZsS0t0gPK4iEYAlPgtLFfD_sWIN7BjLBa_7WJ96IcSLTyEu_syAJ8TCvhyGxZdTbe3naCgYKATASARISFQEjDvL90qbSsSOnz0z8SMuULS9hFg0163"

class TestGooglePhotosAPIClient(unittest.TestCase):
    def setUp(self) -> None:
        self.google_client = GooglePhotosAPIClient(access_token=os.getenv("GOOGLE_AUTH_ACCESS_TOKEN"))
        self.google_client_incorrect_access = GooglePhotosAPIClient(access_token=OUTDATED_TOKEN)
        self.picture_hash = uuid.uuid1()

    def test_upload_incorrect_token(self):
        def upload_picture():
            self.google_client_incorrect_access.upload_picture(picture_file_path=TEST_PICTURE, picture_hash=self.picture_hash)

        self.assertRaises(GooglePhotosAPIAuthenficationException, upload_picture)

    def test_get_info_incorrect_token(self):
        def get_info():
            self.google_client_incorrect_access.get_picture_info(picture_id="xxxxx")

        self.assertRaises(GooglePhotosAPIAuthenficationException, get_info)


    def test_upload_edit_get_info(self):
        picture_id = self.google_client.upload_picture(picture_file_path=TEST_PICTURE, picture_hash=self.picture_hash)
        self.google_client.edit_picture_description(picture_id=picture_id, new_description="TO BE DELETED")
        picture_info = self.google_client.get_picture_info(picture_id=picture_id)

        self.assertEqual(picture_info['description'], "TO BE DELETED")

    def test_get_not_exists(self):
        fake_picture_id = "BLeY-QmJN3aBViPBuryTnj6odBuLQYfbahR1m4cs02D96MTdx52urlM8AxoDe0nrpQzqX1WWw1XBbpBW2Gt2hf_YDO80IIgqKQ"
        picture_info = self.google_client.get_picture_info(picture_id=fake_picture_id)

        self.assertEqual(picture_info, None)
