# encoding=utf-8
""" <see> API class """

from flask import request
from flask_restful import Api, Resource, reqparse

from api.base import IApi


class SeeApi(IApi):
	""" <see> endpoints | Inform the overseer about an incident. """

	def __init__(self):
		super().__init__()


	def add_resources(self, app_api:Api):
		""" See `IApi.add_resources` """
		app_api.add_resource(self.See, self.See.BASE_PATH)


	class See(Resource):
		""" The API resource /see """

		BASE_PATH = "/see"

		def put(self):
			raise NotImplementedError()
