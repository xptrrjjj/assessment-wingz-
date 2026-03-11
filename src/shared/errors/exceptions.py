from rest_framework import status


class ApplicationError(Exception):
    """Base exception for all application errors."""

    default_detail = "An unexpected error occurred."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail=None, extra=None):
        self.detail = detail or self.default_detail
        self.extra = extra or {}
        super().__init__(self.detail)


class ValidationError(ApplicationError):
    default_detail = "Invalid input."
    status_code = status.HTTP_400_BAD_REQUEST


class AuthenticationError(ApplicationError):
    default_detail = "Authentication credentials were not provided or are invalid."
    status_code = status.HTTP_401_UNAUTHORIZED


class PermissionDeniedError(ApplicationError):
    default_detail = "You do not have permission to perform this action."
    status_code = status.HTTP_403_FORBIDDEN


class NotFoundError(ApplicationError):
    default_detail = "The requested resource was not found."
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(ApplicationError):
    default_detail = "This action conflicts with the current state."
    status_code = status.HTTP_409_CONFLICT


class RateLimitError(ApplicationError):
    default_detail = "Too many requests. Please try again later."
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
