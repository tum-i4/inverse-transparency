#!/usr/bin/env python3

import os
import urllib.parse

from pydantic import BaseSettings, validator

SQLITE_PREFIX = "sqlite:///"


class Settings(BaseSettings):
    """ Class for reading settings from environment """

    ADMIN_USER: str
    ADMIN_USER_PASSWORD: str
    """
    Username and password for generating test data using the `/generate` endpoint.
    """

    TECHNICAL_USER: str
    TECHNICAL_USER_PASSWORD: str
    """
    Username and password for requesting data access.
    """

    JWT_ALGORITHM: str
    JWT_PUBLIC_KEY_PATH: str
    """
    Path to the public key of the JWT issuer, as well as,
    the algorithm which is used for signing the tokens.
    """

    REVOLORI_SERVICE_ROOT: str
    """
    URL where Revolori is deployed
    """

    DATABASE_URI: str
    """
    SQLite connection string.
    """

    @validator("DATABASE_URI")
    def validate_sqlite_uri(cls, uri: str) -> str:
        if uri[: len(SQLITE_PREFIX)] != SQLITE_PREFIX:
            raise ValueError("Expected a sqlite uri.")

        path = os.path.abspath(uri[len(SQLITE_PREFIX) :])
        directory = os.path.dirname(path)

        if not os.path.isdir(directory):
            raise ValueError(f"{directory} does not exist.")

        return uri

    @property
    def REVOLORI_ID_ENDPOINT(self):
        return urllib.parse.urljoin(self.REVOLORI_SERVICE_ROOT, "/id")


settings = Settings()
