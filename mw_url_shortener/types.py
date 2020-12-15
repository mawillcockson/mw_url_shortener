print(f"imported mw_url_shortener.types as {__name__}")
"""
Holds all of the custom types used across the application
"""
from pathlib import Path
from typing import NewType, Union

from pydantic import constr

# DONE:NOTE:IMPLEMENTATION Should these be pydantic models instead?
# This would allow the password hashes to be validated, but passlib already
# checks this when they're used.
# A model can't be used for the PlainPassword since the password can be
# anything, including something that looks exactly like a password hash
# DONE:
# Type checking should be sufficient for making sure a PlainPassword never ends
# up in the wrong spot
HashedPassword = NewType("HashedPassword", str)
PlainPassword = NewType("PlainPassword", str)

# NOTE:IMPLEMENTATION Could have more defined types
Uri = NewType("Uri", constr(min_length=1))

# NOTE:TYPES I want to enforce constraints and validation (e.g. min_length),
# and have a default factory using .utils.unsafe_random_chars:
# https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types
Key = NewType("Key", constr(min_length=1))
Username = NewType("Username", constr(min_length=1))

SPath = Union[str, Path]
