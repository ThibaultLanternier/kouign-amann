import os
import unittest
from datetime import datetime, timezone

from app.storage.google_photos import RESTTokenProvider


class TestRESTTokenProvider(unittest.TestCase):
    def setUp(self) -> None:
        API_URL = os.getenv("API_URL")
        self.assertIsNotNone(API_URL)

        self.token_provider_url = f"{API_URL}/auth/google/access_token"

    def test_get_current_token(self):
        token_provider = RESTTokenProvider(url=self.token_provider_url)

        token = token_provider.get_current_token()

        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_get_new_token(self):
        token_provider = RESTTokenProvider(url=self.token_provider_url)

        token = token_provider.get_new_token()

        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

