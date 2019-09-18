# encoding=utf-8
""" <see> API class """

from typing import Dict

from flask import request
from flask_restful import Api, Resource, reqparse

import dao
from api.base import IApi


class SeeApi(IApi):
    """ <see> endpoints | Inform the overseer about an incident. """

    def __init__(self):
        super().__init__()

    def add_resources(self, app_api: Api):
        """ See `IApi.add_resources` """
        app_api.add_resource(self.See, self.See.BASE_PATH)

    class See(Resource):
        """ The API resource /see """

        BASE_PATH = "/see"

        def post(self):
            parser = reqparse.RequestParser()
            parser.add_argument("do", required=True, help="Data owner")
            parser.add_argument("du", required=True, help="Data user")
            parser.add_argument("app", required=True, help="Affected app")
            parser.add_argument("data", required=True, help="Affected data")
            args: Dict = parser.parse_args(strict=True)

            dao.store(**args)

            return ("Got it", 200)
