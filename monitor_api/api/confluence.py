#!/usr/bin/env python3
# encoding=utf-8

""" Confluence API endpoints """


from typing import Dict, List, Tuple
import logging

from flask import request
from flask_restful import Resource, reqparse
import requests

import api.path
from api.base import WrappedResourceBase


BASE_URL = "http://vmpretschner28.informatik.tu-muenchen.de/"
API_BASE_PATH = "rest/api/"

# Paths – ? = not explored, o = explored, t = to implement, x = done
# (?) audit/
# (?) content/
# (?) group/
# (o) longtask
# (o) longtask/{id}
# (o) search
# (?) space/
# (?) user/
#
# Relative paths should be identical to the original API.


class ConfluenceApi(object):

	def __init__(self, logger_base:str):
		my_path:str = logger_base + ".confluence"
		self.logger = logging.getLogger(name=my_path)

		# TODO create all resources with the given logger attached

		# Resource, URL, kwargs
		search_name:str = "search"
		search_relative_url:str = api.path.join(API_BASE_PATH, search_name)

		self.resources:List[Tuple[Resource, str, Dict[str, object]]] = [
			(ConfluenceApi.SearchResource,
				search_relative_url,
				{"own_name" : search_name, "target_url" : api.path.join(BASE_URL, search_relative_url), "logger_base" : my_path}),
		]


	def get_resources(self) -> List[Tuple[Resource, str, Dict[str, object]]]:
		return self.resources


	class SearchResource(WrappedResourceBase):
		""" /search """

		def __init__(self, own_name:str, target_url:str, logger_base:str):
			super().__init__(own_name=own_name, target_url=target_url, logger_base=logger_base)

		def get(self):
			""" Search for entities in Confluence using the Confluence Query Language (CQL) """
			return self._get()
