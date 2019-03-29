#!/usr/bin/env python3
# encoding=utf-8
""" Authenticatior classes """

import base64

from requests import Request


class Authenticator(object):
	""" Base class for various authenticators. """
	def authenticate(self, request:Request) -> None:
		""" Authenticate the given request. """
		raise NotImplementedError()


class BasicAuth(Authenticator):
	""" Basic authentication. """
	def __init__(self, user:str, password:str):
		self.auth_header = "Basic " + base64.b64encode(bytes(user + ":" + password, encoding="utf-8")).decode()

	def authenticate(self, request:Request) -> None:
		""" Authenticate the given request with basic authentication. """
		request.headers = {"Authorization" : self.auth_header}
