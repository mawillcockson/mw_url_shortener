print(f"imported mw_url_shortener.__init__ as {__name__}")
import sys
from typing import NewType
from pydantic import constr

# From:
# https://github.com/mawillcockson/eggord/blob/ea7e56ce173561a550a08b67a9dafdaec149ff17/eggord/__init__.py
if sys.version_info >= (3, 8):
    from importlib.metadata import version as metadata_version
else:
    from importlib_metadata import version as metadata_version

__version__ = str(metadata_version(__name__))


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
# and have a default factory using .random_chars.unsafe_random_chars:
# https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types
Key = NewType("Key", constr(min_length=1))
Username = NewType("Username", str)
