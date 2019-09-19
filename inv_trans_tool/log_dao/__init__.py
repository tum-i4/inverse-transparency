#!.venv/bin/python3
""" Log DAO module """

import datetime as dt
import json
from typing import List, Tuple

LOG_FILE_PATH = "/var/log/mapi.log"
ISO_DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S%z"


def load_all(
    user_id: str, start: dt.date = None
) -> List[Tuple[str, str, str, dt.datetime]]:
    """
	Load all data uses regarding the given user in the form: "Responsible", "Tool", "Usage", "Date"
	
	:param start: Specify the earliest date to retrieve.
	"""

    if not start:
        start = dt.date(1, 1, 1)

    with open(LOG_FILE_PATH, "r") as log_file:
        lines: List[str] = log_file.readlines()

    result: List[Tuple[str, str, str, dt.datetime]] = []

    # We backtrack from the end (newest entry) until reaching the specified start date
    while lines:
        line = lines.pop()
        data = json.loads(line)
        entry_datetime: dt.datetime = dt.datetime.strptime(
            data["time"], ISO_DATETIME_FORMAT
        )

        if entry_datetime.date() < start:
            break

        responsible = data["user"]
        tool = data["api"]
        usage = data["method"]

        result.insert(0, (responsible, tool, usage, entry_datetime))

    return result
