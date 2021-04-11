import unittest
from datetime import datetime, timezone

from src.tools.date import DateTimeConverter


class TestDateTimeConverter(unittest.TestCase):
    def test_to_string(self):
        test_date = datetime(2007, 5, 24, 18, 53, 39, 456, tzinfo=timezone.utc)
        expected = "2007-05-24T18:53:39.000456Z"

        self.assertEqual(expected, DateTimeConverter().to_string(test_date))

    def test_from_string(self):
        input_string = "2007-05-24T18:53:39.000000Z"
        expected = datetime(2007, 5, 24, 18, 53, 39, tzinfo=timezone.utc)

        self.assertEqual(expected, DateTimeConverter().from_string(input_string))

    def test_from_string_long(self):
        input_string = "2007-05-24T18:53:39.000000Z"
        expected = datetime(2007, 5, 24, 18, 53, 39, tzinfo=timezone.utc)

        self.assertEqual(expected, DateTimeConverter().from_string(input_string))
