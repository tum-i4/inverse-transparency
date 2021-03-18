import logging
from contextlib import contextmanager

from fastapi import HTTPException

from overseer.services import IdMappingError
from starlette.status import HTTP_400_BAD_REQUEST

logger = logging.getLogger(__name__)


@contextmanager
def http_exception(exc_type: type, status_code: int, detail: str = None):
    """
    Context manager for reraising exceptions as HTTPExceptions
    """
    try:
        yield
    except Exception as exc:
        if isinstance(exc, exc_type):
            logger.exception(exc)
            raise HTTPException(status_code, detail) from exc
        else:
            raise


def handle_user_not_signed_up():
    return http_exception(
        IdMappingError, HTTP_400_BAD_REQUEST, "User is not signed up with Revolori."
    )


def handle_owner_not_signed_up():
    return http_exception(
        IdMappingError,
        HTTP_400_BAD_REQUEST,
        "One or more owners are not signed up with Revolori.",
    )
