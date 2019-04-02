#!/usr/bin/env python3
# encoding=utf-8
""" Entry class """

import json
from typing import Dict


class Entry(object):
	""" Log content object """

	def __init__(self, method:str, url:str, request_params:Dict, response_content:str):
		self.method = method
		self.url = url
		self.request_params = request_params
		self.response_content = response_content


	def __str__(self):
		""" Called when the entry is stored. """
		return "{} {} | Params: {}".format(
			self.method,
			self.url,
			self.request_params
		)


	def to_json(self):
		""" A storable JSON one-liner. """

		return json.dumps({
			"method" : self.method,
			"url" : self.url,
			"request_params" : self.request_params,
			"response_content" : self.response_content
		})
