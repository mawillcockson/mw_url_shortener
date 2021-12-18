#!/bin/sh
set -eu
SETUP='
from mw_url_shortener.utils import probably_okay_codepoint, probably_okay_codepoint2, unsafe_random_unicode_codepoints
codepoints = list(map(chr, unsafe_random_unicode_codepoints(100_000)))
'
python -m timeit -s "${SETUP}" '"".join(map(probably_okay_codepoint , codepoints)).encode("utf-8")'
python -m timeit -s "${SETUP}" '"".join(map(probably_okay_codepoint2, codepoints)).encode("utf-8")'
