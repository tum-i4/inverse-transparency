#!/usr/bin/env python3
# encoding=utf-8

""" API wrapper base """


import logging

from flask import request
from flask_restful import Resource
import requests


class WrappedResourceBase(Resource):
	""" A wrapped resource that pipes and logs requests. """

	def __init__(self, own_name:str, target_url:str, logger_base:str):
		self.target_url = target_url
		self.logger = logging.getLogger(name=logger_base + "." + own_name)

	def _get(self):
		""" Wrapped GET (has to be explicitly linked to get()) """
		r = requests.get(self.target_url, params=request.form)
		self.logger.info("GET %s | Data: %s | Return: %s", self.target_url, request.form, r.json())
		return r.json(), r.status_code
