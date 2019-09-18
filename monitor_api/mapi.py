#!.venv/bin/python3
# encoding=utf-8
""" Monitor API """

if __name__ != "__main__":
    raise ImportError("This module may only be run, not imported")

import logging
import sys

import apiu.path
import requests
from flask import Flask
from flask_restful import Api

from api.confluence import ConfluenceApi
from api.jira import JiraApi
import log.format
from see import OVERSEER_URL

MY_LOGGER_PATH = "mapi"
API_BASE_PATH = ""

app = Flask(__name__)
app_api = Api(app)

# TODO configure logger
logging.basicConfig(
    format=log.format.READABLE_LOG_FORMAT, datefmt=log.format.ISO_DATE_FORMAT
)
logger = logging.getLogger(MY_LOGGER_PATH)

# Connect Confluence API
logger.info("Initializing Confluence API")
confluence_base_path = apiu.path.join(API_BASE_PATH, "confluence")
for resource, relative_path, kwargs_dict in ConfluenceApi(
    logger_base=MY_LOGGER_PATH
).get_resources():
    app_api.add_resource(
        resource,
        apiu.path.join(confluence_base_path, relative_path),
        resource_class_kwargs=kwargs_dict,
    )

# Connect JIRA API
logger.info("Initializing JIRA API")
jira_base_path = apiu.path.join(API_BASE_PATH, "jira")
for resource, relative_path, kwargs_dict in JiraApi(
    logger_base=MY_LOGGER_PATH
).get_resources():
    app_api.add_resource(
        resource,
        apiu.path.join(jira_base_path, relative_path),
        resource_class_kwargs=kwargs_dict,
    )

# TODO connect further APIs

# Try to connect to Overseer
try:
    requests.get(OVERSEER_URL)
except requests.exceptions.ConnectionError:
    print(f"Overseer not reachable at {OVERSEER_URL}")
    sys.exit(1)

# Flask handles Ctrl-C
app.run(debug=True)
