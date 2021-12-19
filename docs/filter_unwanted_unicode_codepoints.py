import math
import sys
from itertools import chain
from random import random as _random
from typing import List

from unwanted_unicode_category_ranges import UNICODE_CATEGORIES as UNWANTED_CATEGORIES

UNWANTED_CODEPOINT_RANGES = list(
        chain.from_iterable(
            d["ranges"] for d in UNWANTED_CATEGORIES.values()
        )
    )


def unsafe_random_string(length: int) -> str:
    unwanted_codepoint_ranges = UNWANTED_CODEPOINT_RANGES
    LARGEST_UNICODE_CODEPOINT_PLUS_ONE = sys.maxunicode + 1
    floor = math.floor
    random = _random

    probably_okay_codepoints: "List[str]" = []
    def valid_codepoint(_: int) -> str:
        codepoint = floor(LARGEST_UNICODE_CODEPOINT_PLUS_ONE * random())
        while True:
            for _range in unwanted_codepoint_ranges:
                if codepoint in _range:
                    codepoint = floor(LARGEST_UNICODE_CODEPOINT_PLUS_ONE * random())
        return chr(codepoint)

    return "".join(map(valid_codepoint, range(length)))
