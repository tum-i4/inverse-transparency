#!/usr/bin/env python3
# encoding=utf-8

""" Generate password hash """

import argparse
import hashlib
import secrets
import sys


if __name__ == "__main__":
	try:
		parser = argparse.ArgumentParser(prog="pw_hash")
		parser.add_argument("password", help="The password to hash")
		parser.add_argument("--size", type=int, default=16, help="Size in bytes; in [0, 64]")
		args = parser.parse_args()
		password:str = args.password
		size:int = args.size

		salt:bytes = secrets.token_bytes(8)
		pw_hash:str = hashlib.blake2b(bytes(password, encoding="utf-8"), salt=salt, digest_size=size).hexdigest()

		print("Password hash ({} Byte): {}\nSalt: {}".format(size, pw_hash, salt))

	except KeyboardInterrupt:
		# Exit code for Ctrl-C
		sys.exit(130)
else:
	raise ImportError("Can't import standalone script")
