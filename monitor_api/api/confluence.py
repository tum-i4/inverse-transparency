# encoding=utf-8
""" Confluence API endpoints """

import json
import logging
from typing import Dict, List, Tuple

from flask import request
from flask_restful import Resource, reqparse
import requests
import requests.auth

from api.base import IApi, WrappedResourceBase
import api.path


API_BASE_PATH = "rest/api/"
with open("config.json", "r") as config:
	config_content = json.load(config)["confluence"]
	BASE_URL = config_content["base_url"]
	USER = config_content["user"]
	PASSWORD = config_content["password"]


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


class ConfluenceApi(IApi):

	NAME = "confluence"
	AUTH = requests.auth.HTTPBasicAuth(username=USER, password=PASSWORD)

	def __init__(self, logger_base:str):
		my_path:str = logger_base + "." + ConfluenceApi.NAME
		self.logger = logging.getLogger(name=my_path)

		# TODO create all resources with the given logger attached

		# Resource, URL, kwargs
		self.resources:List[Tuple[Resource, str, Dict[str, object]]] = [
			(ConfluenceApi.SearchResource,
				ConfluenceApi.SearchResource.RELATIVE_URL,
				{"base_url" : BASE_URL, "logger_base" : my_path}),
			(ConfluenceApi.ContentIdHistoryResource,
				ConfluenceApi.ContentIdHistoryResource.RELATIVE_URL,
				{"base_url" : BASE_URL, "logger_base" : my_path}),
		]


	def get_resources(self) -> List[Tuple[Resource, str, Dict[str, object]]]:
		return self.resources


	class SearchResource(WrappedResourceBase):
		""" /search """

		NAME = "search"
		RELATIVE_URL = api.path.join(API_BASE_PATH, NAME)

		def __init__(self, base_url:str, logger_base:str):
			super().__init__(
				resource_name=self.NAME,
				api_name=ConfluenceApi.NAME,
				target_url=api.path.join(base_url, self.RELATIVE_URL),
				logger_base=logger_base,
				auth=ConfluenceApi.AUTH,
			)

		def get(self):
			""" Search for entities in Confluence using the Confluence Query Language (CQL). """
			return self._get()


	class ContentIdHistoryResource(WrappedResourceBase):
		""" /content/{id}/history """

		NAME = "content_history"
		_TEMPLATE_URL = api.path.join(API_BASE_PATH, "content", "%s", "history")
		RELATIVE_URL = _TEMPLATE_URL % "<int:id>"

		def __init__(self, base_url:str, logger_base:str):
			super().__init__(
				resource_name=self.NAME,
				api_name=ConfluenceApi.NAME,
				logger_base=logger_base,
				auth=ConfluenceApi.AUTH,
				template_url=api.path.join(base_url, self._TEMPLATE_URL),
			)

		def get(self, id):
			""" Return the history of a particular piece of content. """
			self.target_url = self._build_url(id)
			return self._get()
