#!.venv/bin/python3
# encoding=utf-8
""" Monitor API """

import logging

from flask import Flask
from flask_restful import Api

app = Flask(__name__)
app_api = Api(app)

if __name__ == "__main__":

	# Flask handles Ctrl-C
	app.run(debug=True)
