#!/usr/bin/env python3
# encoding=utf-8

""" moduleinfo """

from flask import Flask
from flask_restful import Resource, Api

from api import confluence

app = Flask(__name__)
api = Api(app)

if __name__ == "__main__":
	# Connect Confluence API
	confluence_base_path = "confluence/"
	for resource, relative_path in confluence.RESOURCES:
		api.add_resource(resource, confluence_base_path + relative_path)

	# TODO connect further APIs

	# Flask handles Ctrl-C
	app.run(debug=True)
