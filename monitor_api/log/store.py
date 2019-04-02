#!/usr/bin/env python3
# encoding=utf-8
""" Log storage """

from log.entry import Entry


class Storage(object):
	def __init__(self, filename:str, source:str):
		raise NotImplementedError()

	def add(self, entry:Entry) -> None:
		raise NotImplementedError()
