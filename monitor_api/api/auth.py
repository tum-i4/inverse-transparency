# encoding=utf-8
""" API authentication """

from abc import ABC, abstractmethod
import base64
import re
import secrets
from typing import Dict, List, Tuple

import flask

import api.sec


# TODO We currently fake a user DB with this
_USERS:Dict[str, Tuple[str, str, str, bytes]] = {
	# user_key : First, Last, password_hash, password_salt # password
	"frauke"   : ("Frauke", "Mahna",          "ef736a966ab9eb44d90e49867fc7dd5c", b'A\xa6\xf35\xdd\xe6\x05\xb4'), # 1234
	"valentin" : ("Valentin", "Admin",        "dd9dd401c1a7fd23506e6462f5718ce6", b';\xa3\x9c\xe6\x10\xd7\xad\x0c'), # super-secure-password
	"somebody" : ("Somebody Once", "Told Me", "dacb2aab01d6bbc4db5ec7b086ec285a", b'\x92\xe1#\xac2(\xca\x82'), # pwd
}


class Auth(ABC):
	""" Authenticate requests """

	@abstractmethod
	@staticmethod
	def get_user_readable(request:flask.Request) -> str:
		""" Return a readable representation of the user that authorized the given request. """
		raise NotImplementedError()

	@abstractmethod
	@staticmethod
	def is_authorized_flask_req(request:flask.Request) -> bool:
		""" Verify securely whether the given request contains authorization corresponding to an authorized user. """
		raise NotImplementedError()


class BasicAuth(Auth):
	""" Authenticate requests using HTTP Basic Authentication """

	@staticmethod
	def user_password_from(basic_auth_header:str) -> Tuple[str, str]:
		""" Extract user and password from the given BasicAuth header. """

		if not re.fullmatch(r"Basic\s\S+", basic_auth_header):
			raise ValueError("Given input does not correspond to expected format")

		b64str:str = basic_auth_header[6:]
		decoded_auth:str = base64.b64decode(b64str).decode(encoding="utf-8")
		user, password = decoded_auth.split(":")
		return user, password


	@staticmethod
	def is_authorized_header(basic_auth_header:str) -> bool:
		user, password = BasicAuth.user_password_from(basic_auth_header)

		if not user in _USERS:
			return False

		_, _, pw_hash, pw_salt = _USERS[user]
		received_pw_hash:str = api.sec.password_hash(password=password, salt=pw_salt)

		return secrets.compare_digest(pw_hash, received_pw_hash)


	@staticmethod
	def is_authorized_flask_req(request:flask.Request) -> bool:
		auth_key = "Authorization"
		if auth_key not in request.headers:
			return False
		basic_auth_header = request.headers[auth_key]
		return BasicAuth.is_authorized_header(basic_auth_header)
