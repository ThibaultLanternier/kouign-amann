import unittest
from datetime import datetime, timedelta, timezone

from app.tools.date import DateTimeConverter
from app.tools.hash import HashExtractor


class TestHashExtractor(unittest.TestCase):
    def test_extract(self):
        self.assertEqual(
            "88335eafa3f00fc4", HashExtractor().extract("phash:88335eafa3f00fc4")
        )

    def test_extract_none(self):
        self.assertIsNone(HashExtractor().extract("phash:788335eafa3f00fc4"))


class TestDateTimeConverter(unittest.TestCase):
    def test_from_string(self):
        self.assertEqual(
            DateTimeConverter().from_string("2012-12-19T06:01:17.171000Z"),
            datetime(2012, 12, 19, 6, 1, 17, 171000, timezone.utc),
        )

    def test_to_string(self):
        self.assertEqual(
            DateTimeConverter().to_string(
                datetime(2012, 12, 19, 6, 1, 17, 171000, timezone.utc)
            ),
            "2012-12-19T06:01:17.171000Z",
        )

    def test_to_string_with_offset(self):
        self.assertEqual(
            DateTimeConverter().to_string(
                datetime(2012, 12, 19, 6, 1, 17, 171000, timezone(timedelta(hours=1)))
            ),
            "2012-12-19T05:01:17.171000Z",
        )
