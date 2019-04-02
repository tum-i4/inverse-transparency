#!/usr/bin/env python3
# encoding=utf-8
""" MEFileHandler class """

from logging import FileHandler, LogRecord

import log.entry


class MEFileHandler(FileHandler):
	""" Custom handler for a log.entry.Entry object. """

	def __init__(self, filename, mode="r", encoding=None, delay=False):
		super().__init__(filename, mode, encoding, delay)

	def emit(self, record:LogRecord):
		if not isinstance(record, log.entry.Entry):
			return

		super().emit(record)
