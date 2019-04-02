#!/usr/bin/env python3
# encoding=utf-8
""" MEFileHandler class """

from logging import FileHandler, Formatter, LogRecord

import log.entry
import log.format


class MEFileHandler(FileHandler):
	""" Custom handler for a log.entry.Entry object. """

	def __init__(self, filename, mode="r", encoding=None, delay=False):
		super().__init__(filename, mode, encoding, delay)
		super().setFormatter(Formatter(fmt=log.format.JSON_LOG_FORMAT, datefmt=log.format.ISO_DATE_FORMAT))

	def emit(self, record:LogRecord):
		if not isinstance(record, log.entry.Entry):
			return

		record.msg = record.msg.to_json()
		super().emit(record)
