""" Block class """

import datetime as dt
from functools import reduce
import json
from hashlib import sha3_256
from typing import Optional


class Block(object):
    """ A block in the chain """

    # TODO: Continue here https://www.ibm.com/developerworks/cloud/library/cl-develop-blockchain-app-in-python/index.html

    def __init__(
        self,
        index: int,
        content,
        previous_hash: str,
        timestamp_dt: Optional[dt.datetime] = None,
    ):
        """ Ctor. If timestamp is not given, the current time is assumed. """

        self.index: int = index
        self.content = content
        self.previous_hash: str = previous_hash

        timestamp_dt = timestamp_dt or dt.datetime.now()
        self.timestamp: str = timestamp_dt.strftime("%Y-%m-%dT%H:%M:%S%z")

        self.hash = self._hash()

    def _hash(self) -> str:
        """ Hash the block contents with SHA3_256 and return the hex digest. """
        stringified: str = reduce(
            (lambda x, y: x + y),
            map(str, [self.index, self.content, self.previous_hash, self.timestamp]),
            "",
        )
        return sha3_256(stringified.encode()).hexdigest()
