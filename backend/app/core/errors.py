class UserSystemError(Exception):
    """Base domain exception."""


class ValidationError(UserSystemError):
    """Input validation error in service layer."""


class NotFoundError(UserSystemError):
    """Entity not found error."""


class ConflictError(UserSystemError):
    """Conflict error for duplicated resources."""


class UnauthorizedError(UserSystemError):
    """Unauthorized access."""
