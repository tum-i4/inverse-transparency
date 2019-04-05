# encoding=utf-8
""" Security-related functions """

import hashlib
import secrets
from typing import Tuple


def password_hash(password:str, salt:bytes, size:int = 16) -> str:
	""" Generate salt, hash, return both. """
	pw_hash:str = hashlib.blake2b(bytes(password, encoding="utf-8"), salt=salt, digest_size=size).hexdigest()
	return pw_hash


def password_hash_gen(password:str, salt_size:int = 8, size:int = 16) -> Tuple[str, bytes]:
	""" Generate salt, hash, return both. """
	salt = secrets.token_bytes(8)
	pw_hash:str = password_hash(password=password, salt=salt, size=size)
	return pw_hash, salt
