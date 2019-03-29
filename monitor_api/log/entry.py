#!/usr/bin/env python3
# encoding=utf-8
""" Entry class """

from typing import Dict


class Entry(object):
	""" Log content object """

	def __init__(self, method:str, url:str, request_params:Dict, response_content:str):
		self.method = method
		self.url = url
		self.request_params = request_params
		self.response_content = response_content


	def __str__(self):
		return "{} {} | Data: {} | Return: {}".format(
			self.method,
			self.url,
			self.request_params,
			self.response_content
		)
