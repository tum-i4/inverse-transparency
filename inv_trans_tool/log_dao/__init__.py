#!.venv/bin/python3
# encoding=utf-8
""" Log DAO module """

import datetime as dt
from typing import List, Tuple


def load_all(user_id:str, start:dt.date = None) -> List[Tuple[str, str, str, dt.datetime]]:
	"""
	Load all data uses regarding the given user.
	
	:param start: Specify the earliest date to retrieve.
	"""
	raise NotImplementedError()
