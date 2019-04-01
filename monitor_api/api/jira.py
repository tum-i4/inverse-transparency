#!/usr/bin/env python3
# encoding=utf-8
""" JIRA API endpoints """

import json
import logging
from typing import Dict, List, Tuple

from flask_restful import Resource

from api.auth import BasicAuth
from api.base import AnyApi, WrappedResourceBase
import api.path


# This base is not used for all API endpoints!
API_BASE_PATH = "rest/api/2/"
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


class JiraApi(AnyApi):

	def __init__(self, logger_base:str):
		my_path:str = logger_base + ".jira"
		self.logger = logging.getLogger(name=my_path)

		# TODO create all resources with the given logger attached

		# Resource, URL, kwargs
		self.resources:List[Tuple[Resource, str, Dict[str, object]]] = [
		]

	def get_resources(self) -> List[Tuple[Resource, str, Dict[str, object]]]:
		return self.resources
