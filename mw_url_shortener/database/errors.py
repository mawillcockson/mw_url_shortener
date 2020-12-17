print(f"imported mw_url_shortener.database.errors as {__name__}")
"""
collection of errors reported by the database interface
"""
__all__ = [
    "BadConfigInDBError",
    "DatabaseError",
    "DuplicateKeyError",
    "DuplicateThresholdError",
    "RedirectNotFoundError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
]


class DatabaseError(Exception):
    "generic database error from mw_url_shortener"
    pass


class UserNotFoundError(DatabaseError):
    pass


class UserAlreadyExistsError(DatabaseError):
    pass


class BadConfigInDBError(DatabaseError):
    pass


class RedirectNotFoundError(DatabaseError):
    pass


class DuplicateKeyError(DatabaseError):
    pass


class DuplicateThresholdError(DatabaseError):
    pass
