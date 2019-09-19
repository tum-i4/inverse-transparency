""" API authentication """

import base64
import re
import secrets
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

import flask

import api.sec

# TODO We currently fake a user DB with this
_USERS: Dict[str, Tuple[str, str, str, bytes]] = {
    # user_key : First, Last, password_hash, password_salt # password
    "frauke": (
        "Frauke",
        "Mahna",
        "ef736a966ab9eb44d90e49867fc7dd5c",
        b"A\xa6\xf35\xdd\xe6\x05\xb4",
    ),  # Password: 1234
    "valentin": (
        "Valentin",
        "Admin",
        "dd9dd401c1a7fd23506e6462f5718ce6",
        b";\xa3\x9c\xe6\x10\xd7\xad\x0c",
    ),  # Password: super-secure-password
    "somebody": (
        "Somebody Once",
        "Told Me",
        "dacb2aab01d6bbc4db5ec7b086ec285a",
        b"\x92\xe1#\xac2(\xca\x82",
    ),  # Password: pwd
}


class Auth(ABC):
    """ Authenticate requests """

    @staticmethod
    @abstractmethod
    def get_user_readable(request: flask.Request) -> str:
        """ Return a readable representation of the user that authorized the given request. """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def is_authorized_request(request: flask.Request) -> bool:
        """ Verify securely whether the given request contains authorization corresponding to an authorized user. """
        raise NotImplementedError()


class BasicAuth(Auth):
    """ Authenticate requests using HTTP Basic Authentication """

    @staticmethod
    def user_password_from(basic_auth_header: str) -> Tuple[str, str]:
        """ Extract user and password from the given BasicAuth header. """

        if not re.fullmatch(r"Basic\s\S+", basic_auth_header):
            raise ValueError("Given input does not correspond to expected format")

        b64str: str = basic_auth_header[6:]
        decoded_auth: str = base64.b64decode(b64str).decode(encoding="utf-8")
        user, password = decoded_auth.split(":")
        return user, password

    @staticmethod
    def auth_header_from(request: flask.Request) -> Optional[str]:
        """ Return the BasicAuth header; None if not present. """
        auth_key = "Authorization"
        if auth_key not in request.headers:
            return None
        return request.headers[auth_key]

    @staticmethod
    def get_user_readable(request: flask.Request) -> str:
        basic_auth_header = BasicAuth.auth_header_from(request)
        if not basic_auth_header:
            raise ValueError("Given request does not contain a HTTP Basic Auth header!")

        user, _ = BasicAuth.user_password_from(basic_auth_header)
        first, last, _, _ = _USERS[user]
        return last + ", " + first

    @staticmethod
    def is_authorized_header(basic_auth_header: str) -> bool:
        user, password = BasicAuth.user_password_from(basic_auth_header)

        if not user in _USERS:
            return False

        _, _, pw_hash, pw_salt = _USERS[user]
        received_pw_hash: str = api.sec.password_hash(password=password, salt=pw_salt)

        return secrets.compare_digest(pw_hash, received_pw_hash)

    @staticmethod
    def is_authorized_request(request: flask.Request) -> bool:
        basic_auth_header = BasicAuth.auth_header_from(request)
        if not basic_auth_header:
            return False
        return BasicAuth.is_authorized_header(basic_auth_header)
