#!.venv/bin/python3
# encoding=utf-8
""" Monitor API """

if __name__ != "__main__":
    raise ImportError("This module may only be run, not imported")

import logging

from flask import Flask
from flask_restful import Api

from api.base import IApi
from api.see import SeeApi

app = Flask(__name__)
app_api = Api(app)

see_api: IApi = SeeApi()
see_api.add_resources(app_api=app_api)

# Flask handles Ctrl-C
app.run(debug=True, port="5421")
