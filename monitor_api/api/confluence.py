#!/usr/bin/env python3
# encoding=utf-8

""" Confluence API endpoints """


from typing import List, Tuple
import logging

from flask import request
from flask_restful import Resource, reqparse
import requests

import api.path


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
		resources = [
			ConfluenceApi.SearchResource(logger_base=my_path, url_base=API_BASE_PATH, name="search"),
		]
		self.resources:List[Tuple[Resource, str]] = []
		for resource in resources:
			self.resources.append((resource, resource.url))


	def get_resources(self) -> List[Tuple[Resource, str]]:
		return self.resources


	class SearchResource(Resource):
		""" /search """

		def __init__(self, logger_base:str, url_base:str, name:str):
			self.__name__ = name
			self.url = api.path.join(url_base, self.__name__)
			self.logger = logging.getLogger(name=logger_base + ".search")

		def get(self):
			""" Search for entities in Confluence using the Confluence Query Language (CQL) """
			r = requests.get(self.url, params=request.form)
			return r.json(), r.status_code
