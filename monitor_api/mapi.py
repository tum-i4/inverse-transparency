#!/usr/bin/env python3
# encoding=utf-8

""" moduleinfo """

import logging

from flask import Flask
from flask_restful import Resource, Api

from api.confluence import ConfluenceApi
import api.path

MY_LOGGER_PATH = "mapi"
API_BASE_PATH = ""

app = Flask(__name__)
app_api = Api(app)

if __name__ == "__main__":
	# TODO configure logger
	logging.basicConfig(
		format="%(asctime)s (%(name)s | %(levelname)s) \"%(message)s\"",
		datefmt="%Y-%m-%dT%H:%M:%S%z"
	)
	logger = logging.getLogger(MY_LOGGER_PATH)
	logger.info("Initializing API")

	# Connect Confluence API
	confluence_base_path = api.path.join(API_BASE_PATH, "confluence")
	for resource, relative_path in ConfluenceApi(logger_base=MY_LOGGER_PATH).get_resources():
		app_api.add_resource(resource, api.path.join(confluence_base_path, relative_path))

	# TODO connect further APIs

	# Flask handles Ctrl-C
	app.run(debug=True)
