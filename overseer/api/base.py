# encoding=utf-8
""" API base """

from abc import ABC, abstractmethod

from flask_restful import Api


class IApi(ABC):
	@abstractmethod
	def add_resources(self, app_api:Api):
		raise NotImplementedError()
