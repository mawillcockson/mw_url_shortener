"""
module of utility functions

all of these functions can be loaded independently of the rest of this library
"""
import secrets
import string
from math import floor
from random import choices, random
from sys import maxunicode as LARGEST_UNICODE_CODEPOINT
from typing import List

LARGEST_UNICODE_CODEPOINT_PLUS_ONE = LARGEST_UNICODE_CODEPOINT + 1


def unsafe_random_unicode_codepoints(length: int) -> List[int]:
    "returns `length` random integers in the range [0, maxunicode]"
    return [floor(LARGEST_UNICODE_CODEPOINT_PLUS_ONE * random()) for _ in range(length)]


def unsafe_random_string(length: int) -> str:
    "returns a string of `length` random unicode codepoints"
    return "".join(map(chr, unsafe_random_unicode_codepoints(length)))


def unsafe_random_string_from_pool(length: int, allowed_characters: str) -> str:
    "use only allowed characters"
    return "".join(choices(allowed_characters, k=length))


def unsafe_random_printable_string(length: int) -> str:
    "returns `length` random printable ASCII characters"
    return unsafe_random_string_from_pool(
        length=length, allowed_characters=string.printable
    )


def safe_random_string(num_bytes: int) -> str:
    "returns a random, url- and cryptographically-safe string of specified length"
    error_message = "safe_random_chars only takes positive integer values"
    try:
        length = int(num_bytes)
    except (TypeError, ValueError) as err:
        raise TypeError(error_message) from err

    if length < 1:
        raise ValueError(error_message)

    return secrets.token_hex(nbytes=length)
