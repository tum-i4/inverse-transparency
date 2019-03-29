#!/usr/bin/env python3
# encoding=utf-8
""" Authenticatior classes """

from requests import Request


class Authenticator(object):
	""" Base class for various authenticators. """
	def authenticate(self, request:Request) -> None:
		""" Authenticate the given request. """
		raise NotImplementedError()
