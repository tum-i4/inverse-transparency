#!/usr/bin/env python3
# encoding=utf-8

""" Confluence API endpoints """


from typing import List, Tuple
import logging

from flask_restful import Resource


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
		self.logger = logging.getLogger(name=logger_base + ".confluence")
		# TODO create all resources with the given logger attached

	def get_resources(self) -> List[Tuple[Resource, str]]:
		return []
