#!/usr/bin/env python3

import argparse
import datetime as dt
import os
import subprocess

import uvicorn

import jwt


def create_key_pair():
    try:
        # fmt: off
        subprocess.call(["openssl", "ecparam", "-name", "secp384r1", "-genkey", "-noout", "-out", "issuer"])
        subprocess.call(["openssl", "ec", "-in", "issuer", "-pubout", "-out", "issuer.pub"])
        # fmt: on
    except Exception as exc:
        raise AssertionError("Make sure OpenSSL is installed.") from exc


def print_jwt_token(key, user):
    content = {
        "sub": user,
        "exp": (dt.datetime.now() + dt.timedelta(days=30)).timestamp(),
    }
    token = jwt.encode(content, key, algorithm="ES384")
    print(f"{user}:")
    print(f"{token.decode()}")
    print()


def setup_environment():
    os.environ["ADMIN_USER"] = "admin"
    os.environ["ADMIN_USER_PASSWORD"] = "admin"
    os.environ["TECHNICAL_USER"] = "tech"
    os.environ["TECHNICAL_USER_PASSWORD"] = "tech"
    os.environ["DATABASE_URI"] = "sqlite:///data.db"
    os.environ["JWT_ALGORITHM"] = "ES384"
    os.environ["JWT_PUBLIC_KEY_PATH"] = "issuer.pub"
    os.environ["REVOLORI_SERVICE_ROOT"] = "http://localhost:5429"


def create_keys_if_not_existent():
    if not os.path.isfile("issuer.pub") or not os.path.isfile("issuer"):
        create_key_pair()


def read_private_key():
    with open("issuer", "rb") as file:
        return file.read()


if __name__ == "__main__":
    setup_environment()
    create_keys_if_not_existent()
    private_key = read_private_key()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-service-deps",
        dest="no_service_deps",
        action="store_true",
        help="start the dev server without any dependencies on external services",
    )
    args = parser.parse_args()

    parser.print_help()
    print()
    print("JWT tokens:")
    print_jwt_token(private_key, "user1@example.com")
    print_jwt_token(private_key, "user2@example.com")
    print_jwt_token(private_key, "user3@example.com")
    print()

    entry = (
        "no_service_deps:overseer" if args.no_service_deps else "overseer.main:overseer"
    )

    uvicorn.run(entry, host="127.0.0.1", port=5421, log_level="info", reload=True)
