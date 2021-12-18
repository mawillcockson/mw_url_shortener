"""
module of utility functions

all of these functions can be loaded independently of the rest of this library
"""
import secrets
import string
from math import floor
from random import choices, random
from stringprep import in_table_a1 as is_unassigned_codepoint
from stringprep import in_table_b1 as is_commonly_mapped_to_nothing
from stringprep import in_table_c3 as is_private_use
from stringprep import in_table_c4 as is_non_character_codepoint
from stringprep import in_table_c5 as is_surrogate
from stringprep import in_table_c6 as is_innappropriate_for_plaintext
from stringprep import in_table_c7 as is_inappropriate_for_canonical_form
from stringprep import in_table_c8 as is_change_display_or_deprecated
from stringprep import in_table_c9 as is_tagging_character
from stringprep import in_table_c21_c22 as is_control_character
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


def probably_okay_codepoint(codepoint: int) -> bool:
    """
    returns True if the codepoint is probably okay to randomly include in a
    string
    """
    if is_unassigned_codepoint(codepoint):
        return False
    if is_commonly_mapped_to_nothing(codepoint):
        return False
    if is_private_use(codepoint):
        return False
    if is_non_character_codepoint(codepoint):
        return False
    if is_surrogate(codepoint):
        return False
    if is_innappropriate_for_plaintext(codepoint):
        return False
    if is_inappropriate_for_canonical_form(codepoint):
        return False
    if is_change_display_or_deprecated(codepoint):
        return False
    if is_tagging_character(codepoint):
        return False
    return True


def probably_okay_codepoint2(codepoint: int) -> bool:
    """
    returns True if the codepoint is probably okay to randomly include in a
    string
    """
    if unicode_category(codepoint) in {
        "Zl",
        "Zp",
        "Cc",
        "Cf",
        "Cs",
        "Co",
        "Cn",
    }:
        return False
    return True


def unsafe_random_string(length: int) -> str:
    "returns a string of `length` random unicode characters (probably)"
    # the documentation for unicodedata and stringprep libraries was useful, as
    # was this stack overflow question:
    # https://stackoverflow.com/q/1477294
    probably_okay_codepoints: List[int] = []
    while len(probably_okay_codepoints) < length:
        number_needed_characters = length - len(probably_okay_codepoints)
        codepoints = unsafe_random_unicode_codepoints(number_needed_characters)
        probably_okay_codepoints.extend(filter(probably_okay_codepoint, codepoints))
    return "".join(map(chr, probably_okay_codepoints))


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
