import unittest


class TestPictureDataRepository(unittest.TestCase):
    def test_get(self):
        # Assuming you have a PictureDataRepository class and a method to get pictures
        from app.repositories.picture_data_repository import PictureDataRepository

        repository = PictureDataRepository()
        pictures = repository.get_pictures()

        self.assertIsInstance(pictures, list)
        self.assertTrue(all(isinstance(picture, dict) for picture in pictures))