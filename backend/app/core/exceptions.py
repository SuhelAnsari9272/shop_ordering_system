"""
Custom exceptions used by the service layer.

Routes catch these and translate them into appropriate HTTP responses.
This keeps HTTP-specific concerns (status codes) out of the service layer,
which makes services reusable and easier to unit-test in isolation.
"""


class AppError(Exception):
    """Base class for all application-level errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""


class AlreadyExistsError(AppError):
    """Raised when attempting to create a resource that already exists (e.g. duplicate mobile)."""


class InvalidCredentialsError(AppError):
    """Raised when login credentials are incorrect."""


class InactiveAccountError(AppError):
    """Raised when a customer account has been deactivated."""


class ValidationError(AppError):
    """Raised for business-rule validation failures (e.g. empty cart, inactive product)."""


class AuthorizationError(AppError):
    """Raised when an authenticated user attempts an action they're not permitted to perform."""


class InvalidStatusTransitionError(AppError):
    """Raised when an order status transition is not allowed."""
