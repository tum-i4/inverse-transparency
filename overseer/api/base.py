""" API base """

from abc import ABC, abstractmethod

from flask_restful import Api


class IApi(ABC):
    """ Interface for API classes """

    @abstractmethod
    def add_resources(self, app_api: Api):
        """ Adds own resources to the given app API. """
        raise NotImplementedError()
