import re


class HashExtractor:
    def extract(self, raw_hash):
        match_result = re.match("^phash:([0-9a-z]{16})$", raw_hash)

        if match_result is None:
            return None
        else:
            return match_result.groups()[0]
