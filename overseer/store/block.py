""" Block class """

import datetime as dt
import json
from hashlib import sha3_256
from typing import Optional


class Block(object):
    """ A block in the chain """

    def __init__(
        self,
        index: int,
        content,
        previous_hash: str,
        timestamp_dt: Optional[dt.datetime] = None,
    ):
        """ If timestamp is not given, the current time is assumed. """

        self.index: int = index
        self.content = content
        self.previous_hash: str = previous_hash

        timestamp_dt = timestamp_dt or dt.datetime.now()
        self.timestamp: str = timestamp_dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    def _hash(self) -> str:
        """ Hash the block contents with SHA3_256 and return the hex digest. """
        stringified: str = json.dumps(
            {
                "index": self.index,
                "content": self.content,
                "previous_hash": self.previous_hash,
                "timestamp": self.timestamp,
            },
            sort_keys=True,
        )
        return sha3_256(stringified.encode()).hexdigest()
