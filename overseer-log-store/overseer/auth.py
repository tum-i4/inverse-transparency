import secrets
from os import path
from typing import Mapping

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBearer
from pydantic import BaseModel, ValidationError

import jwt
from jwt import InvalidTokenError
from overseer.models import RevoloriId
from overseer.settings import settings
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED


class JWTAuthenticationCredentials(BaseModel):
    user_rid: RevoloriId


class JWTBearer(HTTPBearer):
    def __init__(self, algorithm: str, issuer_public_key: bytes):
        super().__init__(auto_error=False)
        self._algorithm = algorithm
        self._issuer_public_key = issuer_public_key

    async def __call__(self, request: Request) -> JWTAuthenticationCredentials:
        credentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )

        token = self._parse_token(credentials.credentials)
        return self._parse_claims(token)

    def _parse_token(self, credentials: str) -> Mapping:
        try:
            return jwt.decode(
                credentials,
                self._issuer_public_key,
                algorithms=[self._algorithm],
                options={"require_exp": True, "verify_exp": True},
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    @staticmethod
    def _parse_claims(token: Mapping) -> JWTAuthenticationCredentials:
        try:
            return JWTAuthenticationCredentials(user_rid=token["sub"])
        except (ValidationError, KeyError):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid claims"
            )


def read_pub_key(pub_key_path: str) -> bytes:
    abspath = path.abspath(pub_key_path)
    with open(abspath, "rb") as file:
        return file.read()


jwt_auth = JWTBearer(settings.JWT_ALGORITHM, read_pub_key(settings.JWT_PUBLIC_KEY_PATH))


def get_current_user(credentials: JWTAuthenticationCredentials = Depends(jwt_auth)):
    return credentials.user_rid


class RequiredLogin(HTTPBasic):
    def __init__(self, scheme_name: str, username: str, password: str):
        super().__init__(scheme_name=scheme_name)
        self._username = username
        self._password = password

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)

        correct_username = secrets.compare_digest(credentials.username, self._username)
        correct_password = secrets.compare_digest(credentials.password, self._password)
        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )


technical_user_logged_in = RequiredLogin(
    "Technical User", settings.TECHNICAL_USER, settings.TECHNICAL_USER_PASSWORD
)

admin_user_logged_in = RequiredLogin(
    "Admin", settings.ADMIN_USER, settings.ADMIN_USER_PASSWORD
)
