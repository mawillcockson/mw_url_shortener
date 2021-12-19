from math import floor
from random import random
from sys import maxunicode as LARGEST_UNICODE_CODEPOINT
from typing import List
from unicodedata import category as unicode_category

LARGEST_UNICODE_CODEPOINT_PLUS_ONE = LARGEST_UNICODE_CODEPOINT + 1


def probably_okay_codepoint(_: int) -> str:
    # character categories from:
    # https://www.unicode.org/reports/tr44/#GC_Values_Table
    codepoint = chr(floor(LARGEST_UNICODE_CODEPOINT_PLUS_ONE * random()))
    category = unicode_category(codepoint)
    while category[0] == "C":
        codepoint = chr(floor(LARGEST_UNICODE_CODEPOINT_PLUS_ONE * random()))
        category = unicode_category(codepoint)
    return codepoint


def unsafe_random_string(length: int) -> str:
    "returns a string of `length` random unicode characters (probably)"
    # the documentation for unicodedata and stringprep libraries was useful, as
    # was this stack overflow question:
    # https://stackoverflow.com/q/1477294
    return "".join(map(probably_okay_codepoint, range(length)))
