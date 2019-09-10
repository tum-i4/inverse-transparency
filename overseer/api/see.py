# encoding=utf-8
""" <see> API class """

from flask_restful import Api

from api.base import IApi


class SeeApi(IApi):
	""" <see> endpoints | Inform the overseer about an incident. """

	def __init__(self):
		super().__init__()


	def add_resources(self, app_api:Api):
		""" See `IApi.add_resources` """
		raise NotImplementedError()
