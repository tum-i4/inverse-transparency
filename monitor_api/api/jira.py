#!/usr/bin/env python3
# encoding=utf-8
""" JIRA API endpoints """

import json
import logging
from typing import Dict, List, Tuple

from flask_restful import Resource
import requests.auth

from api.auth import BasicAuth
from api.base import IApi, WrappedResourceBase
import api.path


API_BASE_PATH = "rest/"
# This part is not used for all API endpoints!
API_2_PATH = "api/2/"
with open("config.json", "r") as config:
	config_content = json.load(config)["jira"]
	BASE_URL = config_content["base_url"]
	USER = config_content["user"]
	PASSWORD = config_content["password"]


# Paths – ? = not explored, o = explored, t = to implement, x = done
# (?) ...
# (o) api/2/configuration
# (?) ...
#
# Relative paths should be identical to the original API.


class JiraApi(IApi):

	NAME = "jira"
	AUTH = requests.auth.HTTPBasicAuth(username=USER, password=PASSWORD)

	def __init__(self, logger_base:str):
		my_path:str = logger_base + "." + JiraApi.NAME
		self.logger = logging.getLogger(name=my_path)

		# TODO create all resources with the given logger attached

		# Resource, URL, kwargs
		self.resources:List[Tuple[Resource, str, Dict[str, object]]] = [
			(JiraApi.ConfigurationResource,
				JiraApi.ConfigurationResource.RELATIVE_URL,
				{"base_url" : BASE_URL, "logger_base" : my_path}),
		]

	def get_resources(self) -> List[Tuple[Resource, str, Dict[str, object]]]:
		return self.resources


	class ConfigurationResource(WrappedResourceBase):
		""" api/2/configuration """

		NAME = "configuration"
		RELATIVE_URL = api.path.join(API_BASE_PATH, API_2_PATH, NAME)

		def __init__(self, base_url:str, logger_base:str):
			super().__init__(
				resource_name=self.NAME,
				api_name=JiraApi.NAME,
				target_url=api.path.join(base_url, self.RELATIVE_URL),
				logger_base=logger_base,
				auth=JiraApi.AUTH
			)

		def get(self):
			""" Returns the information if the optional features in JIRA are enabled or disabled. """
			return self._get()
