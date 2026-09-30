"""Domain-level exceptions.

These exceptions carry no knowledge of HTTP, FastAPI or any transport
concern. The API layer is responsible for translating them into HTTP
responses (see app/api/error_handlers.py).
"""


class DomainError(Exception):
    """Base class for all business-rule violations."""

    code: str = "DOMAIN_ERROR"

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(DomainError):
    code = "NOT_FOUND"


class ConflictError(DomainError):
    """Raised when an operation would violate a business invariant
    (e.g. duplicate team in a pool, scheduling on top of played matches)."""

    code = "CONFLICT"


class InvalidStateError(DomainError):
    """Raised when an operation is attempted on an entity in a state
    that does not allow it (e.g. modifying a CLOSED competition)."""

    code = "INVALID_STATE"


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
