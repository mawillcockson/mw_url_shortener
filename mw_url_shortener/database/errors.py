print(f"imported mw_url_shortener.database.errors as {__name__}")
"""
collection of errors reported by the database interface
"""
from .interface import UserNotFoundError, DatabaseError, UserAlreadyExistsError


__all__ = ["UserNotFoundError", "DatabaseError", "UserAlreadyExistsError"]
