#!/usr/bin/env python3
# encoding=utf-8

""" moduleinfo """

import logging

from flask import Flask
from flask_restful import Resource, Api

from api.confluence import ConfluenceApi

LOGGER_BASE:str = "mapi"

app = Flask(__name__)
api = Api(app)

if __name__ == "__main__":
	# Connect Confluence API
	confluence_base_path = "confluence/"
	for resource, relative_path in ConfluenceApi(logger_base=LOGGER_BASE).get_resources():
		api.add_resource(resource, confluence_base_path + relative_path)

	# TODO connect further APIs

	# Flask handles Ctrl-C
	app.run(debug=True)
