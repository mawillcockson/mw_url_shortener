from typing import List
from unicodedata import category as unicode_category

from mw_url_shortener.utils import unsafe_random_unicode_codepoints


def probably_okay_codepoint(character: str) -> bool:
    # character categories from:
    # https://www.unicode.org/reports/tr44/#GC_Values_Table
    category = unicode_category(character)
    if category[0] == "C":
        return False
    if category in ["Zl", "Zp"]:
        return False
    return True


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
