print(f"imported mw_url_shortener.utils as {__name__}")
"""
module of utility functions

all of these functions can be loaded independently of the rest of this library,
except for the types
"""
import orjson
import random
import secrets
import string
from itertools import islice
from typing import Callable, Iterable
import random
import string
from mw_url_shortener.types import Username, HashedPassword
from typing import Iterable
import re
import sys
from passlib.context import CryptContext


__all__ = ["orjson_dumps", "orjson_loads", "unsafe_random_chars", "safe_random_chars", "random_username", "unsafe_random_hashed_password"]


def orjson_dumps(v, *, default):
    """
    orjson.dumps returns bytes, to match standard json.dumps we need to decode

    from:
    https://pydantic-docs.helpmanual.io/usage/exporting_models/#custom-json-deserialisation
    """
    return orjson.dumps(v, default=default).decode()


orjson_loads = orjson.loads


def make_unsafe_random_characters() -> Callable[[int], str]:
    """
    Returns a function that produces strings of specified length,
    composed of random characters
    """
    valid_chars = list(set(string.ascii_letters + string.digits))

    def char_gen() -> Iterable[str]:
        "makes an infinite generator of random characters"
        while True:
            yield random.choice(valid_chars)

    chars = char_gen()

    def unsafe(num: int) -> str:
        """
        produces a url-safe string of length num of random characters
        
        this function is not cryptographically safe
        """
        error_message = "unsafe_random_chars only takes positive integer values"
        try:
            length = int(num)
        except (TypeError, ValueError) as err:
            raise TypeError(error_message) from err

        if length < 1:
            raise ValueError(error_message)

        return "".join(islice(chars, int(num)))

    return unsafe


unsafe_random_chars = make_unsafe_random_characters()


def safe_random_chars(num_bytes: int) -> str:
    "Generates a random, url- and cryptographically-safe string of specified length"
    error_message = "safe_random_chars only takes positive integer values"
    try:
        length = int(num_bytes)
    except (TypeError, ValueError) as err:
        raise TypeError(error_message) from err

    if length < 1:
        raise ValueError(error_message)

    return secrets.token_hex(nbytes=length)


def unsafe_random_string(num: int) -> str:
    """
    generates a string of random unicode characters

    this is unlikely to be printable
    """
    error_message = "random_string only takes positive integer values"
    try:
        length = int(num)
    except (TypeError, ValueError) as err:
        raise TypeError(error_message) from err

    if length < 1:
        raise ValueError(error_message)

    return "".join([chr(random.randint(0, sys.maxunicode)) for x in range(num)])


def random_username(num: int) -> Username:
    "Generates a random username"
    return Username(unsafe_random_string(num))

# NOTE:DUP This needs to mirror the password context in authentication.py
# It can't be imported, both because this module should be standalone, and
# because I want to avoid import loops
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def unsafe_random_hashed_password() -> HashedPassword:
    """
    generates a password hash from random input

    the input is not from a cryptographically random source
    """
    return HashedPassword(password_context.hash(unsafe_random_string(random.randint(1, 100))))


def printable_characters_generator() -> Iterable[str]:
    """
    returns a generator that returns all printable unicode characters

    this is very computationally slow, so as to avoid excessive memory use
    """
    non_whitespace_re = re.compile(r"^[\S]+$")
    all_unicode_characters = (chr(o) for o in range(sys.maxunicode + 1))
    
    def character_gen() -> Iterable[str]:
        "iterates over range of unicode characters, filtering out unprintable ones"
        # NOTE:BUG This doesn't do what it claims to
        # It does not filter out all unicode control characters
        # A better approach may be a list of range(start, end+1) of the unwanted
        # parts of unicode
        for character in all_unicode_characters: # +1 so that the end is included
            if not non_whitespace_re.match(character):
                continue
            if len(repr(character)) != 3:
                continue

            yield character

    return character_gen()
