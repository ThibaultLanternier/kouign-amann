import unittest
from datetime import datetime, timezone

from app.storage.google_photos import RESTTokenProvider

BASE_URL = "http://app.kouignamann.bzh:5000/auth/google/access_token"


class TestRESTTokenProvider(unittest.TestCase):
    def test_get_current_token(self):
        token_provider = RESTTokenProvider(url=BASE_URL)

        token = token_provider.get_current_token()

        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_get_new_token(self):
        token_provider = RESTTokenProvider(url=BASE_URL)

        token = token_provider.get_new_token()

        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

