#!.venv/bin/python3
# encoding=utf-8
""" Monitor API """

import logging

from api.base import IApi
from api.see import SeeApi
from flask import Flask
from flask_restful import Api

app = Flask(__name__)
app_api = Api(app)

if __name__ == "__main__":

    see_api: IApi = SeeApi()
    see_api.add_resources(app_api=app_api)

    # Flask handles Ctrl-C
    app.run(debug=True)
