"""
Maps domain-level exceptions (app.core.exceptions) to FastAPI HTTPExceptions.

Routes call domain services inside a try/except and use `raise_http_error`
in the except block, OR we register these as FastAPI exception handlers in
main.py so routes don't need try/except at all. We do both for clarity:
the global handlers in main.py are the primary mechanism; this module
documents the mapping in one place.
"""
from fastapi import status

from app.core.exceptions import (
    AlreadyExistsError,
    AppError,
    AuthorizationError,
    InactiveAccountError,
    InvalidCredentialsError,
    InvalidStatusTransitionError,
    NotFoundError,
    ValidationError,
)

EXCEPTION_STATUS_MAP: dict[type[AppError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    AlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    InactiveAccountError: status.HTTP_403_FORBIDDEN,
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    InvalidStatusTransitionError: status.HTTP_409_CONFLICT,
}


def status_code_for(exc: AppError) -> int:
    return EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
