import unittest
import requests
from datetime import datetime, timezone

BASE_URL = "http://picture-server-debug:5000"

class PictureIntegrationTest(unittest.TestCase):
    def test_post_picture(self):
        test_payload = expected_dict = {
            "hash": 'c643dbe5e4d60e0a',
            "creation_time": "2019-11-19T12:46:56.000Z",
            "crawl_time": "2019-12-19T12:46:56.000Z",
            "crawler_id": "XXXX",
            "resolution": (5472, 3648),
            "thumbnail": '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAADAAUDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwCbUbG0vjFJeW0Ny4BAM6CTABxxnOOnaiiisKram7HTSScEf//Z',
            "picture_path": "/fake/picture/path"
        }

        response = requests.post(f"{BASE_URL}/picture",json=test_payload)

        self.assertEqual(201, response.status_code)

        response = requests.get(f"{BASE_URL}/picture-info/c643dbe5e4d60e0a")

        self.assertEqual(200, response.status_code)

        response = requests.get(f"{BASE_URL}/picture-info/c643dbe5e4d60e0a_xxx")

        self.assertEqual(404, response.status_code)


if __name__ == '__main__':
    unittest.main()
