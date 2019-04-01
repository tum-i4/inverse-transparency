#!/usr/bin/env python3
# encoding=utf-8
""" API wrapper base """

from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Tuple

from flask import request
from flask_restful import Resource
import requests

from api.auth import Authenticator
from log.entry import Entry


class AnyApi(ABC):
	@abstractmethod
	def __init__(self, logger_base:str):
		raise NotImplementedError()

	@abstractmethod
	def get_resources(self) -> List[Tuple[Resource, str, Dict[str, object]]]:
		raise NotImplementedError()


class WrappedResourceBase(Resource):
	""" A wrapped resource that pipes and logs requests. """

	def __init__(self, own_name:str, target_url:str, logger_base:str, authenticator:Authenticator):
		self.target_url = target_url
		self.logger = logging.getLogger(name=logger_base + "." + own_name)
		self.authenticator = authenticator
		# TODO debug
		self.logger.setLevel(logging.DEBUG)


	def _get(self):
		""" Wrapped GET (has to be explicitly linked to get()) """

		req = requests.Request("GET", self.target_url, params=request.args)
		self.authenticator.authenticate(request=req)
		res = requests.Session().send(req.prepare())

		self.logger.info(Entry(method="GET", url=self.target_url, request_params=request.args.to_dict(flat=False), response_content=res.json()))

		return res.json(), res.status_code
