import unittest

from app.entities.picture_data import iPictureData
from app.models import picture
from app.services.picture_id import PictureIdService


class TestPictureIdService(unittest.TestCase):
    def test_compute_id(self):
        picture_id_service = PictureIdService()

        picture_path = "tests/files/test-canon-eos70D.jpg"
        
        expected_hash = "c643dbe5e4d60f02"

        picture_data = picture_id_service.compute_id(picture_path)

        self.assertIsInstance(picture_data, iPictureData)
        self.assertEqual(picture_data.get_hash(), expected_hash)
