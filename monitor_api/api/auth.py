# encoding=utf-8
""" API authentication """

from typing import Dict, List, Tuple


# TODO We currently fake a user DB with this
_USERS:Dict[str, Tuple[str, str, str, bytes]] = {
	# user_key : First, Last, password_hash, password_salt # password
	"frauke"   : ("Frauke", "Mahna",          "ef736a966ab9eb44d90e49867fc7dd5c", b'A\xa6\xf35\xdd\xe6\x05\xb4'), # 1234
	"valentin" : ("Valentin", "Admin",        "dd9dd401c1a7fd23506e6462f5718ce6", b';\xa3\x9c\xe6\x10\xd7\xad\x0c'), # super-secure-password
	"somebody" : ("Somebody Once", "Told Me", "dacb2aab01d6bbc4db5ec7b086ec285a", b'\x92\xe1#\xac2(\xca\x82'), # pwd
}
