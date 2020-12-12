print(f"imported mw_url_shortener.database.errors as {__name__}")
"""
collection of errors reported by the database interface
"""
__all__ = ["UserNotFoundError", "DatabaseError", "UserAlreadyExistsError", "BadConfigError"]


class DatabaseError(Exception):
    "generic database error from mw_url_shortener"
    pass


class UserNotFoundError(DatabaseError):
    pass


class UserAlreadyExistsError(DatabaseError):
    pass


class BadConfigError(DatabaseError):
    pass
