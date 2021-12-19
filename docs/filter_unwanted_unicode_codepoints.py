import math
import sys
from itertools import chain
from random import random as _random
from typing import List

from unwanted_unicode_category_ranges import UNICODE_CATEGORIES as UNWANTED_CATEGORIES

UNWANTED_CODEPOINTS = set(
    chain.from_iterable(
        list(_range)
        for _range in chain.from_iterable(
            d["ranges"] for d in UNWANTED_CATEGORIES.values()
        )
    )
)


def unsafe_random_string(length: int) -> str:
    unwanted_codepoints = UNWANTED_CODEPOINTS
    LARGEST_UNICODE_CODEPOINT_PLUS_ONE = sys.maxunicode + 1
    floor = math.floor
    random = _random

    probably_okay_codepoints: "List[str]" = []
    for _ in range(length):
        codepoint = floor(LARGEST_UNICODE_CODEPOINT_PLUS_ONE * random())
        while codepoint in unwanted_codepoints:
            codepoint = floor(LARGEST_UNICODE_CODEPOINT_PLUS_ONE * random())
        probably_okay_codepoints.append(chr(codepoint))
    return "".join(probably_okay_codepoints)
