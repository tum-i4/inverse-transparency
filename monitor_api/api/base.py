#!/usr/bin/env python3
# encoding=utf-8
""" API wrapper base """

from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Optional, Tuple

from flask import request
from flask_restful import Resource
import requests

from api.auth import Authenticator
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

	def __init__(self, resource_name:str, api_name:str, logger_base:str, authenticator:Authenticator,
		target_url:Optional[str] = None, template_url:Optional[str] = None):
		"""
		:param target_url: A constant URL to target
		:param template_url: A template URL (with replaceable arg) to target
		"""

		if not (bool(target_url) ^ bool(template_url)):
			raise ValueError("Specify either target_url xor templater_url")

		self.target_url = target_url
		self.template_url = template_url
		self.logger = logging.getLogger(name=logger_base + "." + resource_name)
		self.authenticator = authenticator
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

		req = requests.Request("GET", self.target_url, params=request.args)
		# TODO Temp
		# req = requests.Request("GET", "http://httpbin.org/json")
		self.authenticator.authenticate(request=req)
		with requests.Session() as s:
			res = s.send(req.prepare())

		entry = Entry(method="GET", url=self.target_url, request_params=request.args.to_dict(flat=False), response_content=res.json())
		self.logger.info(entry)
		self.storage.add(entry)

		return res.json(), res.status_code
