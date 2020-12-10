print(f"imported mw_url_shortener.utils as {__name__}")
"""
module of utility functions

all of these functions can be loaded independently of the rest of this library
"""
import orjson
import random
import secrets
import string
from itertools import islice
from typing import Callable, Iterable


__all__ = ["orjson_dumps", "orjson_loads", "unsafe_random_chars", "safe_random_chars"]


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
        produces a string of length num of random characters
        
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
    "Generates a random, url-safe string of specified length"
    error_message = "safe_random_chars only takes positive integer values"
    try:
        length = int(num_bytes)
    except (TypeError, ValueError) as err:
        raise TypeError(error_message) from err

    if length < 1:
        raise ValueError(error_message)

    return secrets.token_hex(nbytes=length)
