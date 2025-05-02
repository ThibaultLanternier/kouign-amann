import unittest
from unittest.mock import MagicMock

from app.entities.picture_data import iPictureData
from app.repositories.picture_data import iPictureDataRepository
from app.services.picture_id import PictureIdService


class TestPictureIdService(unittest.TestCase):
    def test_compute_id(self):
        mock_picture_data_repo = MagicMock(name="mock_picture_data_repo", spec=iPictureDataRepository)

        picture_id_service = PictureIdService(picture_data_repo=mock_picture_data_repo)

        picture_path = "tests/files/test-canon-eos70D.jpg"
        
        expected_hash = "c643dbe5e4d60f02"

        picture_data = picture_id_service.compute_id(picture_path)

        self.assertIsInstance(picture_data, iPictureData)
        self.assertEqual(picture_data.get_hash(), expected_hash)
