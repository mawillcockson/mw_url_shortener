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
from unicodedata import category as unicode_category

LARGEST_UNICODE_CODEPOINT_PLUS_ONE = LARGEST_UNICODE_CODEPOINT + 1


def unsafe_random_unicode_codepoints(length: int) -> List[int]:
    """
    returns `length` random integers in the range [0, maxunicode]

    these aren't guaranteed to be valid in the order fiven, and are likely to
    give an error like:

    UnicodeEncodeError: 'utf-8' codec can't encode character '\\uddd3' in position 1299: surrogates not allowed
    """
    return [floor(LARGEST_UNICODE_CODEPOINT_PLUS_ONE * random()) for _ in range(length)]


def probably_okay_codepoint(character: str) -> bool:
    """
    returns the codepoint if it's probably okay to randomly include in a string

    simply removing characters from U+D800 through to U+DFFF (surrogate codes)
    seems sufficient:
    https://datatracker.ietf.org/doc/html/rfc3454.html#section-5.5

    the rest make it slightly easier to display
    """
    # character categories from:
    # https://www.unicode.org/reports/tr44/#GC_Values_Table
    return unicode_category(character) not in {
        "Zl",  # U+2028 LINE SEPARATOR only
        "Zp",  # U+2029 PARAGRAPH SEPARATOR only
        "Cc",  # a C0 or C1 control code
        "Cf",  # a format control character
        "Cs",  # a surrogate code point
        "Co",  # a private-use character
        "Cn",  # a reserved unassigned code point or a noncharacter
    }


def unsafe_random_string(length: int) -> str:
    "returns a string of `length` random unicode characters (probably)"
    # the documentation for unicodedata and stringprep libraries was useful, as
    # was this stack overflow question:
    # https://stackoverflow.com/q/1477294
    probably_okay_codepoints: List[str] = []
    while len(probably_okay_codepoints) < length:
        number_needed_characters = length - len(probably_okay_codepoints)
        codepoints = unsafe_random_unicode_codepoints(number_needed_characters)
        probably_okay_codepoints.extend(
            filter(probably_okay_codepoint, map(chr, codepoints))
        )
    return "".join(probably_okay_codepoints)


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
