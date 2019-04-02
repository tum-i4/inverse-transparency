#!/usr/bin/env python3
# encoding=utf-8
""" Log storage """

import time
import json

from log.entry import Entry
import log.format


class Storage(object):
	def __init__(self, filename:str, source:str):
		self.filename = filename
		self.source = source

	def add(self, entry:Entry) -> None:
		content = {
			"time" : time.strftime(log.format.ISO_DATE_FORMAT),
			"source" : self.source
		}
		content.update(entry.to_dict())
		with open(self.filename, "a") as f:
			json.dump(content, f)
			f.write("\n")
