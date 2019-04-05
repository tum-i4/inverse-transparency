#!/usr/bin/env python3
# encoding=utf-8
""" API wrapper base """

from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Optional, Tuple

from flask import request
from flask_restful import Resource
import requests
import requests.auth

import api.tools
from log.entry import Entry
from log.store import Storage


class IApi(ABC):
	@abstractmethod
	def __init__(self, logger_base:str):
		raise NotImplementedError()

	@abstractmethod
	def get_resources(self) -> List[Tuple[Resource, str, Dict[str, object]]]:
		raise NotImplementedError()


class WrappedResourceBase(Resource):
	""" A wrapped resource that pipes and logs requests. """

	CONTENT_NOT_JSON_ERR:Tuple[Dict, int] = ({ "error_message" : "The API did not return JSON data" }, 500)

	def __init__(self,
		resource_name:str,
		api_name:str,
		logger_base:str,
		auth:requests.auth.AuthBase,
		target_url:Optional[str] = None,
		template_url:Optional[str] = None
	):
		"""
		:param target_url: A constant URL to target
		:param template_url: A template URL (with replaceable arg) to target
		"""

		if not (bool(target_url) ^ bool(template_url)):
			raise ValueError("Specify either target_url xor templater_url")

		self.target_url = target_url
		self.template_url = template_url
		self.logger = logging.getLogger(name=logger_base + "." + resource_name)
		self.auth = auth
		self.storage = Storage(filename="/var/log/mapi.log", api=api_name)

		# TODO debug
		self.logger.setLevel(logging.DEBUG)


	def _build_url(self, *args) -> str:
		"""
		Build or retrieve the URL to target.
		:param args: The URL args to merge with the template URL
		"""
		if self.target_url:
			return self.target_url
		elif self.template_url:
			# String formatting automatically raises in case of an invalid number of arguments
			return self.template_url % args
		else:
			raise RuntimeError("Both URL attributes not set")


	def _get(self):
		""" Wrapped GET (has to be explicitly linked to get()) """

		req = requests.Request("GET", self.target_url, params=request.args, auth=self.auth)

		with requests.Session() as s:
			# TODO The timeouts are very low for debug purposes – might need to be increased for production!
			response_requests = s.send(s.prepare_request(req), timeout=(0.1, 1))

		# TODO Check if the timeout was activated and warn?

		# We currently only process JSON data
		if not api.tools.requests_Response_is_json(response_requests):
			return WrappedResourceBase.CONTENT_NOT_JSON_ERR

		response_flask = api.tools.requests_Response_to_flask_Response(response_requests)
		response_requests.close()

		entry = Entry(method="GET", url=self.target_url, request_params=request.args.to_dict(flat=False), response_content=response_flask.get_json())
		self.logger.info(entry)
		self.storage.add(entry)

		return response_flask
