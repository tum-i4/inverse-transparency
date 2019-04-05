# encoding=utf-8
""" API authentication """

import base64
import re
import secrets
from typing import Dict, List, Tuple

import api.sec


# TODO We currently fake a user DB with this
_USERS:Dict[str, Tuple[str, str, str, bytes]] = {
	# user_key : First, Last, password_hash, password_salt # password
	"frauke"   : ("Frauke", "Mahna",          "ef736a966ab9eb44d90e49867fc7dd5c", b'A\xa6\xf35\xdd\xe6\x05\xb4'), # 1234
	"valentin" : ("Valentin", "Admin",        "dd9dd401c1a7fd23506e6462f5718ce6", b';\xa3\x9c\xe6\x10\xd7\xad\x0c'), # super-secure-password
	"somebody" : ("Somebody Once", "Told Me", "dacb2aab01d6bbc4db5ec7b086ec285a", b'\x92\xe1#\xac2(\xca\x82'), # pwd
}


def is_authorized_header(basic_auth_header:str) -> bool:
	""" Verify securely whether the given authorization corresponds to an authorized user. """

	if not re.fullmatch(r"Basic\s\S+", basic_auth_header):
		raise ValueError("Given input does not correspond to expected format")

	b64str:str = basic_auth_header[6:]
	decoded_auth:str = base64.b64decode(b64str).decode(encoding="utf-8")
	user, password = decoded_auth.split(":")

	if not user in _USERS:
		return False

	_, _, pw_hash, pw_salt = _USERS[user]
	received_pw_hash:str = api.sec.password_hash(password=password, salt=pw_salt)

	return secrets.compare_digest(pw_hash, received_pw_hash)
