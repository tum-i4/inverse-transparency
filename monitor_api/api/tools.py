#!/usr/bin/env python3
# encoding=utf-8
""" Low-level tools """

import flask
import requests
import werkzeug.datastructures as wz_ds

def requests_Response_to_flask_Response(req_response:requests.Response) -> flask.Response:
	""" Convert a `requests.Response` object to a `flask.Response` object. """
	raise NotImplementedError()


def requests_Response_is_json(req_response:requests.Response) -> bool:
	""" Safely determine whether the given response consists of JSON data. """

	if not req_response.headers["content-type"] == "application/json":
		return False

	try:
		req_response.json()
	except ValueError:
		return False

	return True
