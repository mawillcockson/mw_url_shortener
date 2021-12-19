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
    current_length = len(probably_okay_codepoints)
    while current_length < length:
        probably_okay_codepoints.extend(
            chr(codepoint)
            for codepoint in [
                floor(LARGEST_UNICODE_CODEPOINT_PLUS_ONE * random())
                for _ in range(length - current_length)
            ]
            if codepoint not in unwanted_codepoints
        )
        current_length = len(probably_okay_codepoints)
    return "".join(probably_okay_codepoints)
