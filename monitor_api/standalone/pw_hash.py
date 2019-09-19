#!/usr/bin/env python3
""" Generate password hash """

if __name__ != "__main__":
    raise ImportError("Can't import standalone script")

import argparse
import hashlib
import secrets
import sys

import api.sec

try:
    parser = argparse.ArgumentParser(prog="pw_hash")
    parser.add_argument("password", help="The password to hash")
    args = parser.parse_args()
    password: str = args.password

    pw_hash, salt = api.sec.password_hash_gen(password=password)

    print("Password hash: {}\nSalt: {}".format(pw_hash, salt))

except KeyboardInterrupt:
    # Exit code for Ctrl-C
    sys.exit(130)
