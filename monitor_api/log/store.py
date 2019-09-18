# encoding=utf-8
""" Log storage """

import json
import time

from log.entry import Entry
import log.format


class Storage(object):
    def __init__(self, filename: str, api: str):
        self.filename = filename
        self.api = api

    def add(self, entry: Entry) -> None:
        content = {"time": time.strftime(log.format.ISO_DATE_FORMAT), "api": self.api}
        content.update(entry.to_dict())
        with open(self.filename, "a") as f:
            json.dump(content, f)
            f.write("\n")
