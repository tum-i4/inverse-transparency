""" Interaction with the Overseer """

import json
import time
from typing import Dict

import requests

from log.entry import Entry
import log.format

from . import OVERSEER_URL


class SeeConnector(object):
    def __init__(self, app: str):
        self.app = app

    def send(self, entry: Entry) -> None:
        """ Alert the Overseer about a data access. """

        entry_dict: Dict[str, str] = entry.to_dict()
        data_user: str = entry_dict.pop("user")

        request_body: Dict = {
            "do": "NOT_YET_DETERMINED",
            "du": data_user,
            "app": self.app,
            "data": entry_dict,
        }

        requests.post(OVERSEER_URL, data=request_body)
